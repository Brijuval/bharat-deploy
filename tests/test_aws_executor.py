import pytest
from unittest.mock import patch, MagicMock

from src.aws_executor import AWSExecutor


@pytest.fixture
def executor():
    return AWSExecutor()


def test_dry_run_returns_success(executor):
    result = executor.execute("aws ec2 describe-instances", dry_run=True)
    assert result["success"] is True


def test_dry_run_output_contains_command(executor):
    cmd = "aws ec2 describe-instances"
    result = executor.execute(cmd, dry_run=True)
    assert cmd in result["output"]
    assert "[DRY RUN]" in result["output"]


def test_dry_run_no_error(executor):
    result = executor.execute("aws s3 ls", dry_run=True)
    assert result["error"] is None


def test_successful_command(executor):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "instance-id: i-123456"
    mock_result.stderr = ""

    with patch('src.aws_executor.subprocess.run', return_value=mock_result):
        result = executor.execute("aws ec2 describe-instances")

    assert result["success"] is True
    assert "instance-id" in result["output"]


def test_failed_command(executor):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "An error occurred (InvalidAMIID.NotFound)"

    with patch('src.aws_executor.subprocess.run', return_value=mock_result):
        result = executor.execute("aws ec2 run-instances --image-id bad-id")

    assert result["success"] is False
    assert "InvalidAMIID.NotFound" in result["error"]


def test_exception_during_execution(executor):
    with patch('src.aws_executor.subprocess.run', side_effect=OSError("command not found")):
        result = executor.execute("aws ec2 describe-instances")

    assert result["success"] is False
    assert "command not found" in result["error"]
