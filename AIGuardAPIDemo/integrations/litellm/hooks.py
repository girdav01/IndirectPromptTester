"""
LiteLLM hooks for AI Guard integration

These hooks can be used directly with LiteLLM's callback system.
"""

import logging
from typing import Dict, Any, Optional
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_guard_client import AIGuardClient, AIGuardException

# Global client instance
_ai_guard_client: Optional[AIGuardClient] = None
logger = logging.getLogger(__name__)


def initialize_ai_guard(
    api_key: str,
    base_url: str = "https://api.xdr.trendmicro.com"
) -> None:
    """
    Initialize AI Guard client for hooks

    Args:
        api_key: Trend Vision One API key
        base_url: API base URL
    """
    global _ai_guard_client
    _ai_guard_client = AIGuardClient(api_key=api_key, base_url=base_url)
    logger.info("AI Guard initialized for LiteLLM hooks")


def ai_guard_pre_call_hook(
    model: str,
    messages: list,
    kwargs: Dict[str, Any]
) -> None:
    """
    Pre-call hook for LiteLLM to scan inputs

    This function is called before the LLM is invoked.

    Example usage:
        import litellm
        from integrations.litellm import ai_guard_pre_call_hook, initialize_ai_guard

        initialize_ai_guard(api_key="your-api-key")
        litellm.pre_call_hooks = [ai_guard_pre_call_hook]

    Args:
        model: Model name
        messages: List of messages
        kwargs: Additional arguments

    Raises:
        AIGuardException: If threats detected in input
    """
    if not _ai_guard_client:
        logger.warning("AI Guard not initialized, skipping input scan")
        return

    try:
        for message in messages:
            if isinstance(message, dict) and "content" in message:
                content = message["content"]
                result = _ai_guard_client.scan_prompt(content)

                if not result["is_safe"]:
                    logger.warning(
                        f"AI Guard detected threats in input: {result['threats_detected']}"
                    )
                    raise AIGuardException(
                        f"Input blocked by AI Guard: {result['threats_detected']}"
                    )

        logger.debug("AI Guard input scan: No threats detected")

    except AIGuardException:
        raise
    except Exception as e:
        logger.error(f"AI Guard input scan failed: {str(e)}")
        # Don't block on scanning errors unless configured otherwise
        pass


def ai_guard_post_call_hook(
    model: str,
    messages: list,
    response: Any,
    kwargs: Dict[str, Any]
) -> Any:
    """
    Post-call hook for LiteLLM to scan outputs

    This function is called after the LLM returns a response.

    Example usage:
        import litellm
        from integrations.litellm import ai_guard_post_call_hook, initialize_ai_guard

        initialize_ai_guard(api_key="your-api-key")
        litellm.post_call_hooks = [ai_guard_post_call_hook]

    Args:
        model: Model name
        messages: List of input messages
        response: LLM response
        kwargs: Additional arguments

    Returns:
        Modified response or original if safe

    Raises:
        AIGuardException: If threats detected in output
    """
    if not _ai_guard_client:
        logger.warning("AI Guard not initialized, skipping output scan")
        return response

    try:
        # Extract content from response
        if hasattr(response, "choices"):
            for choice in response.choices:
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    content = choice.message.content
                    result = _ai_guard_client.scan_prompt(content, detailed_response=True)

                    if not result["is_safe"]:
                        logger.warning(
                            f"AI Guard detected threats in output: {result['threats_detected']}"
                        )

                        # Replace with safe message
                        choice.message.content = (
                            "I apologize, but I cannot provide that response as it may "
                            "contain sensitive or harmful content."
                        )

        logger.debug("AI Guard output scan completed")
        return response

    except Exception as e:
        logger.error(f"AI Guard output scan failed: {str(e)}")
        # Return original response on scanning errors
        return response


def ai_guard_success_callback(
    kwargs: Dict[str, Any],
    completion_response: Any,
    start_time: float,
    end_time: float
) -> None:
    """
    Success callback for LiteLLM logging

    This logs successful requests that passed AI Guard checks.

    Args:
        kwargs: Request arguments
        completion_response: Response object
        start_time: Request start time
        end_time: Request end time
    """
    logger.info(
        f"Request completed successfully with AI Guard protection. "
        f"Duration: {end_time - start_time:.2f}s"
    )


def ai_guard_failure_callback(
    kwargs: Dict[str, Any],
    completion_response: Any,
    start_time: float,
    end_time: float
) -> None:
    """
    Failure callback for LiteLLM logging

    This logs failed requests (blocked by AI Guard or other errors).

    Args:
        kwargs: Request arguments
        completion_response: Response object or exception
        start_time: Request start time
        end_time: Request end time
    """
    logger.error(
        f"Request failed or blocked by AI Guard. "
        f"Duration: {end_time - start_time:.2f}s"
    )
