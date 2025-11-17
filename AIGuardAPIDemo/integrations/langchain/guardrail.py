"""
LangChain Guardrail implementations for AI Guard
"""

from typing import Any, Dict, List, Optional
from langchain.schema import BaseMessage
from langchain.callbacks.manager import CallbackManagerForChainRun
import sys
import os

# Add parent directory to path to import ai_guard_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_guard_client import AIGuardClient, AIGuardException


class AIGuardInputGuardrail:
    """
    Input guardrail for LangChain that validates user inputs using AI Guard

    Example:
        guardrail = AIGuardInputGuardrail(api_key="your-api-key")
        safe_input = guardrail.validate("User input here")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xdr.trendmicro.com",
        block_on_threat: bool = True,
        risk_threshold: float = 0.5
    ):
        """
        Initialize input guardrail

        Args:
            api_key: Trend Vision One API key
            base_url: API base URL
            block_on_threat: Whether to block input when threat detected
            risk_threshold: Risk score threshold (0.0 to 1.0)
        """
        self.client = AIGuardClient(api_key=api_key, base_url=base_url)
        self.block_on_threat = block_on_threat
        self.risk_threshold = risk_threshold

    def validate(self, text: str) -> str:
        """
        Validate input text

        Args:
            text: Input text to validate

        Returns:
            Original text if safe, or raises exception if unsafe

        Raises:
            AIGuardException: If input is unsafe and block_on_threat is True
        """
        result = self.client.scan_prompt(text)

        if not result["is_safe"] or result["risk_score"] >= self.risk_threshold:
            threat_info = {
                "threats": result["threats_detected"],
                "risk_score": result["risk_score"],
                "suggestions": result.get("suggestions", [])
            }

            if self.block_on_threat:
                raise AIGuardException(
                    f"Input blocked by AI Guard. Threats detected: {threat_info}"
                )
            else:
                print(f"Warning: Potential threats detected: {threat_info}")

        return text

    def validate_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Validate a list of LangChain messages

        Args:
            messages: List of LangChain messages

        Returns:
            Original messages if all are safe

        Raises:
            AIGuardException: If any message is unsafe
        """
        for message in messages:
            self.validate(message.content)

        return messages


class AIGuardOutputGuardrail:
    """
    Output guardrail for LangChain that validates LLM outputs using AI Guard

    Example:
        guardrail = AIGuardOutputGuardrail(api_key="your-api-key")
        safe_output = guardrail.validate("LLM output here")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xdr.trendmicro.com",
        block_on_threat: bool = True,
        risk_threshold: float = 0.5,
        sanitize_output: bool = False
    ):
        """
        Initialize output guardrail

        Args:
            api_key: Trend Vision One API key
            base_url: API base URL
            block_on_threat: Whether to block output when threat detected
            risk_threshold: Risk score threshold (0.0 to 1.0)
            sanitize_output: Whether to attempt sanitizing unsafe output
        """
        self.client = AIGuardClient(api_key=api_key, base_url=base_url)
        self.block_on_threat = block_on_threat
        self.risk_threshold = risk_threshold
        self.sanitize_output = sanitize_output

    def validate(self, text: str) -> str:
        """
        Validate output text

        Args:
            text: Output text to validate

        Returns:
            Original or sanitized text if safe

        Raises:
            AIGuardException: If output is unsafe and block_on_threat is True
        """
        result = self.client.scan_prompt(text, detailed_response=True)

        if not result["is_safe"] or result["risk_score"] >= self.risk_threshold:
            threat_info = {
                "threats": result["threats_detected"],
                "risk_score": result["risk_score"],
                "suggestions": result.get("suggestions", [])
            }

            if self.block_on_threat:
                if self.sanitize_output and result.get("suggestions"):
                    # Try to use AI Guard suggestions to sanitize
                    return self._sanitize_output(text, result)
                else:
                    raise AIGuardException(
                        f"Output blocked by AI Guard. Threats detected: {threat_info}"
                    )
            else:
                print(f"Warning: Potential threats in output: {threat_info}")

        return text

    def _sanitize_output(self, text: str, scan_result: Dict) -> str:
        """
        Attempt to sanitize unsafe output based on AI Guard suggestions

        Args:
            text: Original text
            scan_result: AI Guard scan result

        Returns:
            Sanitized text or generic safe message
        """
        # If AI Guard provides sanitized version, use it
        if "sanitized" in scan_result.get("raw_response", {}):
            return scan_result["raw_response"]["sanitized"]

        # Otherwise return generic safe message
        return "I apologize, but I cannot provide that information as it may contain sensitive or harmful content."


class AIGuardTransform:
    """
    Transform function that can be used in LangChain LCEL chains

    Example:
        from langchain.schema.runnable import RunnableLambda

        transform = AIGuardTransform(api_key="your-api-key")
        chain = RunnableLambda(transform.input_guard) | llm | RunnableLambda(transform.output_guard)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xdr.trendmicro.com",
        risk_threshold: float = 0.5
    ):
        self.input_guardrail = AIGuardInputGuardrail(
            api_key=api_key,
            base_url=base_url,
            risk_threshold=risk_threshold
        )
        self.output_guardrail = AIGuardOutputGuardrail(
            api_key=api_key,
            base_url=base_url,
            risk_threshold=risk_threshold
        )

    def input_guard(self, text: str) -> str:
        """Guard input"""
        return self.input_guardrail.validate(text)

    def output_guard(self, text: str) -> str:
        """Guard output"""
        return self.output_guardrail.validate(text)
