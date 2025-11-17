"""
LangChain Callback Handler for AI Guard monitoring
"""

from typing import Any, Dict, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_guard_client import AIGuardClient


class AIGuardCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that monitors LangChain operations and scans
    inputs/outputs using AI Guard

    Example:
        handler = AIGuardCallbackHandler(api_key="your-api-key")
        llm = ChatOpenAI(callbacks=[handler])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xdr.trendmicro.com",
        log_all: bool = True,
        alert_on_threat: bool = True
    ):
        """
        Initialize callback handler

        Args:
            api_key: Trend Vision One API key
            base_url: API base URL
            log_all: Whether to log all scans
            alert_on_threat: Whether to log alerts when threats detected
        """
        super().__init__()
        self.client = AIGuardClient(api_key=api_key, base_url=base_url)
        self.log_all = log_all
        self.alert_on_threat = alert_on_threat
        self.logger = logging.getLogger(__name__)
        self.scan_results = []

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Called when LLM starts running"""
        for prompt in prompts:
            result = self.client.scan_prompt(prompt)
            self.scan_results.append({
                "type": "input",
                "content": prompt[:100] + "...",  # Truncate for logging
                "result": result
            })

            if not result["is_safe"] and self.alert_on_threat:
                self.logger.warning(
                    f"AI Guard detected threats in input: {result['threats_detected']}"
                )

    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any
    ) -> None:
        """Called when LLM finishes running"""
        for generation in response.generations:
            for gen in generation:
                text = gen.text
                result = self.client.scan_prompt(text)
                self.scan_results.append({
                    "type": "output",
                    "content": text[:100] + "...",
                    "result": result
                })

                if not result["is_safe"] and self.alert_on_threat:
                    self.logger.warning(
                        f"AI Guard detected threats in output: {result['threats_detected']}"
                    )

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain starts running"""
        if self.log_all:
            self.logger.info("Chain started with AI Guard monitoring")

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain finishes running"""
        if self.log_all:
            safe_count = sum(1 for r in self.scan_results if r["result"]["is_safe"])
            total_count = len(self.scan_results)
            self.logger.info(
                f"Chain completed. AI Guard scans: {safe_count}/{total_count} safe"
            )

    def get_scan_summary(self) -> Dict[str, Any]:
        """
        Get summary of all scans performed

        Returns:
            Dictionary with scan statistics
        """
        total = len(self.scan_results)
        safe = sum(1 for r in self.scan_results if r["result"]["is_safe"])
        threats_by_type = {}

        for scan in self.scan_results:
            for threat in scan["result"]["threats_detected"]:
                threats_by_type[threat] = threats_by_type.get(threat, 0) + 1

        return {
            "total_scans": total,
            "safe_scans": safe,
            "unsafe_scans": total - safe,
            "threats_by_type": threats_by_type,
            "average_risk_score": sum(r["result"]["risk_score"] for r in self.scan_results) / total if total > 0 else 0
        }

    def clear_results(self) -> None:
        """Clear scan results"""
        self.scan_results = []
