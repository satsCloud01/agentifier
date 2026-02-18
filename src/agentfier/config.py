"""
Agentfier configuration module.

Loads configuration from environment variables and .env files using pydantic-settings.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentfierConfig(BaseSettings):
    """Main configuration for the Agentfier application.

    Settings are loaded in order of priority:
    1. Environment variables
    2. .env file in the project root
    3. Default values defined below
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Anthropic / Claude settings ---
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key (required).",
    )
    claude_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Claude model identifier to use for analysis.",
    )
    max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum number of tokens for Claude responses.",
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for Claude (0.0 – 1.0).",
    )

    # --- Tool paths ---
    cfr_jar_path: str = Field(
        default="tools/cfr.jar",
        description="Path to the CFR decompiler JAR file.",
    )

    # --- Directory settings ---
    workspace_dir: str = Field(
        default="data/workspaces",
        description="Directory for temporary workspaces during ingestion.",
    )
    output_dir: str = Field(
        default="data/outputs",
        description="Directory where analysis outputs are written.",
    )

    # --- Processing limits ---
    max_file_size_mb: int = Field(
        default=100,
        gt=0,
        description="Maximum size (in MB) of a single file to process.",
    )
    max_files_to_analyze: int = Field(
        default=500,
        gt=0,
        description="Maximum number of files to include in analysis.",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"temperature must be between 0.0 and 1.0, got {value}")
        return value

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(f"max_tokens must be a positive integer, got {value}")
        return value

    @field_validator("max_file_size_mb")
    @classmethod
    def validate_max_file_size_mb(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(f"max_file_size_mb must be a positive integer, got {value}")
        return value

    @field_validator("max_files_to_analyze")
    @classmethod
    def validate_max_files_to_analyze(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(
                f"max_files_to_analyze must be a positive integer, got {value}"
            )
        return value

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def workspace_path(self) -> Path:
        """Return *workspace_dir* as a ``pathlib.Path``."""
        return Path(self.workspace_dir)

    @property
    def output_path(self) -> Path:
        """Return *output_dir* as a ``pathlib.Path``."""
        return Path(self.output_dir)

    @property
    def cfr_jar(self) -> Path:
        """Return *cfr_jar_path* as a ``pathlib.Path``."""
        return Path(self.cfr_jar_path)

    @property
    def max_file_size_bytes(self) -> int:
        """Return *max_file_size_mb* converted to bytes."""
        return self.max_file_size_mb * 1024 * 1024


# ---------------------------------------------------------------------------
# Module-level singleton (lazy)
# ---------------------------------------------------------------------------

_config: Optional[AgentfierConfig] = None


def get_config() -> AgentfierConfig:
    """Return (and cache) the global ``AgentfierConfig`` instance.

    The configuration is created on first access so that import-time side
    effects are avoided.
    """
    global _config
    if _config is None:
        _config = AgentfierConfig()  # type: ignore[call-arg]
    return _config
