"""
BharatDeploy Demo — End-to-end working example (no real API calls).

Run with:
    python demo.py
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.lang_detector import detect_language
from src.prompt_packager import PromptPackager
from src.action_mapper import ActionMapper
from src.aws_executor import AWSExecutor
from src.error_explainer import ErrorExplainer
from src.config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def _make_mock_groq_response() -> dict:
    return {
        "action": "ec2_describe_instances",
        "service": "ec2",
        "operation": "describe",
        "aws_cli_command": "aws ec2 describe-instances --region ap-south-1",
        "parameters": {"region": "ap-south-1"},
        "is_destructive": False,
        "confirmation_required": False,
        "explanation_hi": "आपकी सभी EC2 instances की जानकारी दिखाई जाएगी।",
        "explanation_en": "Lists all EC2 instances in the ap-south-1 region.",
        "confidence": 0.92,
    }


# ---------------------------------------------------------------------------
# Demo steps
# ---------------------------------------------------------------------------

def demo_language_detection() -> None:
    _print_section("1. Language Detection")

    test_inputs = [
        "EC2 instance banao",                    # Hinglish
        "नमस्ते, मुझे एक S3 bucket चाहिए",       # Hindi
        "create an S3 bucket",                   # English
        "yeh server start karo please",          # Hinglish
        "",                                       # empty
    ]

    for text in test_inputs:
        result = detect_language(text)
        label = text[:40] + "..." if len(text) > 40 else text or "<empty>"
        print(f"  Input : {label!r}")
        print(f"  Result: language={result['language']}, "
              f"confidence={result['confidence']:.2f}, "
              f"is_hinglish={result['is_hinglish']}")
        print()


def demo_prompt_packaging() -> None:
    _print_section("2. Prompt Packaging")

    packager = PromptPackager()
    lang_result = {"language": "hinglish", "confidence": 0.85, "is_hinglish": True}
    prompt = packager.package(
        "EC2 instance banao",
        lang_result,
        context={"aws_region": "ap-south-1"},
    )
    print(f"  System prompt length: {len(prompt['system'])} chars")
    print(f"  User message:\n    {prompt['user']}")


def demo_action_mapping() -> None:
    _print_section("3. Action Mapper (Groq response → AWS command)")

    mapper = ActionMapper()
    groq_response = _make_mock_groq_response()
    action = mapper.map(groq_response)

    print(f"  AWS CLI Command : {action['aws_cli_command']}")
    print(f"  Is Destructive  : {action['is_destructive']}")
    print(f"  Confidence      : {action['confidence']}")
    print(f"  Hindi Explanation: {action['explanation_hi']}")
    print(f"\n  Bash Script:\n---")
    print(action["bash_script"])
    print("---")


def demo_aws_executor_dry_run() -> None:
    _print_section("4. AWS Executor (dry run)")

    executor = AWSExecutor(dry_run=True)
    result = executor.execute("aws ec2 describe-instances --region ap-south-1")

    print(f"  Success  : {result['success']}")
    print(f"  Dry Run  : {result['dry_run']}")
    print(f"  Output   : {result['stdout']}")


def demo_error_explainer() -> None:
    _print_section("5. Error Explainer")

    explainer = ErrorExplainer()
    errors = [
        "AccessDenied: User is not authorized to perform: ec2:RunInstances",
        "Unable to locate credentials",
        "ResourceNotFoundException: Stack does not exist",
        "ThrottlingException: Rate exceeded",
        "Some completely unknown error",
    ]

    for err in errors:
        result = explainer.explain(err)
        print(f"  Error   : {err[:60]}...")
        print(f"  Hindi   : {result['explanation_hi']}")
        print(f"  Fix     : {result['suggestion_hi']}")
        print()


def demo_full_pipeline_mocked() -> None:
    _print_section("6. Full Pipeline (Groq mocked)")

    # Mock only the Groq client so everything else runs for real
    mock_client = MagicMock()
    msg = MagicMock()
    msg.content = json.dumps(_make_mock_groq_response())
    choice = MagicMock()
    choice.message = msg
    mock_client.chat.completions.create.return_value = MagicMock(choices=[choice])

    config = Config()
    packager = PromptPackager()
    mapper = ActionMapper()
    executor = AWSExecutor(dry_run=True)
    explainer = ErrorExplainer()

    user_input = "Meri saari EC2 instances dikhao"
    print(f"  User Input: {user_input!r}")

    # Step 1 – detect language
    lang_result = detect_language(user_input)
    print(f"  Language  : {lang_result['language']} ({lang_result['confidence']:.2f})")

    # Step 2 – package prompt
    prompt = packager.package(user_input, lang_result, context={"aws_region": config.aws_region})

    # Step 3 – call Groq (mocked)
    with patch("groq.Groq", return_value=mock_client):
        from src.groq_handler import GroqHandler
        handler = GroqHandler(api_key="demo-key")
        groq_response = handler.send_prompt(prompt["system"], prompt["user"])

    # Step 4 – map to AWS command
    action = mapper.map(groq_response)
    print(f"  Command   : {action['aws_cli_command']}")

    # Step 5 – execute (dry run)
    result = executor.execute(action["aws_cli_command"])
    status = "✅ Success" if result["success"] else "❌ Failed"
    print(f"  Result    : {status}")
    print(f"  Output    : {result['stdout']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n🇮🇳  BharatDeploy — Demo\n")

    demo_language_detection()
    demo_prompt_packaging()
    demo_action_mapping()
    demo_aws_executor_dry_run()
    demo_error_explainer()
    demo_full_pipeline_mocked()

    print("\n✅ Demo complete! All components working correctly.\n")
