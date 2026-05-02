"""
AWS Executor for BharatDeploy
Executes validated AWS CLI commands safely
"""

import subprocess
import shlex
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AWSExecutorError(Exception):
    """Raised when AWS command execution fails."""
    pass


class CommandResult:
    """Result of an AWS CLI command execution."""

    def __init__(
        self,
        command: str,
        return_code: int,
        stdout: str,
        stderr: str,
        dry_run: bool = False,
    ):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.dry_run = dry_run
        self.success = return_code == 0

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "dry_run": self.dry_run,
            "success": self.success,
        }

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"CommandResult({status}, rc={self.return_code})"


class AWSExecutor:
    """Executes AWS CLI commands with safety checks."""

    def __init__(self, dry_run: bool = False, timeout: int = 30, region: Optional[str] = None):
        """
        Initialize the AWS executor.

        Args:
            dry_run: If True, commands are printed but not executed
            timeout: Command timeout in seconds
            region: AWS region override
        """
        self.dry_run = dry_run
        self.timeout = timeout
        self.region = region

    def execute(self, command: str) -> CommandResult:
        """
        Execute a single AWS CLI command.

        Args:
            command: AWS CLI command string

        Returns:
            CommandResult with output and status
        """
        # Add region flag if specified
        command = self._inject_region(command)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {command}")
            return CommandResult(
                command=command,
                return_code=0,
                stdout=f"[DRY RUN] Command not executed: {command}",
                stderr="",
                dry_run=True,
            )

        try:
            logger.info(f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return CommandResult(
                command=command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                dry_run=False,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Command timed out after {self.timeout} seconds",
                dry_run=False,
            )
        except Exception as e:
            return CommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=str(e),
                dry_run=False,
            )

    def execute_many(self, commands: list) -> list:
        """
        Execute multiple AWS CLI commands in sequence.

        Args:
            commands: List of AWS CLI command strings

        Returns:
            List of CommandResult objects
        """
        results = []
        for command in commands:
            result = self.execute(command)
            results.append(result)
            # Stop on first failure unless in dry_run mode
            if not result.success and not self.dry_run:
                logger.warning(f"Command failed, stopping execution: {command}")
                break
        return results

    def _inject_region(self, command: str) -> str:
        """Add --region flag to command if region is set and not already present."""
        if self.region and "--region" not in command:
            # Insert region after the service subcommand
            parts = command.split()
            if len(parts) >= 3:
                parts.insert(3, f"--region {self.region}")
                return " ".join(parts)
        return command

    def check_aws_credentials(self) -> bool:
        """
        Check if AWS credentials are configured.

        Returns:
            True if credentials are valid, False otherwise
        """
        result = self.execute("aws sts get-caller-identity")
        return result.success

    def get_current_region(self) -> str:
        """Get the current AWS region."""
        result = self.execute("aws configure get region")
        if result.success and result.stdout.strip():
            return result.stdout.strip()
        return self.region or "ap-south-1"
