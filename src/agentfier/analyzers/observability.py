"""
Observability analyzer -- Dimension 6.

Inspects logging configurations, metrics endpoints, tracing setup, and
health-check files to map the observability stack.
"""

import re
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import ObservabilityResult

LOGGING_FRAMEWORKS: dict[str, list[str]] = {
    "logback": [r"logback", r"ch\.qos\.logback"],
    "log4j": [r"log4j", r"org\.apache\.logging"],
    "python_logging": [r"import logging", r"logging\.getLogger"],
    "winston": [r"winston"],
    "pino": [r"pino"],
    "bunyan": [r"bunyan"],
    "structlog": [r"structlog"],
    "serilog": [r"Serilog"],
    "slf4j": [r"org\.slf4j"],
}

METRICS_TOOLS: dict[str, list[str]] = {
    "prometheus": [r"prometheus", r"micrometer", r"prom-client"],
    "datadog": [r"datadog", r"ddtrace", r"dd-trace"],
    "new_relic": [r"newrelic", r"new_relic"],
    "grafana": [r"grafana"],
    "statsd": [r"statsd", r"StatsD"],
}

TRACING_TOOLS: dict[str, list[str]] = {
    "opentelemetry": [r"opentelemetry", r"otel"],
    "jaeger": [r"jaeger"],
    "zipkin": [r"zipkin"],
    "xray": [r"aws.xray", r"X-Ray"],
}


class ObservabilityAnalyzer(BaseAnalyzer):
    DIMENSION = "observability"
    PATTERNS = [
        "**/logback*.xml",
        "**/log4j*.xml",
        "**/log4j*.properties",
        "**/logging*.py",
        "**/logging*.conf",
        "**/logging*.yaml",
        "**/*metrics*.py",
        "**/*metrics*.java",
        "**/*metrics*.ts",
        "**/*tracing*.py",
        "**/*tracing*.java",
        "**/*tracing*.ts",
        "**/*health*.py",
        "**/*health*.java",
        "**/*health*.ts",
        "**/*monitor*.py",
        "**/*monitor*.java",
        "**/application*.yml",
        "**/application*.properties",
        "**/docker-compose*.yml",
        "**/requirements.txt",
        "**/package.json",
        "**/pom.xml",
    ]

    def _get_result_model(self) -> type[ObservabilityResult]:
        return ObservabilityResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        logging_found: set[str] = set()
        metrics_found: set[str] = set()
        tracing_found: set[str] = set()
        error_tracking: set[str] = set()
        has_health = False

        for f in files:
            try:
                content = f.read_text(errors="replace")

                for fw, patterns in LOGGING_FRAMEWORKS.items():
                    for pat in patterns:
                        if re.search(pat, content):
                            logging_found.add(fw)
                            break

                for tool, patterns in METRICS_TOOLS.items():
                    for pat in patterns:
                        if re.search(pat, content, re.IGNORECASE):
                            metrics_found.add(tool)
                            break

                for tool, patterns in TRACING_TOOLS.items():
                    for pat in patterns:
                        if re.search(pat, content, re.IGNORECASE):
                            tracing_found.add(tool)
                            break

                if any(
                    kw in content.lower()
                    for kw in ["sentry", "rollbar", "bugsnag", "airbrake"]
                ):
                    for et in ["sentry", "rollbar", "bugsnag", "airbrake"]:
                        if et in content.lower():
                            error_tracking.add(et)

                if "health" in f.name.lower():
                    has_health = True
            except Exception:
                pass

        return {
            "logging_frameworks": list(logging_found),
            "metrics_tools": list(metrics_found),
            "tracing_tools": list(tracing_found),
            "error_tracking": list(error_tracking),
            "has_health_checks": has_health,
        }
