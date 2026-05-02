"""
Tests for AWS Executor module (all mocked - no real AWS calls)
"""

import pytest
from unittest.mock import MagicMock, patch

from src.aws_executor import AWSExecutor, CommandResult, AWSExecutorError


class TestCommandResult:
    def test_success_result(self):
        result = CommandResult(
            command="aws ec2 describe-instances",
            return_code=0,
            stdout='{"Reservations": []}',
            stderr="",
        )
        assert result.success is True
        assert result.return_code == 0

    def test_failure_result(self):
        result = CommandResult(
            command="aws ec2 describe-instances",
            return_code=1,
            stdout="",
            stderr="An error occurred (UnauthorizedOperation)",
        )
        assert result.success is False
        assert result.return_code == 1

    def test_to_dict(self):
        result = CommandResult(
            command="aws s3 ls",
            return_code=0,
            stdout="my-bucket",
            stderr="",
        )
        d = result.to_dict()
        assert d["command"] == "aws s3 ls"
        assert d["return_code"] == 0
        assert d["stdout"] == "my-bucket"
        assert d["success"] is True
        assert d["dry_run"] is False

    def test_dry_run_result(self):
        result = CommandResult(
            command="aws ec2 run-instances",
            return_code=0,
            stdout="[DRY RUN] Not executed",
            stderr="",
            dry_run=True,
        )
        assert result.dry_run is True
        assert result.success is True

    def test_repr(self):
        result = CommandResult("aws s3 ls", 0, "", "")
        assert "SUCCESS" in repr(result)

    def test_repr_failed(self):
        result = CommandResult("aws s3 ls", 1, "", "error")
        assert "FAILED" in repr(result)


class TestAWSExecutorInit:
    def test_default_init(self):
        executor = AWSExecutor()
        assert executor.dry_run is False
        assert executor.timeout == 30
        assert executor.region is None

    def test_custom_init(self):
        executor = AWSExecutor(dry_run=True, timeout=60, region="us-east-1")
        assert executor.dry_run is True
        assert executor.timeout == 60
        assert executor.region == "us-east-1"


class TestAWSExecutorDryRun:
    def test_dry_run_does_not_execute(self):
        executor = AWSExecutor(dry_run=True)
        with patch("subprocess.run") as mock_run:
            result = executor.execute("aws ec2 describe-instances")
        mock_run.assert_not_called()

    def test_dry_run_returns_success(self):
        executor = AWSExecutor(dry_run=True)
        result = executor.execute("aws ec2 describe-instances")
        assert result.success is True
        assert result.dry_run is True
        assert "DRY RUN" in result.stdout

    def test_dry_run_includes_command_in_output(self):
        executor = AWSExecutor(dry_run=True)
        result = executor.execute("aws s3 ls")
        assert "aws s3 ls" in result.stdout


class TestAWSExecutorExecute:
    def test_successful_command(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"Reservations": []}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            executor = AWSExecutor()
            result = executor.execute("aws ec2 describe-instances")

        assert result.success is True
        assert result.stdout == '{"Reservations": []}'

    def test_failed_command(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "An error occurred (AccessDenied)"

        with patch("subprocess.run", return_value=mock_result):
            executor = AWSExecutor()
            result = executor.execute("aws ec2 describe-instances")

        assert result.success is False
        assert "AccessDenied" in result.stderr

    def test_timeout_returns_failure(self):
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
            executor = AWSExecutor(timeout=30)
            result = executor.execute("aws ec2 describe-instances")

        assert result.success is False
        assert "timed out" in result.stderr.lower()

    def test_exception_returns_failure(self):
        with patch("subprocess.run", side_effect=Exception("Connection refused")):
            executor = AWSExecutor()
            result = executor.execute("aws ec2 describe-instances")

        assert result.success is False
        assert "Connection refused" in result.stderr

    def test_region_injected_when_set(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            executor = AWSExecutor(region="ap-south-1")
            executor.execute("aws ec2 describe-instances")

        call_args = mock_run.call_args[0][0]
        assert "ap-south-1" in call_args

    def test_region_not_injected_when_already_present(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        original_cmd = "aws ec2 describe-instances --region us-east-1"
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            executor = AWSExecutor(region="ap-south-1")
            executor.execute(original_cmd)

        call_args = mock_run.call_args[0][0]
        # Should not duplicate region
        assert call_args.count("--region") == 1


class TestAWSExecutorExecuteMany:
    def test_executes_all_commands(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""

        commands = [
            "aws ec2 describe-instances",
            "aws s3 ls",
            "aws lambda list-functions",
        ]

        with patch("subprocess.run", return_value=mock_result):
            executor = AWSExecutor()
            results = executor.execute_many(commands)

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_stops_on_first_failure(self):
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stdout = ""
        success_result.stderr = ""

        failure_result = MagicMock()
        failure_result.returncode = 1
        failure_result.stdout = ""
        failure_result.stderr = "error"

        commands = [
            "aws ec2 describe-instances",
            "aws s3 broken-command",
            "aws lambda list-functions",
        ]

        with patch("subprocess.run", side_effect=[success_result, failure_result]):
            executor = AWSExecutor()
            results = executor.execute_many(commands)

        # Should stop after the failure
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False

    def test_dry_run_executes_all_despite_failure(self):
        executor = AWSExecutor(dry_run=True)
        commands = ["aws ec2 describe-instances", "aws s3 ls", "aws lambda list-functions"]
        results = executor.execute_many(commands)
        assert len(results) == 3

    def test_empty_commands_list(self):
        executor = AWSExecutor()
        results = executor.execute_many([])
        assert results == []


class TestAWSExecutorCheckCredentials:
    def test_valid_credentials(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"UserId": "AIDAI3UMFASDF", "Account": "123456789"}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            executor = AWSExecutor()
            assert executor.check_aws_credentials() is True

    def test_invalid_credentials(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "InvalidClientTokenId"

        with patch("subprocess.run", return_value=mock_result):
            executor = AWSExecutor()
            assert executor.check_aws_credentials() is False
