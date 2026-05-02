#!/usr/bin/env python3
"""
BharatDeploy Demo Script
========================
Demonstrates the full flow with mocked Groq responses.
No real API keys or AWS credentials required.
"""

import json
from unittest.mock import MagicMock, patch

from src.action_mapper import ActionMapper
from src.aws_executor import AWSExecutor
from src.config import ConfigHandler
from src.error_explainer import ErrorExplainer
from src.groq_handler import GroqHandler
from src.lang_detector import LanguageDetector
from src.prompt_packager import PromptPackager


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_language_detection() -> None:
    separator("MODULE 1 — Language Detection")
    detector = LanguageDetector()

    samples = [
        "banao ek EC2 instance",
        "deploy karo mera flask app",
        "create a new S3 bucket",
        "नमस्ते, मुझे एक instance चाहिए",
        "hatao yeh server please",
    ]

    for text in samples:
        result = detector.detect_language(text)
        print(
            f"  Input   : {text!r}\n"
            f"  Language: {result['language']!r}  "
            f"Confidence: {result['confidence']}  "
            f"Hinglish: {result['is_hinglish']}\n"
        )


def demo_prompt_packager() -> None:
    separator("MODULE 3 — Prompt Packager")
    packager = PromptPackager()

    prompt = packager.package_deploy_prompt("banao ek flask app", "hi")
    print("Deploy prompt (first 300 chars):")
    print(prompt[:300])


def demo_groq_handler() -> None:
    separator("MODULE 4 — Groq Handler (Mocked)")

    mock_response_data = {
        "action": "deploy",
        "confidence": 0.95,
        "aws_command": (
            "aws ec2 run-instances --image-id ami-0abcdef1234567890 "
            "--instance-type t3.micro --count 1"
        ),
        "explanation": "Launch a new EC2 instance with t3.micro in ap-south-1",
        "parameters": {"instance_type": "t3.micro"},
    }

    with patch('src.groq_handler.Groq') as mock_groq_class:
        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response_data)

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq_class.return_value = mock_client

        handler = GroqHandler("demo_key")
        result = handler.parse_command("deploy flask app")

    print("Parsed response from Groq:")
    for k, v in result.items():
        print(f"  {k}: {v}")


def demo_action_mapper() -> None:
    separator("MODULE 5 — Action Mapper")
    mapper = ActionMapper()

    cases = [
        {
            "action": "deploy",
            "aws_command": "aws ec2 run-instances",
            "confidence": 0.95,
            "explanation": "Launch EC2 instance",
        },
        {
            "action": "delete",
            "aws_command": "aws ec2 terminate-instances --instance-ids i-123",
            "confidence": 0.9,
            "explanation": "Terminate EC2 instance",
        },
        {
            "action": "list",
            "aws_command": "aws ec2 describe-instances",
            "confidence": 0.6,
            "explanation": "List all EC2 instances",
        },
    ]

    for case in cases:
        result = mapper.map_action(case)
        print(
            f"  Action   : {case['action']!r}\n"
            f"  Destructive: {result['is_destructive']}  "
            f"Requires confirmation: {result['requires_confirmation']}\n"
        )


def demo_aws_executor() -> None:
    separator("MODULE 6 — AWS Executor (Dry Run)")
    executor = AWSExecutor()

    commands = [
        "aws ec2 describe-instances --region ap-south-1",
        "aws s3 ls",
        "aws ec2 run-instances --image-id ami-0abcdef1234567890 --instance-type t3.micro",
    ]

    for cmd in commands:
        result = executor.execute(cmd, dry_run=True)
        print(f"  Command: {cmd[:60]}...")
        print(f"  Output : {result['output']}\n")


def demo_error_explainer() -> None:
    separator("MODULE 7 — Error Explainer")
    explainer = ErrorExplainer()

    errors = [
        "An error occurred (InvalidAMIID.NotFound): ...",
        "An error occurred (UnauthorizedOperation): ...",
        "An error occurred (InsufficientInstanceCapacity): ...",
        "An error occurred (SomethingElseEntirely): ...",
    ]

    for error in errors:
        explanation = explainer.explain_error(error)
        print(f"  Error      : {error[:60]}...")
        print(f"  Explanation: {explanation}\n")


def demo_config_handler() -> None:
    separator("MODULE 8 — Config Handler")
    handler = ConfigHandler()
    config = handler.load_config("config/bharat.yaml.example")
    print("Loaded config:")
    for k, v in config.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    print("\n🇮🇳  BharatDeploy — End-to-End Demo")
    print("    Multi-language DevOps CLI Agent for AWS\n")

    demo_language_detection()
    demo_prompt_packager()
    demo_groq_handler()
    demo_action_mapper()
    demo_aws_executor()
    demo_error_explainer()
    demo_config_handler()

    print("\n✅  Demo complete!\n")
