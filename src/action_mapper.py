"""
Action Mapper for BharatDeploy.

Parses the structured JSON from Groq, validates the generated AWS CLI command
for safety, and produces a ready-to-execute bash script.
"""

from __future__ import annotations

import logging
import re
import shlex
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Safety: list of dangerous sub-commands that require extra confirmation
# ---------------------------------------------------------------------------
_DESTRUCTIVE_PATTERNS: List[str] = [
    r"\bdelete\b",
    r"\bterminate\b",
    r"\bremove\b",
    r"\bdestroy\b",
    r"\bpurge\b",
    r"\bdrop\b",
    r"--force",
    r"--no-dry-run",
    r"rm\s",
]

_ALLOWED_AWS_SERVICES: set[str] = {
    "ec2", "s3", "rds", "lambda", "iam", "vpc", "ecs",
    "eks", "cloudformation", "cloudwatch", "elasticache",
    "elb", "elbv2", "route53", "sns", "sqs", "dynamodb",
    "ssm", "secretsmanager", "acm", "apigateway", "logs",
}


class ActionMapperError(Exception):
    """Raised when the action mapper cannot produce a safe command."""


class ActionMapper:
    """Maps a Groq JSON response to a validated AWS CLI command."""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def map(self, groq_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate *groq_response* and return an enriched action dict.

        Parameters
        ----------
        groq_response:
            JSON dict returned by :class:`~src.groq_handler.GroqHandler`.

        Returns
        -------
        dict with keys:
            - ``aws_cli_command`` – the validated command string
            - ``bash_script``     – a minimal bash script to execute it
            - ``is_destructive``  – bool
            - ``confirmation_required`` – bool
            - ``explanation_hi``  – Hindi explanation
            - ``explanation_en``  – English explanation
            - ``confidence``      – float

        Raises
        ------
        ActionMapperError
            If the command fails validation.
        """
        self._validate_schema(groq_response)

        cmd = groq_response["aws_cli_command"].strip()
        self._validate_command(cmd)

        # Re-evaluate destructiveness in case the LLM missed something
        llm_is_destructive = groq_response.get("is_destructive", False)
        is_destructive = llm_is_destructive or self._is_destructive(cmd)
        # If we upgraded is_destructive, force confirmation_required as well
        if is_destructive and not llm_is_destructive:
            confirmation_required = True
        else:
            confirmation_required = groq_response.get("confirmation_required", is_destructive)

        bash_script = self._generate_bash_script(cmd, groq_response)

        return {
            "aws_cli_command": cmd,
            "bash_script": bash_script,
            "is_destructive": is_destructive,
            "confirmation_required": confirmation_required,
            "explanation_hi": groq_response.get("explanation_hi", ""),
            "explanation_en": groq_response.get("explanation_en", ""),
            "confidence": float(groq_response.get("confidence", 0.0)),
            "action": groq_response.get("action", ""),
            "service": groq_response.get("service", ""),
            "operation": groq_response.get("operation", ""),
        }

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """Ensure required keys are present."""
        required = {"aws_cli_command"}
        missing = required - data.keys()
        if missing:
            raise ActionMapperError(
                f"Groq response is missing required fields: {missing}"
            )

    def _validate_command(self, cmd: str) -> None:
        """Validate that *cmd* is a safe AWS CLI command."""
        if not cmd:
            raise ActionMapperError("aws_cli_command is empty.")

        # Must start with 'aws'
        tokens = shlex.split(cmd)
        if not tokens or tokens[0] != "aws":
            raise ActionMapperError(
                f"Command must start with 'aws', got: {tokens[0]!r}"
            )

        # Service must be in the allow-list
        if len(tokens) < 2:
            raise ActionMapperError("Command must specify an AWS service.")

        service = tokens[1]
        if service not in _ALLOWED_AWS_SERVICES:
            raise ActionMapperError(
                f"AWS service '{service}' is not in the allowed list."
            )

        # Reject shell injection attempts
        _FORBIDDEN_CHARS = [";", "&&", "||", "|", "`", "$(", "${"]
        for char in _FORBIDDEN_CHARS:
            if char in cmd:
                raise ActionMapperError(
                    f"Command contains forbidden character/sequence: {char!r}"
                )

    def _is_destructive(self, cmd: str) -> bool:
        """Return True if *cmd* looks like a destructive operation."""
        lower_cmd = cmd.lower()
        return any(re.search(pat, lower_cmd) for pat in _DESTRUCTIVE_PATTERNS)

    # ------------------------------------------------------------------
    # Script generation
    # ------------------------------------------------------------------

    def _generate_bash_script(
        self,
        cmd: str,
        groq_response: Dict[str, Any],
    ) -> str:
        """Wrap *cmd* in a minimal bash script with comments."""
        explanation_en = groq_response.get("explanation_en", "AWS operation")
        action = groq_response.get("action", "aws_operation")

        lines = [
            "#!/usr/bin/env bash",
            "# Generated by BharatDeploy",
            f"# Action: {action}",
            f"# Description: {explanation_en}",
            "set -euo pipefail",
            "",
            cmd,
        ]
        return "\n".join(lines)
