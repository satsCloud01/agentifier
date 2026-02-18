"""
Agentfier enumeration types.

Defines the core enumerations used across ingestion, analysis, and output
stages of the pipeline.
"""

from enum import Enum


class InputType(str, Enum):
    """Describes the source type of the codebase being analyzed."""

    GITHUB = "github"
    JAR_WAR = "jar_war"
    LOCAL = "local"


class AnalysisStatus(str, Enum):
    """Tracks the lifecycle status of an analysis run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class DiagramLevel(str, Enum):
    """C4-model diagram abstraction levels."""

    CONTEXT = "context"
    CONTAINER = "container"
    COMPONENT = "component"
