"""
Configuration analyzer.

Detects environment variable usage, config file formats, feature flag
systems, multi-environment strategies, and secrets management approaches.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import ConfigurationResult

logger = logging.getLogger(__name__)


class ConfigurationAnalyzer(BaseAnalyzer):
    """Dimension 12 -- Configuration."""

    DIMENSION = "configuration"

    PATTERNS: list[str] = [
        # .env files
        "**/.env*",
        "**/*.env",
        # Config directories
        "**/config/**/*.py",
        "**/config/**/*.ts",
        "**/config/**/*.yaml",
        "**/config/**/*.json",
        # Settings modules
        "**/settings*.py",
        "**/settings*.ts",
        # Java / Spring properties
        "**/application*.yml",
        "**/application*.yaml",
        "**/application*.properties",
        # .NET config
        "**/appsettings*.json",
        # Feature flags
        "**/*feature*flag*",
        "**/*toggle*",
        # Service discovery / secrets
        "**/consul*",
        "**/vault*",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return ConfigurationResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "env_file_count": 0,
            "env_vars_detected": 0,
            "config_formats": [],
            "feature_flag_library": "",
            "multi_env_patterns": [],
            "secrets_management": "",
            "dynamic_config_detected": False,
        }

        config_formats: set[str] = set()
        env_names: set[str] = set()

        feature_flag_patterns = {
            "LaunchDarkly": re.compile(r"launchdarkly|ldclient|ld_client", re.IGNORECASE),
            "Unleash": re.compile(r"unleash", re.IGNORECASE),
            "Flagsmith": re.compile(r"flagsmith", re.IGNORECASE),
            "Split": re.compile(r"split\.io|splitio", re.IGNORECASE),
            "Flipper": re.compile(r"\bFlipper\b"),
            "django-waffle": re.compile(r"waffle", re.IGNORECASE),
        }

        secrets_patterns = {
            "HashiCorp Vault": re.compile(r"vault|hvac", re.IGNORECASE),
            "AWS Secrets Manager": re.compile(r"secretsmanager|aws.*secrets", re.IGNORECASE),
            "AWS SSM Parameter Store": re.compile(r"ssm.*parameter|parameter.?store", re.IGNORECASE),
            "dotenv": re.compile(r"dotenv|load_dotenv|from_env", re.IGNORECASE),
            "Azure Key Vault": re.compile(r"azure.*keyvault|key.?vault", re.IGNORECASE),
            "Google Secret Manager": re.compile(r"google.*secret.?manager|secretmanager", re.IGNORECASE),
        }

        dynamic_config_patterns = [
            re.compile(r"consul", re.IGNORECASE),
            re.compile(r"etcd", re.IGNORECASE),
            re.compile(r"zookeeper", re.IGNORECASE),
            re.compile(r"Spring Cloud Config", re.IGNORECASE),
            re.compile(r"@RefreshScope", re.IGNORECASE),
        ]

        env_var_pattern = re.compile(
            r"""(?:os\.environ|os\.getenv|process\.env|ENV\[|getenv\(|"""
            r"""System\.getenv|@Value\(\"\$\{)""",
            re.IGNORECASE,
        )

        for f in files:
            name = f.name.lower()
            ext = f.suffix.lower()

            # Detect .env files
            if name.startswith(".env") or name.endswith(".env"):
                findings["env_file_count"] += 1

            # Detect config formats
            if ext in (".yaml", ".yml"):
                config_formats.add("YAML")
            elif ext == ".json":
                config_formats.add("JSON")
            elif ext == ".toml":
                config_formats.add("TOML")
            elif ext == ".properties":
                config_formats.add("Properties")
            elif ext == ".ini" or ext == ".cfg":
                config_formats.add("INI")
            elif name.startswith(".env") or name.endswith(".env"):
                config_formats.add("env")

            # Multi-environment pattern detection from filenames
            for env_name in ("dev", "development", "staging", "production", "prod", "test", "qa", "uat", "local"):
                if env_name in name:
                    env_names.add(env_name)

            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            # Count env var usages
            findings["env_vars_detected"] += len(env_var_pattern.findall(content))

            # Feature flag detection
            for lib_name, pat in feature_flag_patterns.items():
                if pat.search(content) and not findings["feature_flag_library"]:
                    findings["feature_flag_library"] = lib_name

            # Secrets management
            for mgr_name, pat in secrets_patterns.items():
                if pat.search(content) and not findings["secrets_management"]:
                    findings["secrets_management"] = mgr_name

            # Dynamic config detection
            for pat in dynamic_config_patterns:
                if pat.search(content):
                    findings["dynamic_config_detected"] = True
                    break

        findings["config_formats"] = sorted(config_formats)
        findings["multi_env_patterns"] = sorted(env_names)

        return findings
