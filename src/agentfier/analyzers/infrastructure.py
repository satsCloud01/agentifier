"""
Infrastructure analyzer.

Detects containerisation, orchestration, CI/CD pipelines, Infrastructure as
Code tools, environment configurations, and scaling strategies.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import InfrastructureResult

logger = logging.getLogger(__name__)


class InfrastructureAnalyzer(BaseAnalyzer):
    """Dimension 9 -- Infrastructure."""

    DIMENSION = "infrastructure"

    PATTERNS: list[str] = [
        # Docker
        "**/Dockerfile*",
        "**/docker-compose*.yml",
        "**/docker-compose*.yaml",
        "**/.dockerignore",
        # Terraform
        "**/terraform/**/*.tf",
        "**/terraform/**/*.tfvars",
        # Kubernetes
        "**/k8s/**/*.yaml",
        "**/k8s/**/*.yml",
        "**/kubernetes/**/*.yaml",
        # Helm
        "**/helm/**/*",
        "**/charts/**/*",
        # CI/CD
        "**/.github/workflows/*.yml",
        "**/.github/workflows/*.yaml",
        "**/Jenkinsfile*",
        "**/.circleci/**/*",
        "**/cloudbuild*.yaml",
        # Serverless / PaaS
        "**/serverless*.yml",
        "**/sam-template*.yaml",
        "**/Procfile",
        "**/app.yaml",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return InfrastructureResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "docker_found": False,
            "docker_compose_found": False,
            "kubernetes_found": False,
            "helm_found": False,
            "terraform_found": False,
            "ci_cd_platform": [],
            "iac_tools": [],
            "cloud_providers": [],
            "serverless_found": False,
            "environments_detected": [],
        }

        cloud_patterns = {
            "AWS": re.compile(r"aws|amazon|ecr|ecs|eks|s3|lambda", re.IGNORECASE),
            "GCP": re.compile(r"gcloud|google.cloud|gcr\.io|gke|cloudbuild", re.IGNORECASE),
            "Azure": re.compile(r"azure|azurecr|aks|az\s", re.IGNORECASE),
        }

        ci_cd_platforms: set[str] = set()
        iac_tools: set[str] = set()
        cloud_providers: set[str] = set()
        environments: set[str] = set()

        for f in files:
            name = f.name.lower()
            rel = str(f.relative_to(self.workspace)).lower()

            # Docker
            if name.startswith("dockerfile"):
                findings["docker_found"] = True
            if "docker-compose" in name:
                findings["docker_compose_found"] = True

            # Kubernetes
            if "k8s/" in rel or "kubernetes/" in rel:
                findings["kubernetes_found"] = True
            if "helm/" in rel or "charts/" in rel:
                findings["helm_found"] = True

            # Terraform
            if name.endswith(".tf") or name.endswith(".tfvars"):
                findings["terraform_found"] = True
                iac_tools.add("Terraform")

            # CI/CD platforms
            if ".github/workflows" in rel:
                ci_cd_platforms.add("GitHub Actions")
            if "jenkinsfile" in name:
                ci_cd_platforms.add("Jenkins")
            if ".circleci" in rel:
                ci_cd_platforms.add("CircleCI")
            if "cloudbuild" in name:
                ci_cd_platforms.add("Google Cloud Build")

            # Serverless
            if "serverless" in name:
                findings["serverless_found"] = True
                iac_tools.add("Serverless Framework")
            if "sam-template" in name:
                findings["serverless_found"] = True
                iac_tools.add("AWS SAM")

            # Read file contents for deeper inspection
            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            # Cloud provider detection
            for provider, pat in cloud_patterns.items():
                if pat.search(content):
                    cloud_providers.add(provider)

            # Environment detection from filenames / content
            for env_name in ("dev", "staging", "production", "prod", "test", "qa", "uat"):
                if env_name in name or env_name in rel:
                    environments.add(env_name)

        if findings["terraform_found"]:
            iac_tools.add("Terraform")
        if findings["docker_found"]:
            iac_tools.add("Docker")

        findings["ci_cd_platform"] = sorted(ci_cd_platforms)
        findings["iac_tools"] = sorted(iac_tools)
        findings["cloud_providers"] = sorted(cloud_providers)
        findings["environments_detected"] = sorted(environments)

        return findings
