"""
AWS Executor for BharatDeploy.

Safely executes validated AWS CLI commands as subprocesses and captures their
output, error streams, and exit codes.
"""

from __future__ import annotations

import logging
import shlex
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AWSExecutorError(Exception):
    """Raised when an AWS CLI command fails or is rejected."""


class AWSExecutor:
    """Executes validated AWS CLI commands.

    Parameters
    ----------
    dry_run:
        When ``True`` the command is *logged but never executed*. Useful for
        previewing what would happen.
    timeout:
        Maximum time in seconds to wait for a command to complete.
    """

    def __init__(self, dry_run: bool = False, timeout: int = 120) -> None:
        self.dry_run = dry_run
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, aws_cli_command: str) -> Dict[str, Any]:
        """Execute *aws_cli_command* and return a result dict.

        Parameters
        ----------
        aws_cli_command:
            The full ``aws …`` command string (already validated).

        Returns
        -------
        dict with keys:
            - ``success``   – bool
            - ``stdout``    – captured standard output (str)
            - ``stderr``    – captured standard error (str)
            - ``exit_code`` – int
            - ``command``   – the command that was run
            - ``dry_run``   – bool
        """
        logger.info("Executing: %s", aws_cli_command)

        if self.dry_run:
            logger.info("[DRY RUN] Would execute: %s", aws_cli_command)
            return {
                "success": True,
                "stdout": f"[DRY RUN] {aws_cli_command}",
                "stderr": "",
                "exit_code": 0,
                "command": aws_cli_command,
                "dry_run": True,
            }

        try:
            tokens: List[str] = shlex.split(aws_cli_command)
        except ValueError as exc:
            raise AWSExecutorError(
                f"Failed to parse command: {exc}"
            ) from exc

        # Safety check: first token must be 'aws'
        if not tokens or tokens[0] != "aws":
            raise AWSExecutorError(
                "Only 'aws' CLI commands are permitted."
            )

        try:
            result = subprocess.run(
                tokens,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError as exc:
            raise AWSExecutorError(
                "AWS CLI is not installed or not on PATH. "
                "Install it from https://aws.amazon.com/cli/"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise AWSExecutorError(
                f"Command timed out after {self.timeout}s: {aws_cli_command}"
            ) from exc

        success = result.returncode == 0
        if not success:
            logger.error(
                "AWS CLI command failed (exit %d): %s",
                result.returncode,
                result.stderr.strip(),
            )

        return {
            "success": success,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "command": aws_cli_command,
            "dry_run": False,
        }
