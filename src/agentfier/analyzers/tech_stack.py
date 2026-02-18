"""
Tech Stack analyzer -- Dimension 1.

Identifies programming languages, frameworks, build tools, and runtime
targets by inspecting file extensions, build manifests, and source files.
"""

from collections import Counter
from pathlib import Path

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import TechStackResult

# Map file extensions to language names
EXT_LANG_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".cs": "C#",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".php": "PHP",
    ".swift": "Swift",
    ".cpp": "C++",
    ".c": "C",
    ".sh": "Shell",
    ".bash": "Shell",
    ".r": "R",
    ".dart": "Dart",
}

BUILD_FILES = {
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "Pipfile",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "composer.json",
    "build.sbt",
    "project.clj",
    "mix.exs",
}


class TechStackAnalyzer(BaseAnalyzer):
    DIMENSION = "tech_stack"
    PATTERNS = [
        "**/*.py",
        "**/*.java",
        "**/*.js",
        "**/*.ts",
        "**/*.tsx",
        "**/*.jsx",
        "**/*.go",
        "**/*.rs",
        "**/*.rb",
        "**/*.cs",
        "**/*.kt",
        "**/*.scala",
        "**/pom.xml",
        "**/build.gradle",
        "**/build.gradle.kts",
        "**/package.json",
        "**/pyproject.toml",
        "**/setup.py",
        "**/requirements.txt",
        "**/go.mod",
        "**/Cargo.toml",
        "**/Gemfile",
        "**/composer.json",
        "**/Dockerfile*",
    ]

    def _get_result_model(self) -> type[TechStackResult]:
        return TechStackResult

    def _run_heuristics(self, files: list[Path]) -> dict:
        lang_counts: Counter[str] = Counter()
        build_tools_found: list[str] = []
        total_source = 0

        for f in files:
            ext = f.suffix.lower()
            if ext in EXT_LANG_MAP:
                lang_counts[EXT_LANG_MAP[ext]] += 1
                total_source += 1
            if f.name in BUILD_FILES:
                build_tools_found.append(f.name)

        # Calculate percentages
        lang_pcts: dict[str, float] = {}
        if total_source > 0:
            for lang, count in lang_counts.most_common():
                lang_pcts[lang] = round(count / total_source * 100, 1)

        return {
            "language_distribution": lang_pcts,
            "build_files_found": list(set(build_tools_found)),
            "total_source_files": total_source,
        }

    def get_relevant_files(self) -> list[Path]:
        """Override: prioritize build files, then sample source files."""
        all_files = super().get_relevant_files()
        build_files = [f for f in all_files if f.name in BUILD_FILES]
        source_files = [f for f in all_files if f.name not in BUILD_FILES]
        # Return all build files + up to 50 source file samples
        return build_files + source_files[:50]
