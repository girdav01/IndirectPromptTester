"""
Configuration for LiteLLM AI Guard integration
"""

from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class AIGuardConfig:
    """
    Configuration for AI Guard in LiteLLM

    Example:
        config = AIGuardConfig(
            api_key="your-api-key",
            check_input=True,
            check_output=True
        )
    """

    # API Configuration
    api_key: str
    base_url: str = "https://api.xdr.trendmicro.com"
    timeout: int = 30

    # Guard Configuration
    check_input: bool = True
    check_output: bool = True
    block_on_threat: bool = True
    risk_threshold: float = 0.5

    # Logging Configuration
    log_threats: bool = True
    log_all_requests: bool = False

    # Performance Configuration
    async_scanning: bool = False
    cache_results: bool = True
    cache_ttl: int = 300  # seconds

    # Team/Key specific settings
    enabled_for_teams: Optional[List[str]] = None
    enabled_for_keys: Optional[List[str]] = None

    def is_enabled_for_team(self, team_id: str) -> bool:
        """Check if AI Guard is enabled for a specific team"""
        if self.enabled_for_teams is None:
            return True
        return team_id in self.enabled_for_teams

    def is_enabled_for_key(self, api_key: str) -> bool:
        """Check if AI Guard is enabled for a specific API key"""
        if self.enabled_for_keys is None:
            return True
        return api_key in self.enabled_for_keys
