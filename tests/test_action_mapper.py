"""
Tests for Action Mapper module
"""

import pytest
from src.action_mapper import (
    map_action,
    MappedAction,
    ActionMapperError,
    _validate_command,
    _is_destructive_command,
    format_commands_for_display,
)


# Sample Groq responses for testing
DEPLOY_RESPONSE = {
    "action": "deploy",
    "resource_type": "ec2",
    "resource_name": "flask-app",
    "aws_commands": [
        "aws ec2 run-instances --image-id ami-0123456789abcdef0 --instance-type t2.micro --count 1"
    ],
    "confidence": 0.85,
    "explanation_hindi": "EC2 instance banaya ja raha hai",
}

LIST_RESPONSE = {
    "action": "list",
    "resource_type": "ec2",
    "aws_commands": ["aws ec2 describe-instances"],
    "confidence": 0.95,
    "explanation_hindi": "EC2 instances ki list",
}

DELETE_RESPONSE = {
    "action": "delete",
    "resource_type": "ec2",
    "resource_name": "old-server",
    "aws_commands": ["aws ec2 terminate-instances --instance-ids i-1234567890abcdef0"],
    "confidence": 0.90,
    "is_destructive": True,
    "explanation_hindi": "Instance delete ho raha hai",
    "warning_hindi": "Yeh action irreversible hai!",
}

S3_RESPONSE = {
    "action": "deploy",
    "resource_type": "s3",
    "resource_name": "my-bucket",
    "aws_commands": ["aws s3 mb s3://my-bucket"],
    "confidence": 0.80,
    "explanation_hindi": "S3 bucket banaya ja raha hai",
}


class TestMapAction:
    def test_deploy_response(self):
        result = map_action(DEPLOY_RESPONSE)
        assert isinstance(result, MappedAction)
        assert result.action == "deploy"
        assert result.resource_type == "ec2"
        assert result.resource_name == "flask-app"
        assert len(result.aws_commands) > 0
        assert result.confidence == 0.85

    def test_list_response(self):
        result = map_action(LIST_RESPONSE)
        assert result.action == "list"
        assert result.resource_type == "ec2"
        assert "aws ec2 describe-instances" in result.aws_commands

    def test_delete_response_is_destructive(self):
        result = map_action(DELETE_RESPONSE)
        assert result.is_destructive is True
        assert result.action == "delete"

    def test_s3_create_response(self):
        result = map_action(S3_RESPONSE)
        assert result.action == "deploy"
        assert result.resource_type == "s3"

    def test_empty_response_raises(self):
        with pytest.raises(ActionMapperError):
            map_action({})

    def test_none_response_raises(self):
        with pytest.raises(ActionMapperError):
            map_action(None)

    def test_non_dict_raises(self):
        with pytest.raises(ActionMapperError):
            map_action("not a dict")

    def test_commands_are_strings(self):
        result = map_action(DEPLOY_RESPONSE)
        for cmd in result.aws_commands:
            assert isinstance(cmd, str)

    def test_commands_start_with_aws(self):
        result = map_action(DEPLOY_RESPONSE)
        for cmd in result.aws_commands:
            assert cmd.startswith("aws ")

    def test_confidence_is_float(self):
        result = map_action(DEPLOY_RESPONSE)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_command_without_aws_prefix_is_fixed(self):
        response = {
            "action": "list",
            "resource_type": "s3",
            "aws_commands": ["s3 ls"],  # Missing 'aws' prefix
            "confidence": 0.8,
            "explanation_hindi": "test",
        }
        result = map_action(response)
        assert all(cmd.startswith("aws ") for cmd in result.aws_commands)

    def test_invalid_commands_are_skipped(self):
        response = {
            "action": "list",
            "resource_type": "ec2",
            "aws_commands": [
                "aws ec2 describe-instances",
                "",  # empty command
                None,  # None command
            ],
            "confidence": 0.8,
            "explanation_hindi": "test",
        }
        result = map_action(response)
        assert len(result.aws_commands) == 1

    def test_delete_action_sets_destructive(self):
        response = {
            "action": "delete",
            "resource_type": "s3",
            "aws_commands": ["aws s3 ls"],  # non-destructive command but delete action
            "confidence": 0.8,
            "explanation_hindi": "test",
        }
        result = map_action(response)
        assert result.is_destructive is True


