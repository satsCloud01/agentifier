"""
Dependency analyzer -- Dimension 2.

Examines dependency manifests and lock files to identify direct and
transitive dependencies, license distribution, and potential vulnerabilities.
"""

import json as _json
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import DependencyResult

DEP_FILES = {
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "requirements.txt",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "pyproject.toml",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
}


class DependencyAnalyzer(BaseAnalyzer):
    DIMENSION = "dependencies"
    PATTERNS = [
        "**/pom.xml",
        "**/build.gradle",
        "**/build.gradle.kts",
        "**/package.json",
        "**/package-lock.json",
        "**/yarn.lock",
        "**/requirements.txt",
        "**/Pipfile",
        "**/Pipfile.lock",
        "**/poetry.lock",
        "**/pyproject.toml",
        "**/go.mod",
        "**/go.sum",
        "**/Cargo.toml",
        "**/Cargo.lock",
        "**/Gemfile",
        "**/Gemfile.lock",
        "**/composer.json",
        "**/composer.lock",
    ]

    def _get_result_model(self) -> type[DependencyResult]:
        return DependencyResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        dep_files_found = [f.name for f in files]
        has_lockfile = any("lock" in f.name.lower() for f in files)

        # Try to count direct deps from common formats
        dep_count = 0
        for f in files:
            if f.name == "requirements.txt":
                try:
                    lines = f.read_text(errors="replace").strip().split("\n")
                    dep_count += len(
                        [l for l in lines if l.strip() and not l.startswith("#")]
                    )
                except Exception:
                    pass
            elif f.name == "package.json":
                try:
                    data = _json.loads(f.read_text())
                    dep_count += len(data.get("dependencies", {}))
                    dep_count += len(data.get("devDependencies", {}))
                except Exception:
                    pass

        return {
            "dependency_files": list(set(dep_files_found)),
            "has_lockfile": has_lockfile,
            "estimated_direct_deps": dep_count,
        }
