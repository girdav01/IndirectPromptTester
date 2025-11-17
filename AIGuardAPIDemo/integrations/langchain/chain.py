"""
LangChain Chain wrapper with AI Guard protection
"""

from typing import Any, Dict, List, Optional
from langchain.chains.base import Chain
from langchain.callbacks.manager import CallbackManagerForChainRun
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_guard_client import AIGuardClient, AIGuardException


class AIGuardChain(Chain):
    """
    Wrapper chain that adds AI Guard protection to any LangChain chain

    Example:
        from langchain.llms import OpenAI
        from langchain.chains import LLMChain

        base_chain = LLMChain(llm=OpenAI(), prompt=prompt)
        protected_chain = AIGuardChain(
            chain=base_chain,
            ai_guard_api_key="your-api-key"
        )
    """

    chain: Chain
    ai_guard_api_key: str
    ai_guard_base_url: str = "https://api.xdr.trendmicro.com"
    check_input: bool = True
    check_output: bool = True
    block_on_threat: bool = True
    risk_threshold: float = 0.5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = AIGuardClient(
            api_key=self.ai_guard_api_key,
            base_url=self.ai_guard_base_url
        )

    @property
    def input_keys(self) -> List[str]:
        """Input keys from wrapped chain"""
        return self.chain.input_keys

    @property
    def output_keys(self) -> List[str]:
        """Output keys from wrapped chain"""
        return self.chain.output_keys

    def _validate_input(self, text: str) -> None:
        """
        Validate input using AI Guard

        Args:
            text: Input text to validate

        Raises:
            AIGuardException: If input is unsafe
        """
        result = self.client.scan_prompt(text)

        if not result["is_safe"] or result["risk_score"] >= self.risk_threshold:
            if self.block_on_threat:
                raise AIGuardException(
                    f"Input blocked by AI Guard. "
                    f"Threats: {result['threats_detected']}, "
                    f"Risk score: {result['risk_score']}"
                )

    def _validate_output(self, text: str) -> None:
        """
        Validate output using AI Guard

        Args:
            text: Output text to validate

        Raises:
            AIGuardException: If output is unsafe
        """
        result = self.client.scan_prompt(text, detailed_response=True)

        if not result["is_safe"] or result["risk_score"] >= self.risk_threshold:
            if self.block_on_threat:
                raise AIGuardException(
                    f"Output blocked by AI Guard. "
                    f"Threats: {result['threats_detected']}, "
                    f"Risk score: {result['risk_score']}"
                )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, Any]:
        """
        Execute chain with AI Guard protection

        Args:
            inputs: Chain inputs
            run_manager: Callback manager

        Returns:
            Chain outputs

        Raises:
            AIGuardException: If input or output is unsafe
        """
        # Validate inputs if enabled
        if self.check_input:
            for key, value in inputs.items():
                if isinstance(value, str):
                    self._validate_input(value)

        # Execute wrapped chain
        outputs = self.chain(inputs, return_only_outputs=True)

        # Validate outputs if enabled
        if self.check_output:
            for key, value in outputs.items():
                if isinstance(value, str):
                    self._validate_output(value)

        return outputs

    @property
    def _chain_type(self) -> str:
        """Return chain type"""
        return "ai_guard_chain"
