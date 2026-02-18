"""
API Architecture analyzer.

Detects API endpoints, style (REST / GraphQL / gRPC), rate-limiting
configuration, versioning strategy, and documentation format by scanning
controllers, routes, handlers, and OpenAPI / Swagger specifications.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import ApiArchitectureResult

logger = logging.getLogger(__name__)


class ApiArchitectureAnalyzer(BaseAnalyzer):
    """Dimension 7 -- API Architecture."""

    DIMENSION = "api_architecture"

    PATTERNS: list[str] = [
        # Controllers
        "**/*controller*.py",
        "**/*controller*.java",
        "**/*controller*.ts",
        # Routes
        "**/*route*.py",
        "**/*route*.ts",
        "**/*route*.js",
        # Handlers
        "**/*handler*.py",
        "**/*handler*.go",
        # Django views
        "**/*view*.py",
        # OpenAPI / Swagger specs
        "**/openapi*.yaml",
        "**/openapi*.json",
        "**/swagger*.yaml",
        "**/swagger*.json",
        # GraphQL
        "**/*.graphql",
        "**/schema.graphql",
        # Resolvers
        "**/*resolver*.ts",
        "**/*resolver*.py",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return ApiArchitectureResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "rest_decorators": 0,
            "graphql_schemas": 0,
            "grpc_proto_files": 0,
            "rate_limiting_detected": False,
            "endpoint_count_estimate": 0,
            "openapi_spec_found": False,
            "frameworks_detected": [],
        }

        rest_patterns = [
            # Flask / FastAPI / Starlette
            re.compile(r"@app\.(get|post|put|delete|patch|route)\b", re.IGNORECASE),
            re.compile(r"@router\.(get|post|put|delete|patch)\b", re.IGNORECASE),
            # Django REST Framework
            re.compile(r"@api_view\b"),
            # Spring Boot
            re.compile(
                r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\b"
            ),
            # Express.js style
            re.compile(r"router\.(get|post|put|delete|patch)\("),
        ]

        rate_limit_patterns = [
            re.compile(r"rate.?limit", re.IGNORECASE),
            re.compile(r"throttle", re.IGNORECASE),
            re.compile(r"SlowAPI|slowapi", re.IGNORECASE),
            re.compile(r"RateLimit", re.IGNORECASE),
        ]

        frameworks: set[str] = set()

        for f in files:
            name = f.name.lower()

            # OpenAPI / Swagger detection
            if "openapi" in name or "swagger" in name:
                findings["openapi_spec_found"] = True

            # GraphQL schema detection
            if name.endswith(".graphql"):
                findings["graphql_schemas"] += 1

            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            # Count REST decorators / endpoint definitions
            for pat in rest_patterns:
                matches = pat.findall(content)
                findings["rest_decorators"] += len(matches)

            # Rate-limiting detection
            for pat in rate_limit_patterns:
                if pat.search(content):
                    findings["rate_limiting_detected"] = True
                    break

            # Framework hints
            if "@app.route" in content or "from flask" in content:
                frameworks.add("Flask")
            if "from fastapi" in content or "FastAPI" in content:
                frameworks.add("FastAPI")
            if "@RequestMapping" in content or "@GetMapping" in content:
                frameworks.add("Spring")
            if "from rest_framework" in content:
                frameworks.add("Django REST Framework")
            if "router.get(" in content or "express()" in content:
                frameworks.add("Express")

        # Check for gRPC proto files in the workspace
        proto_files = list(self.workspace.glob("**/*.proto"))
        findings["grpc_proto_files"] = len(proto_files)

        findings["endpoint_count_estimate"] = findings["rest_decorators"]
        findings["frameworks_detected"] = sorted(frameworks)

        return findings
