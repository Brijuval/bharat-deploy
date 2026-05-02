"""
Tests for Groq Handler module (all mocked - no real API calls)
"""

import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from src.groq_handler import GroqHandler, GroqHandlerError


# Sample mock responses
MOCK_DEPLOY_RESPONSE = {
    "action": "deploy",
    "resource_type": "ec2",
    "resource_name": "flask-app",
    "aws_commands": [
        "aws ec2 run-instances --image-id ami-0123456789abcdef0 --instance-type t2.micro --count 1"
    ],
    "confidence": 0.85,
    "explanation_hindi": "Flask app ke liye EC2 instance banaya ja raha hai",
}

MOCK_LIST_RESPONSE = {
    "action": "list",
    "resource_type": "ec2",
    "aws_commands": ["aws ec2 describe-instances"],
    "confidence": 0.95,
    "explanation_hindi": "Saare EC2 instances ki list dekh rahe hain",
}


class TestGroqHandlerInit:
    def test_init_with_api_key(self):
        with patch("src.groq_handler.Groq"):
            handler = GroqHandler(api_key="test-key-123")
        assert handler.api_key == "test-key-123"

    def test_init_with_custom_model(self):
        with patch("src.groq_handler.Groq"):
            handler = GroqHandler(api_key="test-key", model="llama3-70b-8192")
        assert handler.model == "llama3-70b-8192"

    def test_init_uses_default_model(self):
        with patch("src.groq_handler.Groq"):
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                handler = GroqHandler()
        assert handler.model is not None
        assert len(handler.model) > 0

    def test_no_api_key_raises_on_call(self):
        with patch("src.groq_handler.GROQ_AVAILABLE", True):
            handler = GroqHandler.__new__(GroqHandler)
            handler.api_key = None
            handler.model = "llama3-8b-8192"
            handler.max_retries = 3
            handler.retry_delay = 1.0
            handler.temperature = 0.1
            handler.max_tokens = 1024
            handler._client = None

            with pytest.raises(GroqHandlerError, match="GROQ_API_KEY"):
                handler.call([{"role": "user", "content": "test"}])

    def test_groq_not_available_raises(self):
        with patch("src.groq_handler.GROQ_AVAILABLE", False):
            handler = GroqHandler.__new__(GroqHandler)
            handler.api_key = "test"
            handler.model = "llama3-8b-8192"
            handler.max_retries = 3
            handler.retry_delay = 1.0
            handler.temperature = 0.1
            handler.max_tokens = 1024
            handler._client = None

            with pytest.raises(GroqHandlerError, match="groq package"):
                handler.call([{"role": "user", "content": "test"}])


class TestGroqHandlerCall:
    def _make_mock_response(self, content: dict) -> MagicMock:
        """Create a mock Groq API response."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(content)
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150
        return mock_response

    def test_successful_deploy_call(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            MOCK_DEPLOY_RESPONSE
        )

        with patch("src.groq_handler.Groq", return_value=mock_client):
            handler = GroqHandler(api_key="test-key")
            result = handler.call([{"role": "user", "content": "flask banao"}], "deploy")

        assert result["action"] == "deploy"
        assert result["resource_type"] == "ec2"
        assert "aws_commands" in result
        assert "_metadata" in result
        assert result["_metadata"]["attempt"] == 1

    def test_successful_list_call(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            MOCK_LIST_RESPONSE
        )

        with patch("src.groq_handler.Groq", return_value=mock_client):
            handler = GroqHandler(api_key="test-key")
            result = handler.call([{"role": "user", "content": "list karo"}], "list")

        assert result["action"] == "list"
        assert result["confidence"] == 0.95

    def test_retry_on_json_error(self):
        mock_client = MagicMock()
        good_response = self._make_mock_response(MOCK_DEPLOY_RESPONSE)

        # First call returns invalid JSON, second returns valid JSON
        bad_response = MagicMock()
        bad_response.choices[0].message.content = "not valid json {"
        bad_response.usage = None

        mock_client.chat.completions.create.side_effect = [bad_response, good_response]

        with patch("src.groq_handler.Groq", return_value=mock_client):
            with patch("time.sleep"):  # Don't actually sleep in tests
                handler = GroqHandler(api_key="test-key")
                handler.max_retries = 3
                result = handler.call([{"role": "user", "content": "test"}])

        assert result["action"] == "deploy"
        assert mock_client.chat.completions.create.call_count == 2

    def test_all_retries_fail_raises_error(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = (
            "invalid json {"
        )
        mock_client.chat.completions.create.return_value.usage = None

        with patch("src.groq_handler.Groq", return_value=mock_client):
            with patch("time.sleep"):
                handler = GroqHandler(api_key="test-key")
                handler.max_retries = 2

                with pytest.raises(GroqHandlerError):
                    handler.call([{"role": "user", "content": "test"}])

    def test_rate_limit_triggers_backoff(self):
        mock_client = MagicMock()
        good_response = self._make_mock_response(MOCK_LIST_RESPONSE)

        mock_client.chat.completions.create.side_effect = [
            Exception("rate limit exceeded 429"),
            good_response,
        ]

        with patch("src.groq_handler.Groq", return_value=mock_client):
            with patch("time.sleep") as mock_sleep:
                handler = GroqHandler(api_key="test-key")
                handler.max_retries = 3
                result = handler.call([{"role": "user", "content": "test"}])

        assert result["action"] == "list"
        mock_sleep.assert_called()  # Should have slept for backoff


class TestGroqHandlerParseJson:
    def setup_method(self):
        with patch("src.groq_handler.Groq"):
            self.handler = GroqHandler(api_key="test-key")

    def test_valid_json(self):
        result = self.handler._parse_json_response('{"action": "deploy"}')
        assert result["action"] == "deploy"

    def test_json_with_markdown_code_block(self):
        content = '```json\n{"action": "list"}\n```'
        result = self.handler._parse_json_response(content)
        assert result["action"] == "list"

    def test_json_with_code_block(self):
        content = '```\n{"action": "delete"}\n```'
        result = self.handler._parse_json_response(content)
        assert result["action"] == "delete"

    def test_empty_content_raises(self):
        with pytest.raises(ValueError, match="Empty response"):
            self.handler._parse_json_response("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="Empty response"):
            self.handler._parse_json_response("   ")

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            self.handler._parse_json_response("{not valid json")

    def test_nested_json(self):
        content = '{"action": "deploy", "commands": ["aws ec2 run-instances"]}'
        result = self.handler._parse_json_response(content)
        assert result["action"] == "deploy"
        assert len(result["commands"]) == 1


class TestGroqHandlerModelInfo:
    def test_get_model_info(self):
        with patch("src.groq_handler.Groq"):
            handler = GroqHandler(api_key="test-key", model="llama3-8b-8192")
        info = handler.get_model_info()

        assert info["model"] == "llama3-8b-8192"
        assert "max_retries" in info
        assert "temperature" in info
        assert "max_tokens" in info
        assert "client_ready" in info
