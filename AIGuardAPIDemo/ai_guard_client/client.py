"""
Trend Vision One AI Guard API Client
"""

import requests
import logging
from typing import Dict, Optional, List
from enum import Enum
from .exceptions import (
    AIGuardException,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    APIError
)


class SecurityLevel(Enum):
    """AI Guard security levels"""
    CAUTIOUS = "cautious"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class ThreatType(Enum):
    """Types of threats AI Guard can detect"""
    HARMFUL_CONTENT = "harmful_content"
    SENSITIVE_INFO = "sensitive_info"
    PROMPT_INJECTION = "prompt_injection"


class AIGuardClient:
    """
    Client for interacting with Trend Vision One AI Guard API

    Example:
        client = AIGuardClient(
            api_key="your-api-key",
            base_url="https://api.xdr.trendmicro.com"
        )
        result = client.scan_prompt("User input text here")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xdr.trendmicro.com",
        region: str = "us",
        timeout: int = 30,
        security_level: SecurityLevel = SecurityLevel.MODERATE
    ):
        """
        Initialize AI Guard client

        Args:
            api_key: Trend Vision One API key
            base_url: Base URL for API endpoint
            region: API region (us, eu, ap, etc.)
            timeout: Request timeout in seconds
            security_level: Default security level for scans
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.region = region
        self.timeout = timeout
        self.security_level = security_level
        self.logger = logging.getLogger(__name__)

        # API endpoint
        self.guard_endpoint = f"{self.base_url}/beta/aiSecurity/guard"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AIGuard-Python-Client/1.0.0"
        }

    def scan_prompt(
        self,
        text: str,
        detailed_response: bool = False,
        check_types: Optional[List[ThreatType]] = None
    ) -> Dict:
        """
        Scan a prompt or response for security threats

        Args:
            text: The prompt or response text to scan
            detailed_response: Whether to return detailed threat information
            check_types: List of specific threat types to check for

        Returns:
            Dictionary containing scan results

        Raises:
            ValidationError: If input is invalid
            APIError: If API request fails
        """
        if not text or not isinstance(text, str):
            raise ValidationError("Text must be a non-empty string")

        if len(text) > 100000:  # 100KB limit
            raise ValidationError("Text exceeds maximum length of 100KB")

        payload = {
            "guard": text
        }

        # Add configuration if needed
        if check_types:
            payload["checkTypes"] = [t.value for t in check_types]

        params = {"detailedResponse": str(detailed_response).lower()}

        try:
            self.logger.debug(f"Scanning text of length {len(text)}")
            response = requests.post(
                self.guard_endpoint,
                json=payload,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )

            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")

            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")

            # Handle other errors
            if response.status_code != 200:
                raise APIError(
                    f"API request failed: {response.text}",
                    status_code=response.status_code,
                    response=response
                )

            result = response.json()
            self.logger.debug(f"Scan completed: {result}")

            return self._parse_response(result)

        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def _parse_response(self, response: Dict) -> Dict:
        """
        Parse and normalize API response

        Args:
            response: Raw API response

        Returns:
            Normalized response dictionary
        """
        # Default structure
        result = {
            "is_safe": True,
            "threats_detected": [],
            "risk_score": 0.0,
            "suggestions": []
        }

        # Parse based on API response format
        # Note: Adjust this based on actual API response structure
        if "threats" in response:
            result["threats_detected"] = response["threats"]
            result["is_safe"] = len(response["threats"]) == 0

        if "riskScore" in response:
            result["risk_score"] = response["riskScore"]
            result["is_safe"] = response["riskScore"] < 0.5

        if "blocked" in response:
            result["is_safe"] = not response["blocked"]

        if "suggestions" in response:
            result["suggestions"] = response["suggestions"]

        # Add raw response for detailed analysis
        result["raw_response"] = response

        return result

    def scan_conversation(
        self,
        messages: List[Dict[str, str]],
        detailed_response: bool = False
    ) -> List[Dict]:
        """
        Scan multiple messages in a conversation

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            detailed_response: Whether to return detailed threat information

        Returns:
            List of scan results for each message
        """
        results = []

        for message in messages:
            if "content" not in message:
                raise ValidationError("Each message must have 'content' field")

            result = self.scan_prompt(
                text=message["content"],
                detailed_response=detailed_response
            )
            result["role"] = message.get("role", "unknown")
            results.append(result)

        return results

    def is_safe(self, text: str, threshold: float = 0.5) -> bool:
        """
        Quick check if text is safe

        Args:
            text: Text to check
            threshold: Risk score threshold (0.0 to 1.0)

        Returns:
            True if text is safe, False otherwise
        """
        result = self.scan_prompt(text)
        return result["is_safe"] and result["risk_score"] < threshold

    def batch_scan(
        self,
        texts: List[str],
        detailed_response: bool = False
    ) -> List[Dict]:
        """
        Scan multiple texts in batch

        Args:
            texts: List of texts to scan
            detailed_response: Whether to return detailed threat information

        Returns:
            List of scan results
        """
        results = []

        for text in texts:
            try:
                result = self.scan_prompt(text, detailed_response)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to scan text: {str(e)}")
                results.append({
                    "is_safe": False,
                    "error": str(e),
                    "threats_detected": ["scan_failed"]
                })

        return results
