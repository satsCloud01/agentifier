"""
Business Logic analyzer.

Detects domain models, workflows, background jobs, state machines, and
event-driven patterns by scanning service layers, domain modules, task
definitions, and event handlers.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import BusinessLogicResult

logger = logging.getLogger(__name__)


class BusinessLogicAnalyzer(BaseAnalyzer):
    """Dimension 8 -- Business Logic."""

    DIMENSION = "business_logic"

    PATTERNS: list[str] = [
        # Service layers
        "**/services/**/*.py",
        "**/services/**/*.java",
        "**/services/**/*.ts",
        # Domain layer
        "**/domain/**/*.py",
        "**/domain/**/*.java",
        # Workflows
        "**/workflows/**/*",
        "**/workflow/**/*",
        # Tasks / Jobs
        "**/tasks/**/*.py",
        "**/jobs/**/*.py",
        "**/jobs/**/*.java",
        # CQRS / Event sourcing
        "**/commands/**/*",
        "**/events/**/*",
        "**/handlers/**/*",
        # Schedulers
        "**/celery*.py",
        "**/*scheduler*.py",
        "**/*scheduler*.java",
        "**/cron*.py",
        "**/*cron*.java",
    ]

    # ------------------------------------------------------------------
    # Result model
    # ------------------------------------------------------------------

    def _get_result_model(self) -> type[BaseModel]:
        return BusinessLogicResult

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _run_heuristics(self, files: list[Path]) -> dict:
        findings: dict = {
            "celery_tasks": 0,
            "scheduled_annotations": 0,
            "state_machine_imports": False,
            "event_bus_patterns": False,
            "service_classes": 0,
            "workflow_files": 0,
            "job_files": 0,
        }

        celery_patterns = [
            re.compile(r"@(shared_task|task|celery_app\.task)\b"),
            re.compile(r"@app\.task\b"),
        ]

        scheduled_patterns = [
            re.compile(r"@Scheduled\b"),
            re.compile(r"crontab\("),
            re.compile(r"beat_schedule"),
        ]

        state_machine_keywords = [
            "transitions",
            "statemachine",
            "state_machine",
            "StateMachine",
            "django_fsm",
            "xstate",
        ]

        event_bus_keywords = [
            "EventBus",
            "event_bus",
            "EventEmitter",
            "event_emitter",
            "publish_event",
            "emit(",
            "on_event",
            "EventHandler",
            "DomainEvent",
            "ApplicationEvent",
        ]

        service_class_pattern = re.compile(
            r"class\s+\w*Service\w*\s*[\(:]"
        )

        for f in files:
            name = f.name.lower()
            rel = str(f.relative_to(self.workspace)).lower()

            # Count workflow and job files
            if "workflow" in rel:
                findings["workflow_files"] += 1
            if "job" in rel or "task" in rel:
                findings["job_files"] += 1

            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            # Celery tasks
            for pat in celery_patterns:
                findings["celery_tasks"] += len(pat.findall(content))

            # Scheduled annotations
            for pat in scheduled_patterns:
                findings["scheduled_annotations"] += len(pat.findall(content))

            # State machine detection
            for kw in state_machine_keywords:
                if kw in content:
                    findings["state_machine_imports"] = True
                    break

            # Event bus / emitter detection
            for kw in event_bus_keywords:
                if kw in content:
                    findings["event_bus_patterns"] = True
                    break

            # Service classes
            findings["service_classes"] += len(
                service_class_pattern.findall(content)
            )

        return findings
