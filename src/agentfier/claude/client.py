import json
import time
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929",
                 max_tokens: int = 4096, temperature: float = 0.2):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def analyze(self, system_prompt: str, user_content: str) -> dict:
        """Send analysis request to Claude, expecting structured JSON response.
        Includes retry logic (3 attempts with exponential backoff).
        On JSON parse failure, retries once with error correction prompt."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_content}]
                )
                text = response.content[0].text
                # Strip markdown code fences if present
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                    if text.endswith("```"):
                        text = text[:-3]
                    elif "```" in text:
                        text = text[:text.rfind("```")]
                return json.loads(text.strip())
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    # Retry with error correction
                    logger.warning(f"JSON parse error on attempt {attempt+1}: {e}")
                    user_content = (
                        f"Your previous response was not valid JSON. Error: {e}\n"
                        f"Please respond with ONLY valid JSON, no markdown or extra text.\n\n"
                        f"Original request:\n{user_content}"
                    )
                    time.sleep(2 ** attempt)
                else:
                    raise ValueError(f"Failed to get valid JSON from Claude after {max_retries} attempts: {e}")
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"API error on attempt {attempt+1}: {e}")
                    time.sleep(2 ** attempt)
                else:
                    raise

    def generate_diagram_spec(self, analysis_context: str, diagram_type: str) -> str:
        """Generate Graphviz DOT code for C4 diagrams.
        Returns raw DOT string."""
        system = (
            "You are a software architect generating C4 architecture diagrams in Graphviz DOT format.\n"
            "Output ONLY valid DOT code. No markdown, no explanation, just the DOT digraph."
        )
        # diagram_type is one of: c4_context, c4_container, c4_component
        user = f"Generate a C4 {diagram_type.replace('c4_', '').title()} diagram in DOT format based on this analysis:\n\n{analysis_context}"
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0.3,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if "```" in text:
                text = text[:text.rfind("```")]
        return text.strip()

    def generate_conversion_plan(self, full_analysis: str) -> dict:
        """Generate agent-native conversion plan. Returns dict."""
        system = (
            "You are an expert in agent-native system architecture. "
            "Given a comprehensive analysis of a traditional software system, produce a detailed "
            "conversion plan to transform it into an agent-native architecture.\n\n"
            "Your plan must include:\n"
            "1. agent_decomposition: list of {name, responsibilities (list[str]), tools (list[str])}\n"
            "2. communication_topology: string describing the communication pattern\n"
            "3. orchestration_pattern: string (supervisor/peer-to-peer/hierarchical)\n"
            "4. migration_phases: list of {phase (int), name (str), description (str), tasks (list[str]), risks (list[str])}\n"
            "5. risk_assessment: overall risk assessment string\n\n"
            "Respond ONLY with valid JSON."
        )
        return self.analyze(system, f"Full system analysis:\n\n{full_analysis}")

    def generate_flow_diagram(self, analysis_context: str) -> str:
        """Generate user flow diagram in DOT format."""
        system = (
            "You are a software architect generating user flow diagrams in Graphviz DOT format.\n"
            "Output ONLY valid DOT code. No markdown, no explanation."
        )
        user = f"Generate a user flow diagram in DOT format showing the main user journeys based on this analysis:\n\n{analysis_context}"
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0.3,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if "```" in text:
                text = text[:text.rfind("```")]
        return text.strip()
