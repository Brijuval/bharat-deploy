import json
import pytest
from unittest.mock import MagicMock, patch

from src.groq_handler import GroqHandler


@patch('src.groq_handler.Groq')
def test_parse_command_returns_dict(mock_groq_class):
    """parse_command should return a dict parsed from the JSON response."""
    mock_response_data = {
        "action": "deploy",
        "confidence": 0.95,
        "aws_command": "aws ec2 run-instances --image-id ami-0abcdef1234567890",
        "explanation": "Launch a new EC2 instance",
        "parameters": {},
    }

    mock_message = MagicMock()
    mock_message.content = json.dumps(mock_response_data)

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_groq_class.return_value = mock_client

    handler = GroqHandler("test_key")
    result = handler.parse_command("deploy flask app")

    assert result["action"] == "deploy"
    assert result["confidence"] == 0.95
    assert "aws ec2 run-instances" in result["aws_command"]


@patch('src.groq_handler.Groq')
def test_parse_command_calls_correct_model(mock_groq_class):
    """parse_command should call the llama-3.1-70b-versatile model."""
    mock_message = MagicMock()
    mock_message.content = json.dumps({"action": "list"})

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_groq_class.return_value = mock_client

    handler = GroqHandler("test_key")
    handler.parse_command("list resources")

    call_kwargs = mock_client.chat.completions.create.call_args
    assert call_kwargs[1]["model"] == "llama-3.1-70b-versatile"


@patch('src.groq_handler.Groq')
def test_parse_command_uses_json_response_format(mock_groq_class):
    """parse_command should request json_object response format."""
    mock_message = MagicMock()
    mock_message.content = json.dumps({"action": "delete"})

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_groq_class.return_value = mock_client

    handler = GroqHandler("test_key")
    handler.parse_command("delete instance")

    call_kwargs = mock_client.chat.completions.create.call_args
    assert call_kwargs[1]["response_format"] == {"type": "json_object"}
