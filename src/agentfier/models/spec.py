"""
Agentfier agent specification model.

Wraps the raw ``AnalysisResult`` with a conversion plan, diagram paths,
and optional API documentation to produce the final ``AgentSpec`` output.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from agentfier.models.analysis import AnalysisResult


# =====================================================================
# Conversion plan sub-models
# =====================================================================


class AgentDecomposition(BaseModel):
    """Describes a single agent in the target multi-agent system."""

    name: str
    responsibilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class MigrationPhase(BaseModel):
    """One phase in the migration plan from monolith to agent system."""

    phase: str
    description: Optional[str] = None
    tasks: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class ConversionPlan(BaseModel):
    """Complete plan for converting the analysed codebase into an agent-based
    architecture."""

    agent_decomposition: List[AgentDecomposition] = Field(default_factory=list)
    communication_topology: str = ""
    orchestration_pattern: str = ""
    migration_phases: List[MigrationPhase] = Field(default_factory=list)
    risk_assessment: str = ""


# =====================================================================
# Top-level spec
# =====================================================================


class AgentSpec(BaseModel):
    """Final output artifact produced by the Agentfier pipeline.

    Combines the full analysis result with a conversion plan, generated
    diagrams, and optional API documentation.
    """

    analysis: AnalysisResult
    conversion_plan: Optional[ConversionPlan] = None
    diagram_paths: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps diagram name (e.g. 'context', 'container') to file path.",
    )
    api_documentation: Optional[str] = None