class TestValidateCommand:
    def test_valid_ec2_command(self):
        # Should not raise
        _validate_command("aws ec2 describe-instances")

    def test_valid_s3_command(self):
        _validate_command("aws s3 ls")

    def test_valid_lambda_command(self):
        _validate_command("aws lambda list-functions")

    def test_command_without_aws_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("ec2 describe-instances")

    def test_too_short_command_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws ec2")

    def test_unsupported_service_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws unsupported-service do-something")

    def test_semicolon_injection_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws ec2 describe-instances; rm -rf /")

    def test_pipe_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws ec2 describe-instances | cat /etc/passwd")

    def test_backtick_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws ec2 describe-instances `whoami`")

    def test_command_substitution_raises(self):
        with pytest.raises(ActionMapperError):
            _validate_command("aws ec2 describe-instances $(whoami)")


class TestIsDestructiveCommand:
    def test_terminate_instances_is_destructive(self):
        assert _is_destructive_command("aws ec2 terminate-instances --instance-ids i-123") is True

    def test_s3_rb_is_destructive(self):
        assert _is_destructive_command("aws s3 rb s3://my-bucket") is True

    def test_rds_delete_is_destructive(self):
        assert _is_destructive_command("aws rds delete-db-instance --db-instance-identifier mydb") is True

    def test_lambda_delete_is_destructive(self):
        assert _is_destructive_command("aws lambda delete-function --function-name my-func") is True

    def test_describe_instances_not_destructive(self):
        assert _is_destructive_command("aws ec2 describe-instances") is False

    def test_s3_ls_not_destructive(self):
        assert _is_destructive_command("aws s3 ls") is False

    def test_s3_mb_not_destructive(self):
        assert _is_destructive_command("aws s3 mb s3://new-bucket") is False


class TestMappedActionMethods:
    def test_to_dict(self):
        result = map_action(DEPLOY_RESPONSE)
        d = result.to_dict()
        assert "action" in d
        assert "resource_type" in d
        assert "resource_name" in d
        assert "aws_commands" in d
        assert "is_destructive" in d
        assert "confidence" in d
        assert "explanation_hindi" in d

    def test_generate_bash_script(self):
        result = map_action(DEPLOY_RESPONSE)
        script = result.generate_bash_script()
        assert script.startswith("#!/bin/bash")
        assert "set -e" in script
        assert result.aws_commands[0] in script

    def test_generate_bash_script_destructive_warning(self):
        result = map_action(DELETE_RESPONSE)
        script = result.generate_bash_script()
        assert "WARNING" in script or "destructive" in script.lower()


class TestFormatCommandsForDisplay:
    def test_basic_format(self):
        result = map_action(DEPLOY_RESPONSE)
        output = format_commands_for_display(result)
        assert "DEPLOY" in output.upper()
        assert "ec2" in output.lower()
        assert "85%" in output or "0.85" in output

    def test_destructive_warning_shown(self):
        result = map_action(DELETE_RESPONSE)
        output = format_commands_for_display(result)
        assert "WARNING" in output or "destructive" in output.lower() or "⚠️" in output

    def test_dry_run_shown(self):
        result = map_action(LIST_RESPONSE)
        output = format_commands_for_display(result, dry_run=True)
        assert "DRY RUN" in output.upper()

    def test_commands_listed(self):
        result = map_action(LIST_RESPONSE)
        output = format_commands_for_display(result)
        assert "aws ec2 describe-instances" in output
