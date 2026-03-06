"""
Tests for AgentfierConfig configuration loading and validation.
"""

import os
import pytest
from pydantic import ValidationError
from unittest.mock import patch

from agentfier.config import AgentfierConfig


class TestAgentfierConfig:
    def _make_config(self, **overrides) -> AgentfierConfig:
        """Build a config with required ANTHROPIC_API_KEY set."""
        defaults = {"anthropic_api_key": "sk-ant-test-key"}
        defaults.update(overrides)
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": defaults.pop("anthropic_api_key")}, clear=False):
            env = {k.upper(): str(v) for k, v in defaults.items()}
            with patch.dict(os.environ, env, clear=False):
                return AgentfierConfig()

    # --- Required field --------------------------------------------------

    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                AgentfierConfig()

    def test_api_key_set(self):
        cfg = self._make_config()
        assert cfg.anthropic_api_key == "sk-ant-test-key"

    # --- Defaults --------------------------------------------------------

    def test_default_model(self):
        cfg = self._make_config()
        assert cfg.claude_model == "claude-sonnet-4-5-20250929"

    def test_default_max_tokens(self):
        cfg = self._make_config()
        assert cfg.max_tokens == 4096

    def test_default_temperature(self):
        cfg = self._make_config()
        assert cfg.temperature == 0.2

    def test_default_workspace_dir(self):
        cfg = self._make_config()
        assert cfg.workspace_dir == "data/workspaces"

    def test_default_output_dir(self):
        cfg = self._make_config()
        assert cfg.output_dir == "data/outputs"

    def test_default_max_file_size(self):
        cfg = self._make_config()
        assert cfg.max_file_size_mb == 100

    def test_default_max_files(self):
        cfg = self._make_config()
        assert cfg.max_files_to_analyze == 500

    # --- Temperature validation ------------------------------------------

    def test_temperature_zero_valid(self):
        cfg = self._make_config(temperature=0.0)
        assert cfg.temperature == 0.0

    def test_temperature_one_valid(self):
        cfg = self._make_config(temperature=1.0)
        assert cfg.temperature == 1.0

    def test_temperature_too_high(self):
        with pytest.raises((ValidationError, ValueError)):
            self._make_config(temperature=1.5)

    def test_temperature_negative(self):
        with pytest.raises((ValidationError, ValueError)):
            self._make_config(temperature=-0.1)

    # --- max_tokens validation ------------------------------------------

    def test_max_tokens_positive(self):
        cfg = self._make_config(max_tokens=1024)
        assert cfg.max_tokens == 1024

    def test_max_tokens_zero_invalid(self):
        with pytest.raises((ValidationError, ValueError)):
            self._make_config(max_tokens=0)

    # --- max_file_size_mb validation ------------------------------------

    def test_max_file_size_positive(self):
        cfg = self._make_config(max_file_size_mb=50)
        assert cfg.max_file_size_mb == 50

    def test_max_file_size_zero_invalid(self):
        with pytest.raises((ValidationError, ValueError)):
            self._make_config(max_file_size_mb=0)

    # --- max_files_to_analyze validation --------------------------------

    def test_max_files_positive(self):
        cfg = self._make_config(max_files_to_analyze=100)
        assert cfg.max_files_to_analyze == 100

    def test_max_files_zero_invalid(self):
        with pytest.raises((ValidationError, ValueError)):
            self._make_config(max_files_to_analyze=0)

    # --- Convenience properties -----------------------------------------

    def test_workspace_path_property(self):
        cfg = self._make_config()
        from pathlib import Path
        assert cfg.workspace_path == Path("data/workspaces")

    def test_output_path_property(self):
        cfg = self._make_config()
        from pathlib import Path
        assert cfg.output_path == Path("data/outputs")

    def test_cfr_jar_property(self):
        cfg = self._make_config()
        from pathlib import Path
        assert cfg.cfr_jar == Path("tools/cfr.jar")

    def test_max_file_size_bytes_property(self):
        cfg = self._make_config(max_file_size_mb=10)
        assert cfg.max_file_size_bytes == 10 * 1024 * 1024

    # --- Custom values --------------------------------------------------

    def test_custom_workspace_dir(self):
        cfg = self._make_config(workspace_dir="/tmp/ws")
        assert cfg.workspace_dir == "/tmp/ws"

    def test_custom_model(self):
        cfg = self._make_config(claude_model="claude-haiku-4-5-20251001")
        assert cfg.claude_model == "claude-haiku-4-5-20251001"
