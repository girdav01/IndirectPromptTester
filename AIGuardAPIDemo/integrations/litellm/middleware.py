"""
LiteLLM middleware for AI Guard integration
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_guard_client import AIGuardClient, AIGuardException
from .config import AIGuardConfig


class AIGuardMiddleware:
    """
    Middleware for LiteLLM proxy that integrates AI Guard security scanning

    This middleware can be added to LiteLLM proxy to scan all requests and responses
    for security threats using Trend Vision One AI Guard.

    Example usage in LiteLLM config:
        ```yaml
        litellm_settings:
          callbacks: ["ai_guard"]

        ai_guard:
          api_key: "your-api-key"
          check_input: true
          check_output: true
          block_on_threat: true
        ```
    """

    def __init__(self, config: AIGuardConfig):
        """
        Initialize middleware

        Args:
            config: AI Guard configuration
        """
        self.config = config
        self.client = AIGuardClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout
        )
        self.logger = logging.getLogger(__name__)
        self._cache = {} if config.cache_results else None

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()

    def _check_cache(self, text: str) -> Optional[Dict]:
        """Check if scan result is in cache"""
        if not self._cache:
            return None

        cache_key = self._get_cache_key(text)
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                return cached_result
            else:
                del self._cache[cache_key]
        return None

    def _update_cache(self, text: str, result: Dict) -> None:
        """Update cache with scan result"""
        if self._cache:
            cache_key = self._get_cache_key(text)
            self._cache[cache_key] = (result, time.time())

    def process_request(
        self,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming request and scan for threats

        Args:
            request_data: LiteLLM request data
            metadata: Request metadata (team_id, api_key, etc.)

        Returns:
            Modified request data or raises exception if blocked

        Raises:
            AIGuardException: If threats detected and blocking enabled
        """
        if not self.config.check_input:
            return request_data

        # Check if enabled for this team/key
        if metadata:
            team_id = metadata.get("team_id")
            api_key = metadata.get("api_key")

            if team_id and not self.config.is_enabled_for_team(team_id):
                return request_data
            if api_key and not self.config.is_enabled_for_key(api_key):
                return request_data

        # Extract messages from request
        messages = request_data.get("messages", [])

        for i, message in enumerate(messages):
            if isinstance(message, dict) and "content" in message:
                content = message["content"]

                # Check cache first
                cached_result = self._check_cache(content)
                if cached_result:
                    result = cached_result
                else:
                    # Scan content
                    result = self.client.scan_prompt(content)
                    self._update_cache(content, result)

                # Log if threats detected
                if not result["is_safe"] or result["risk_score"] >= self.config.risk_threshold:
                    threat_info = {
                        "message_index": i,
                        "role": message.get("role", "unknown"),
                        "threats": result["threats_detected"],
                        "risk_score": result["risk_score"]
                    }

                    if self.config.log_threats:
                        self.logger.warning(f"AI Guard detected input threat: {threat_info}")

                    # Block if configured
                    if self.config.block_on_threat:
                        raise AIGuardException(
                            f"Request blocked by AI Guard. Threats: {result['threats_detected']}"
                        )

        if self.config.log_all_requests:
            self.logger.info("AI Guard input scan completed: No threats detected")

        return request_data

    def process_response(
        self,
        response_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process LLM response and scan for threats

        Args:
            response_data: LiteLLM response data
            metadata: Request metadata

        Returns:
            Modified response data or raises exception if blocked

        Raises:
            AIGuardException: If threats detected and blocking enabled
        """
        if not self.config.check_output:
            return response_data

        # Check if enabled for this team/key
        if metadata:
            team_id = metadata.get("team_id")
            api_key = metadata.get("api_key")

            if team_id and not self.config.is_enabled_for_team(team_id):
                return response_data
            if api_key and not self.config.is_enabled_for_key(api_key):
                return response_data

        # Extract choices from response
        choices = response_data.get("choices", [])

        for i, choice in enumerate(choices):
            if isinstance(choice, dict):
                # Handle different response formats
                content = None
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                elif "text" in choice:
                    content = choice["text"]

                if content:
                    # Check cache
                    cached_result = self._check_cache(content)
                    if cached_result:
                        result = cached_result
                    else:
                        # Scan content
                        result = self.client.scan_prompt(content, detailed_response=True)
                        self._update_cache(content, result)

                    # Log if threats detected
                    if not result["is_safe"] or result["risk_score"] >= self.config.risk_threshold:
                        threat_info = {
                            "choice_index": i,
                            "threats": result["threats_detected"],
                            "risk_score": result["risk_score"]
                        }

                        if self.config.log_threats:
                            self.logger.warning(f"AI Guard detected output threat: {threat_info}")

                        # Block if configured
                        if self.config.block_on_threat:
                            # Replace with safe message
                            safe_message = "I apologize, but I cannot provide that response as it may contain sensitive or harmful content."

                            if "message" in choice:
                                choice["message"]["content"] = safe_message
                            elif "text" in choice:
                                choice["text"] = safe_message

        if self.config.log_all_requests:
            self.logger.info("AI Guard output scan completed")

        return response_data

    def get_stats(self) -> Dict[str, Any]:
        """
        Get middleware statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "cache_size": len(self._cache) if self._cache else 0,
            "config": {
                "check_input": self.config.check_input,
                "check_output": self.config.check_output,
                "block_on_threat": self.config.block_on_threat,
                "risk_threshold": self.config.risk_threshold
            }
        }
