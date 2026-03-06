"""
Tests for ClaudeClient: analyze, generate_diagram_spec, generate_conversion_plan,
generate_flow_diagram, JSON parsing, retry logic, and error handling.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call

from agentfier.claude.client import ClaudeClient


def _make_client(**kwargs) -> ClaudeClient:
    with patch("agentfier.claude.client.Anthropic"):
        return ClaudeClient(api_key="sk-ant-test", **kwargs)


def _mock_text_response(client: ClaudeClient, text: str):
    """Configure client.client.messages.create to return a mocked response with given text."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    client.client.messages.create.return_value = msg
    return msg


# ===========================================================================
# ClaudeClient.__init__
# ===========================================================================


class TestClaudeClientInit:
    def test_default_model(self):
        c = _make_client()
        assert c.model == "claude-sonnet-4-5-20250929"

    def test_custom_model(self):
        c = _make_client(model="claude-haiku-4-5-20251001")
        assert c.model == "claude-haiku-4-5-20251001"

    def test_default_max_tokens(self):
        c = _make_client()
        assert c.max_tokens == 4096

    def test_default_temperature(self):
        c = _make_client()
        assert c.temperature == 0.2


# ===========================================================================
# ClaudeClient.analyze
# ===========================================================================


class TestClaudeClientAnalyze:
    def test_returns_dict_from_json(self):
        c = _make_client()
        payload = {"languages": ["Python"], "confidence": 0.9}
        _mock_text_response(c, json.dumps(payload))
        result = c.analyze("system", "user")
        assert result == payload

    def test_strips_markdown_fences(self):
        c = _make_client()
        payload = {"key": "value"}
        fenced = f"```json\n{json.dumps(payload)}\n```"
        _mock_text_response(c, fenced)
        result = c.analyze("system", "user")
        assert result == payload

    def test_strips_backtick_fences_no_lang(self):
        c = _make_client()
        payload = {"x": 1}
        fenced = f"```\n{json.dumps(payload)}\n```"
        _mock_text_response(c, fenced)
        result = c.analyze("system", "user")
        assert result == payload

    def test_raises_after_max_retries_on_invalid_json(self):
        c = _make_client()
        _mock_text_response(c, "not json at all {{")
        with pytest.raises(ValueError, match="Failed to get valid JSON"):
            c.analyze("system", "user")

    def test_retries_on_json_error(self):
        """First call returns bad JSON, second returns valid JSON."""
        c = _make_client()
        bad = MagicMock()
        bad.content = [MagicMock(text="INVALID")]
        good = MagicMock()
        good.content = [MagicMock(text='{"ok": true}')]
        c.client.messages.create.side_effect = [bad, good, good]

        with patch("time.sleep"):  # skip backoff
            result = c.analyze("system", "user")
        assert result == {"ok": True}

    def test_retries_on_api_exception(self):
        c = _make_client()
        good = MagicMock()
        good.content = [MagicMock(text='{"status": "ok"}')]
        c.client.messages.create.side_effect = [Exception("rate limit"), good]

        with patch("time.sleep"):
            result = c.analyze("system", "user")
        assert result["status"] == "ok"

    def test_raises_after_max_retries_on_api_error(self):
        c = _make_client()
        c.client.messages.create.side_effect = Exception("persistent error")
        with patch("time.sleep"):
            with pytest.raises(Exception, match="persistent error"):
                c.analyze("system", "user")

    def test_passes_correct_model_and_params(self):
        c = _make_client(model="claude-haiku-4-5-20251001", max_tokens=1024, temperature=0.5)
        _mock_text_response(c, '{"ok": 1}')
        c.analyze("sys_prompt", "user_content")
        call_kwargs = c.client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
        assert call_kwargs["max_tokens"] == 1024
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["system"] == "sys_prompt"

    def test_nested_json_preserved(self):
        c = _make_client()
        payload = {"a": {"b": [1, 2, 3]}, "c": True}
        _mock_text_response(c, json.dumps(payload))
        result = c.analyze("s", "u")
        assert result["a"]["b"] == [1, 2, 3]


# ===========================================================================
# ClaudeClient.generate_diagram_spec
# ===========================================================================


class TestGenerateDiagramSpec:
    def test_returns_dot_string(self):
        c = _make_client()
        dot = 'digraph { A -> B }'
        _mock_text_response(c, dot)
        result = c.generate_diagram_spec("analysis context", "c4_context")
        assert "digraph" in result or result == dot

    def test_strips_markdown_from_dot(self):
        c = _make_client()
        dot = "digraph { A -> B }"
        fenced = f"```dot\n{dot}\n```"
        _mock_text_response(c, fenced)
        result = c.generate_diagram_spec("context", "c4_container")
        assert "```" not in result

    def test_calls_messages_create(self):
        c = _make_client()
        _mock_text_response(c, "digraph { X -> Y }")
        c.generate_diagram_spec("ctx", "c4_component")
        c.client.messages.create.assert_called_once()

    def test_diagram_type_in_user_prompt(self):
        c = _make_client()
        _mock_text_response(c, "digraph {}")
        c.generate_diagram_spec("ctx", "c4_context")
        call_args = c.client.messages.create.call_args
        messages = call_args.kwargs.get("messages") or call_args[1].get("messages", [])
        user_msg = messages[0]["content"]
        assert "context" in user_msg.lower()


# ===========================================================================
# ClaudeClient.generate_conversion_plan
# ===========================================================================


class TestGenerateConversionPlan:
    def test_returns_dict(self):
        c = _make_client()
        plan = {
            "agent_decomposition": [],
            "communication_topology": "star",
            "orchestration_pattern": "supervisor",
            "migration_phases": [],
            "risk_assessment": "low",
        }
        _mock_text_response(c, json.dumps(plan))
        result = c.generate_conversion_plan("full analysis text")
        assert isinstance(result, dict)
        assert result["communication_topology"] == "star"

    def test_passes_analysis_in_user_content(self):
        c = _make_client()
        _mock_text_response(c, '{"agent_decomposition": [], "communication_topology": "", "orchestration_pattern": "", "migration_phases": [], "risk_assessment": ""}')
        c.generate_conversion_plan("MY_ANALYSIS")
        call_args = c.client.messages.create.call_args
        messages = call_args.kwargs.get("messages", [])
        assert any("MY_ANALYSIS" in m.get("content", "") for m in messages)


# ===========================================================================
# ClaudeClient.generate_flow_diagram
# ===========================================================================


class TestGenerateFlowDiagram:
    def test_returns_dot_string(self):
        c = _make_client()
        _mock_text_response(c, "digraph flow { Start -> Login -> Dashboard }")
        result = c.generate_flow_diagram("ctx")
        assert isinstance(result, str)

    def test_strips_markdown_from_flow(self):
        c = _make_client()
        dot = "digraph flow { A -> B }"
        _mock_text_response(c, f"```\n{dot}\n```")
        result = c.generate_flow_diagram("ctx")
        assert "```" not in result

    def test_calls_messages_create(self):
        c = _make_client()
        _mock_text_response(c, "digraph {}")
        c.generate_flow_diagram("ctx")
        c.client.messages.create.assert_called_once()
