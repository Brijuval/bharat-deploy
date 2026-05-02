"""
Tests for src/aws_executor.py — subprocess calls are mocked.
"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess

from src.aws_executor import AWSExecutor, AWSExecutorError


class TestAWSExecutor:

    # ------------------------------------------------------------------
    # Dry-run mode
    # ------------------------------------------------------------------

    def test_dry_run_does_not_call_subprocess(self):
        executor = AWSExecutor(dry_run=True)
        with patch("subprocess.run") as mock_run:
            result = executor.execute("aws ec2 describe-instances")
            mock_run.assert_not_called()

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "DRY RUN" in result["stdout"]

    def test_dry_run_returns_command(self):
        executor = AWSExecutor(dry_run=True)
        result = executor.execute("aws s3 ls")
        assert result["command"] == "aws s3 ls"
        assert result["exit_code"] == 0

    # ------------------------------------------------------------------
    # Successful execution
    # ------------------------------------------------------------------

    def test_successful_execution(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "i-1234567890abcdef0\n"
        mock_result.stderr = ""

        executor = AWSExecutor(dry_run=False)
        with patch("subprocess.run", return_value=mock_result):
            result = executor.execute("aws ec2 describe-instances")

        assert result["success"] is True
        assert result["exit_code"] == 0
        assert "i-1234" in result["stdout"]
        assert result["dry_run"] is False

    def test_failed_command_returns_success_false(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "An error occurred: AccessDenied"

        executor = AWSExecutor(dry_run=False)
        with patch("subprocess.run", return_value=mock_result):
            result = executor.execute("aws ec2 describe-instances")

        assert result["success"] is False
        assert result["exit_code"] == 1
        assert "AccessDenied" in result["stderr"]

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_raises_if_not_starting_with_aws(self):
        executor = AWSExecutor(dry_run=False)
        with pytest.raises(AWSExecutorError, match="Only 'aws' CLI commands"):
            executor.execute("rm -rf /")

    def test_raises_on_aws_cli_not_installed(self):
        executor = AWSExecutor(dry_run=False)
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(AWSExecutorError, match="not installed"):
                executor.execute("aws ec2 describe-instances")

    def test_raises_on_timeout(self):
        executor = AWSExecutor(dry_run=False, timeout=1)
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="aws", timeout=1),
        ):
            with pytest.raises(AWSExecutorError, match="timed out"):
                executor.execute("aws ec2 describe-instances")

    def test_raises_on_malformed_command(self):
        executor = AWSExecutor(dry_run=False)
        # Unclosed quote causes shlex.split to raise
        with pytest.raises(AWSExecutorError):
            executor.execute("aws ec2 describe-instances --filters 'Name=tag:Name")

    # ------------------------------------------------------------------
    # Subprocess is called with the right arguments
    # ------------------------------------------------------------------

    def test_subprocess_called_with_list(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "{}"
        mock_result.stderr = ""

        executor = AWSExecutor(dry_run=False)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            executor.execute("aws s3 ls s3://my-bucket")

        call_args = mock_run.call_args
        tokens = call_args[0][0]
        assert tokens == ["aws", "s3", "ls", "s3://my-bucket"]
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
