"""
Base analyzer class for all analysis dimensions.

Every concrete analyzer inherits from ``BaseAnalyzer``, defines its
``DIMENSION`` key, file ``PATTERNS``, and result model, then delegates the
heavy lifting (file discovery, heuristics, Claude call, parsing) to this
base class.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel

from agentfier.claude.client import ClaudeClient

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """Base class for all analysis dimensions."""

    MAX_FILES = 200  # Safety cap per analyzer
    MAX_CHARS = 50000  # Max characters to send to Claude

    # Subclasses define their file glob patterns
    PATTERNS: list[str] = []
    # Dimension name (matches key in DIMENSION_PROMPTS)
    DIMENSION: str = ""

    def __init__(self, claude_client: ClaudeClient, workspace_path: str):
        self.claude = claude_client
        self.workspace = Path(workspace_path)

    # ------------------------------------------------------------------
    # File discovery
    # ------------------------------------------------------------------

    def get_relevant_files(self) -> list[Path]:
        """Find files matching this analyzer's patterns."""
        files: list[Path] = []
        seen: set[str] = set()
        for pattern in self.PATTERNS:
            for f in self.workspace.glob(pattern):
                if f.is_file() and str(f) not in seen:
                    seen.add(str(f))
                    files.append(f)
        # Sort by size (smaller first, more likely to be config/source)
        files.sort(key=lambda f: f.stat().st_size)
        return files[: self.MAX_FILES]

    # ------------------------------------------------------------------
    # File reading
    # ------------------------------------------------------------------

    def _read_files(self, paths: list[Path], max_chars: int | None = None) -> str:
        """Read and concatenate files up to character budget."""
        max_chars = max_chars or self.MAX_CHARS
        parts: list[str] = []
        total = 0
        for p in paths:
            try:
                content = p.read_text(errors="replace")
                rel = p.relative_to(self.workspace)
                entry = f"--- {rel} ---\n{content}\n"
                if total + len(entry) > max_chars:
                    # Add partial if we have room
                    remaining = max_chars - total
                    if remaining > 200:
                        parts.append(
                            f"--- {rel} (truncated) ---\n{content[:remaining]}\n"
                        )
                    break
                parts.append(entry)
                total += len(entry)
            except Exception as e:
                logger.debug(f"Could not read {p}: {e}")
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Heuristics (override in subclasses)
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        """Override in subclasses for fast local pre-analysis."""
        return {}

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    @abstractmethod
    def _get_result_model(self) -> type[BaseModel]:
        """Return the Pydantic model class for this dimension's result."""
        ...

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def analyze(self) -> BaseModel:
        """Run the full analysis: find files -> heuristics -> Claude call -> parse."""
        from agentfier.claude.prompts import DIMENSION_PROMPTS

        files = self.get_relevant_files()
        if not files:
            logger.info(
                f"[{self.DIMENSION}] No relevant files found, returning defaults."
            )
            return self._get_result_model()()

        logger.info(f"[{self.DIMENSION}] Found {len(files)} relevant files.")
        heuristics = self._run_heuristics(files)
        file_contents = self._read_files(files)

        system_template, user_template = DIMENSION_PROMPTS[self.DIMENSION]
        model_class = self._get_result_model()
        schema = json.dumps(model_class.model_json_schema(), indent=2)

        system_prompt = system_template.format(schema=schema)
        user_content = user_template.format(
            file_contents=file_contents,
            heuristic_findings=json.dumps(heuristics, indent=2),
        )

        result_dict = self.claude.analyze(system_prompt, user_content)
        return model_class.model_validate(result_dict)
