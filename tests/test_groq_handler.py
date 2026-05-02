"""
Tests for src/groq_handler.py — all calls to Groq are mocked.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from src.groq_handler import GroqHandler, GroqHandlerError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(payload: dict) -> MagicMock:
    """Return a mock that mimics groq.ChatCompletion response shape."""
    msg = MagicMock()
    msg.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGroqHandler:

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_send_prompt_returns_dict(self, mock_build):
        payload = {
            "action": "ec2_create_instance",
            "service": "ec2",
            "operation": "create",
            "aws_cli_command": "aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro",
            "parameters": {},
            "is_destructive": False,
            "confirmation_required": False,
            "explanation_hi": "EC2 instance बनाई जाएगी।",
            "explanation_en": "An EC2 instance will be created.",
            "confidence": 0.9,
        }
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_mock_response(payload)
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="test-key")
        result = handler.send_prompt("system prompt", "user message")

        assert isinstance(result, dict)
        assert result["service"] == "ec2"
        assert result["confidence"] == 0.9

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_send_prompt_calls_groq_with_correct_params(self, mock_build):
        payload = {"aws_cli_command": "aws ec2 describe-instances", "confidence": 0.8}
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_mock_response(payload)
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="test-key", model="llama3-8b-8192")
        handler.send_prompt("sys", "usr")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "llama3-8b-8192"
        assert call_kwargs["response_format"] == {"type": "json_object"}
        messages = call_kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_raises_on_invalid_json(self, mock_build):
        msg = MagicMock()
        msg.content = "this is not json"
        choice = MagicMock()
        choice.message = msg
        resp = MagicMock()
        resp.choices = [choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = resp
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="test-key")
        with pytest.raises(GroqHandlerError, match="invalid JSON"):
            handler.send_prompt("sys", "usr")

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_retries_on_transient_error(self, mock_build):
        payload = {"aws_cli_command": "aws s3 ls", "confidence": 0.7}
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            RuntimeError("transient error"),
            _make_mock_response(payload),
        ]
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="test-key", max_retries=3, retry_delay=0)
        result = handler.send_prompt("sys", "usr")
        assert result["aws_cli_command"] == "aws s3 ls"
        assert mock_client.chat.completions.create.call_count == 2

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_raises_after_max_retries(self, mock_build):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("always fails")
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="test-key", max_retries=2, retry_delay=0)
        with pytest.raises(GroqHandlerError, match="2 attempts"):
            handler.send_prompt("sys", "usr")

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_raises_immediately_on_auth_error(self, mock_build):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception(
            "401 authentication failed"
        )
        mock_build.return_value = mock_client

        handler = GroqHandler(api_key="bad-key", max_retries=3, retry_delay=0)
        with pytest.raises(GroqHandlerError, match="Authentication"):
            handler.send_prompt("sys", "usr")
        # Must NOT retry on auth failure
        assert mock_client.chat.completions.create.call_count == 1

    @patch("src.groq_handler.GroqHandler._build_client")
    def test_default_model(self, mock_build):
        mock_build.return_value = MagicMock()
        handler = GroqHandler(api_key="test-key")
        assert handler.model == GroqHandler.DEFAULT_MODEL
