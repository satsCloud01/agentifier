"""
Agentfier analyzers -- one module per analysis dimension.

Each analyzer extends ``BaseAnalyzer`` and covers a single dimension of
the codebase analysis (tech stack, dependencies, data layer, etc.).
"""

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.analyzers.tech_stack import TechStackAnalyzer
from agentfier.analyzers.dependencies import DependencyAnalyzer
from agentfier.analyzers.data_layer import DataLayerAnalyzer
from agentfier.analyzers.integrations import IntegrationAnalyzer
from agentfier.analyzers.auth import AuthAnalyzer
from agentfier.analyzers.observability import ObservabilityAnalyzer
from agentfier.analyzers.api_architecture import ApiArchitectureAnalyzer
from agentfier.analyzers.business_logic import BusinessLogicAnalyzer
from agentfier.analyzers.infrastructure import InfrastructureAnalyzer
from agentfier.analyzers.security import SecurityAnalyzer
from agentfier.analyzers.frontend import FrontendAnalyzer
from agentfier.analyzers.configuration import ConfigurationAnalyzer

__all__ = [
    "BaseAnalyzer",
    "TechStackAnalyzer",
    "DependencyAnalyzer",
    "DataLayerAnalyzer",
    "IntegrationAnalyzer",
    "AuthAnalyzer",
    "ObservabilityAnalyzer",
    "ApiArchitectureAnalyzer",
    "BusinessLogicAnalyzer",
    "InfrastructureAnalyzer",
    "SecurityAnalyzer",
    "FrontendAnalyzer",
    "ConfigurationAnalyzer",
]
