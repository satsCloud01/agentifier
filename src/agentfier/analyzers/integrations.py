"""
Integration analyzer -- Dimension 4.

Scans service clients, API wrappers, and dependency files to discover
external APIs, webhooks, and third-party service integrations.
"""

import re
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import IntegrationResult

HTTP_CLIENT_PATTERNS = [
    r"requests\.(get|post|put|delete|patch)",
    r"httpx\.",
    r"RestTemplate",
    r"WebClient",
    r"HttpClient",
    r"fetch\(",
    r"axios\.",
    r"urllib",
]

THIRD_PARTY_SDKS: dict[str, str] = {
    "stripe": "Payment",
    "twilio": "SMS/Communication",
    "sendgrid": "Email",
    "mailgun": "Email",
    "aws-sdk": "Cloud (AWS)",
    "boto3": "Cloud (AWS)",
    "google-cloud": "Cloud (GCP)",
    "azure": "Cloud (Azure)",
    "slack": "Communication",
    "firebase": "Backend Services",
    "sentry": "Error Tracking",
    "datadog": "Monitoring",
}


class IntegrationAnalyzer(BaseAnalyzer):
    DIMENSION = "integrations"
    PATTERNS = [
        "**/*client*.py",
        "**/*client*.java",
        "**/*client*.ts",
        "**/*service*.py",
        "**/*service*.java",
        "**/*service*.ts",
        "**/*api*.py",
        "**/*api*.java",
        "**/*api*.ts",
        "**/*webhook*.py",
        "**/*webhook*.java",
        "**/*webhook*.ts",
        "**/*integration*.py",
        "**/*integration*.java",
        "**/*connector*.py",
        "**/*connector*.java",
        "**/requirements.txt",
        "**/package.json",
        "**/pom.xml",
    ]

    def _get_result_model(self) -> type[IntegrationResult]:
        return IntegrationResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        http_clients_found: set[str] = set()
        third_party: dict[str, str] = {}
        webhook_files: list[str] = []

        for f in files:
            try:
                content = f.read_text(errors="replace")
                content_lower = content.lower()

                for pattern in HTTP_CLIENT_PATTERNS:
                    if re.search(pattern, content):
                        http_clients_found.add(
                            pattern.split(r"\.")[0].split(r"\(")[0]
                        )

                for sdk, category in THIRD_PARTY_SDKS.items():
                    if sdk in content_lower:
                        third_party[sdk] = category

                if "webhook" in f.name.lower():
                    webhook_files.append(str(f.relative_to(self.workspace)))
            except Exception:
                pass

        return {
            "http_clients": list(http_clients_found),
            "third_party_services": third_party,
            "webhook_files": webhook_files,
        }
