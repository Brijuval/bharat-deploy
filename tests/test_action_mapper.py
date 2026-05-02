"""
Tests for src/action_mapper.py
"""

import pytest
from src.action_mapper import ActionMapper, ActionMapperError


def _base_response(**overrides):
    base = {
        "action": "ec2_describe_instances",
        "service": "ec2",
        "operation": "describe",
        "aws_cli_command": "aws ec2 describe-instances",
        "parameters": {},
        "is_destructive": False,
        "confirmation_required": False,
        "explanation_hi": "EC2 instances की list दिखाएगा।",
        "explanation_en": "Lists all EC2 instances.",
        "confidence": 0.9,
    }
    base.update(overrides)
    return base


class TestActionMapper:

    def setup_method(self):
        self.mapper = ActionMapper()

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_map_returns_dict(self):
        result = self.mapper.map(_base_response())
        assert isinstance(result, dict)

    def test_map_preserves_command(self):
        result = self.mapper.map(_base_response())
        assert result["aws_cli_command"] == "aws ec2 describe-instances"

    def test_map_generates_bash_script(self):
        result = self.mapper.map(_base_response())
        assert "bash" in result["bash_script"]
        assert "aws ec2 describe-instances" in result["bash_script"]

    def test_map_s3_list(self):
        resp = _base_response(
            service="s3",
            aws_cli_command="aws s3 ls",
        )
        result = self.mapper.map(resp)
        assert result["aws_cli_command"] == "aws s3 ls"

    def test_map_preserves_explanations(self):
        result = self.mapper.map(_base_response())
        assert result["explanation_hi"] == "EC2 instances की list दिखाएगा।"
        assert result["explanation_en"] == "Lists all EC2 instances."

    def test_map_returns_confidence(self):
        result = self.mapper.map(_base_response(confidence=0.85))
        assert result["confidence"] == 0.85

    # ------------------------------------------------------------------
    # Destructive detection
    # ------------------------------------------------------------------

    def test_destructive_delete_flagged(self):
        resp = _base_response(
            aws_cli_command="aws ec2 terminate-instances --instance-ids i-12345",
            is_destructive=False,  # LLM missed it
        )
        result = self.mapper.map(resp)
        assert result["is_destructive"] is True
        assert result["confirmation_required"] is True

    def test_non_destructive_list_not_flagged(self):
        result = self.mapper.map(_base_response())
        assert result["is_destructive"] is False

    def test_llm_marked_destructive_preserved(self):
        resp = _base_response(
            aws_cli_command="aws s3 rb s3://my-bucket --force",
            is_destructive=True,
            confirmation_required=True,
        )
        result = self.mapper.map(resp)
        assert result["is_destructive"] is True
        assert result["confirmation_required"] is True

    # ------------------------------------------------------------------
    # Safety validation failures
    # ------------------------------------------------------------------

    def test_raises_if_aws_cli_command_missing(self):
        resp = {
            "service": "ec2",
            "explanation_hi": "",
            "explanation_en": "",
        }
        with pytest.raises(ActionMapperError, match="missing required fields"):
            self.mapper.map(resp)

    def test_raises_if_command_not_starting_with_aws(self):
        resp = _base_response(aws_cli_command="rm -rf /")
        with pytest.raises(ActionMapperError, match="must start with 'aws'"):
            self.mapper.map(resp)

    def test_raises_on_unknown_service(self):
        resp = _base_response(aws_cli_command="aws notaservice list")
        with pytest.raises(ActionMapperError, match="not in the allowed list"):
            self.mapper.map(resp)

    def test_raises_on_shell_injection_semicolon(self):
        resp = _base_response(aws_cli_command="aws ec2 describe-instances; rm -rf /")
        with pytest.raises(ActionMapperError, match="forbidden"):
            self.mapper.map(resp)

    def test_raises_on_shell_injection_pipe(self):
        resp = _base_response(aws_cli_command="aws ec2 describe-instances | cat /etc/passwd")
        with pytest.raises(ActionMapperError, match="forbidden"):
            self.mapper.map(resp)

    def test_raises_on_empty_command(self):
        resp = _base_response(aws_cli_command="")
        with pytest.raises(ActionMapperError):
            self.mapper.map(resp)

    # ------------------------------------------------------------------
    # Bash script content
    # ------------------------------------------------------------------

    def test_bash_script_has_shebang(self):
        result = self.mapper.map(_base_response())
        assert result["bash_script"].startswith("#!/usr/bin/env bash")

    def test_bash_script_has_set_pipefail(self):
        result = self.mapper.map(_base_response())
        assert "set -euo pipefail" in result["bash_script"]
