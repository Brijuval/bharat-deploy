import pytest
from src.action_mapper import ActionMapper


@pytest.fixture
def mapper():
    return ActionMapper()


def test_destructive_operation_delete(mapper):
    result = mapper.map_action({
        "action": "delete",
        "aws_command": "aws ec2 terminate-instances --instance-ids i-1234567890abcdef0",
        "confidence": 0.9,
        "explanation": "Terminate the instance",
    })
    assert result["is_destructive"] is True
    assert result["requires_confirmation"] is True


def test_destructive_operation_terminate(mapper):
    result = mapper.map_action({
        "action": "terminate",
        "aws_command": "aws ec2 terminate-instances",
        "confidence": 0.9,
    })
    assert result["is_destructive"] is True


def test_destructive_operation_destroy(mapper):
    result = mapper.map_action({
        "action": "destroy",
        "aws_command": "aws cloudformation delete-stack",
        "confidence": 0.85,
    })
    assert result["is_destructive"] is True


def test_non_destructive_operation(mapper):
    result = mapper.map_action({
        "action": "deploy",
        "aws_command": "aws ec2 run-instances",
        "confidence": 0.9,
    })
    assert result["is_destructive"] is False


def test_low_confidence_requires_confirmation(mapper):
    result = mapper.map_action({
        "action": "deploy",
        "aws_command": "aws ec2 run-instances",
        "confidence": 0.5,
    })
    assert result["requires_confirmation"] is True


def test_high_confidence_non_destructive_no_confirmation(mapper):
    result = mapper.map_action({
        "action": "list",
        "aws_command": "aws ec2 describe-instances",
        "confidence": 0.95,
    })
    assert result["requires_confirmation"] is False


def test_command_extracted(mapper):
    result = mapper.map_action({
        "action": "list",
        "aws_command": "aws s3 ls",
        "confidence": 0.9,
    })
    assert result["command"] == "aws s3 ls"


def test_missing_fields_default_safely(mapper):
    result = mapper.map_action({})
    assert result["command"] == ""
    assert result["confidence"] == 0
    assert result["is_destructive"] is False
