"""
Action Mapper for BharatDeploy
Parses Groq JSON responses into validated AWS CLI commands
"""

import re
import shlex
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# AWS CLI commands that are considered destructive
DESTRUCTIVE_PATTERNS = [
    r"ec2\s+terminate-instances",
    r"ec2\s+delete-",
    r"s3\s+rb\s+",
    r"s3\s+rm\s+",
    r"rds\s+delete-",
    r"lambda\s+delete-function",
    r"iam\s+delete-",
    r"cloudformation\s+delete-stack",
    r"ecs\s+delete-",
    r"eks\s+delete-",
    r"dynamodb\s+delete-table",
    r"route53\s+delete-",
]

# Allowed AWS CLI service prefixes
ALLOWED_SERVICES = {
    "ec2", "s3", "rds", "lambda", "ecs", "eks", "iam",
    "cloudformation", "dynamodb", "route53", "elasticbeanstalk",
    "autoscaling", "elb", "elbv2", "cloudwatch", "logs",
    "secretsmanager", "ssm", "sts", "ecr", "sns", "sqs",
}

# Commands that should NEVER be executed
BLOCKED_COMMANDS = [
    "aws iam delete-user",
    "aws iam delete-role",
    "aws s3 rb --force",
    "aws ec2 terminate-instances --instance-ids",  # Require explicit confirmation
]


class ActionMapperError(Exception):
    """Raised when action mapping fails."""
    pass


class MappedAction:
    """Represents a mapped AWS action ready for execution."""

    def __init__(
        self,
        action: str,
        resource_type: str,
        resource_name: Optional[str],
        aws_commands: list,
        is_destructive: bool,
        confidence: float,
        explanation_hindi: str,
        raw_response: dict,
    ):
        self.action = action
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.aws_commands = aws_commands
        self.is_destructive = is_destructive
        self.confidence = confidence
        self.explanation_hindi = explanation_hindi
        self.raw_response = raw_response

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "aws_commands": self.aws_commands,
            "is_destructive": self.is_destructive,
            "confidence": self.confidence,
            "explanation_hindi": self.explanation_hindi,
        }

    def generate_bash_script(self) -> str:
        """Generate a bash script for the mapped commands."""
        lines = [
            "#!/bin/bash",
            "# BharatDeploy Generated Script",
            f"# Action: {self.action}",
            f"# Resource: {self.resource_type} - {self.resource_name or 'N/A'}",
            "",
            "set -e  # Exit on error",
            "",
        ]

        if self.is_destructive:
            lines.extend([
                '# WARNING: This script contains destructive operations!',
                '# Review carefully before executing.',
                "",
            ])

        for cmd in self.aws_commands:
            lines.append(f"{cmd}")

        return "\n".join(lines) + "\n"


def map_action(groq_response: dict) -> MappedAction:
    """
    Map a Groq JSON response to a validated MappedAction.

    Args:
        groq_response: Parsed JSON response from Groq

    Returns:
        MappedAction with validated AWS commands

    Raises:
        ActionMapperError: If response is invalid or commands are unsafe
    """
    if not groq_response or not isinstance(groq_response, dict):
        raise ActionMapperError("Invalid Groq response: expected a JSON object")

    # Extract fields with defaults
    action = groq_response.get("action", "deploy")
    resource_type = groq_response.get("resource_type", "unknown")
    resource_name = groq_response.get("resource_name")
    raw_commands = groq_response.get("aws_commands", [])
    confidence = float(groq_response.get("confidence", 0.5))
    explanation_hindi = groq_response.get(
        "explanation_hindi", "AWS command tayar hai."
    )

    # Validate and sanitize commands
    validated_commands = []
    is_destructive = False

    for cmd in raw_commands:
        if not cmd or not isinstance(cmd, str):
            continue

        cmd = cmd.strip()

        # Ensure command starts with 'aws'
        if not cmd.startswith("aws "):
            if cmd.startswith("aws"):
                cmd = "aws " + cmd[3:].lstrip()
            else:
                cmd = "aws " + cmd

        # Validate command structure
        try:
            _validate_command(cmd)
        except ActionMapperError as e:
            logger.warning(f"Skipping invalid command: {cmd} - {e}")
            continue

        # Check if destructive
        if _is_destructive_command(cmd):
            is_destructive = True

        validated_commands.append(cmd)

    # Also check if action type indicates destructive operation
    if action in ("delete", "terminate", "remove"):
        is_destructive = True

    if not validated_commands and action not in ("explain",):
        raise ActionMapperError(
            f"No valid AWS commands found in Groq response for action: {action}"
        )

    return MappedAction(
        action=action,
        resource_type=resource_type,
        resource_name=resource_name,
        aws_commands=validated_commands,
        is_destructive=is_destructive,
        confidence=confidence,
        explanation_hindi=explanation_hindi,
        raw_response=groq_response,
    )


def _validate_command(command: str) -> None:
    """
    Validate that an AWS CLI command is safe to execute.

    Args:
        command: AWS CLI command string

    Raises:
        ActionMapperError: If command is invalid or unsafe
    """
    # Basic structure check
    parts = command.split()
    if len(parts) < 3:
        raise ActionMapperError(f"Command too short: {command}")

    if parts[0] != "aws":
        raise ActionMapperError(f"Command must start with 'aws': {command}")

    # Check service is allowed
    service = parts[1]
    if service not in ALLOWED_SERVICES:
        raise ActionMapperError(f"Unsupported AWS service: {service}")

    # Check for shell injection attempts
    dangerous_chars = [";", "&&", "||", "`", "$(",  "|", ">", "<", "$("]
    for char in dangerous_chars:
        if char in command:
            raise ActionMapperError(f"Potentially unsafe character '{char}' in command")

    # Check for blocked commands
    for blocked in BLOCKED_COMMANDS:
        if command.startswith(blocked):
            raise ActionMapperError(f"Command is blocked for safety: {blocked}")


def _is_destructive_command(command: str) -> bool:
    """
    Check if a command is destructive (delete/terminate/remove).

    Args:
        command: AWS CLI command string

    Returns:
        True if command is destructive
    """
    command_lower = command.lower()
    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command_lower):
            return True
    return False


def format_commands_for_display(mapped_action: MappedAction, dry_run: bool = False) -> str:
    """
    Format mapped commands for display to the user.

    Args:
        mapped_action: The MappedAction to display
        dry_run: Whether to add --dry-run flag

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append(f"Action: {mapped_action.action.upper()}")
    lines.append(f"Resource: {mapped_action.resource_type}")
    if mapped_action.resource_name:
        lines.append(f"Name: {mapped_action.resource_name}")
    lines.append(f"Confidence: {mapped_action.confidence:.0%}")

    if mapped_action.is_destructive:
        lines.append("\n⚠️  WARNING: This is a destructive operation!")

    if dry_run:
        lines.append("\n[DRY RUN MODE - Commands will NOT be executed]")

    lines.append("\nCommands to execute:")
    for i, cmd in enumerate(mapped_action.aws_commands, 1):
        display_cmd = cmd
        if dry_run and "ec2" in cmd and "--dry-run" not in cmd:
            display_cmd = cmd + " --dry-run"
        lines.append(f"  {i}. {display_cmd}")

    lines.append(f"\nExplanation: {mapped_action.explanation_hindi}")

    return "\n".join(lines)
