"""
BharatDeploy Demo Script
Demonstrates core functionality without requiring real API keys.
"""

import json
from src.lang_detector import detect_language, get_hinglish_action
from src.prompt_packager import package_prompt
from src.action_mapper import map_action, format_commands_for_display
from src.aws_executor import AWSExecutor
from src.error_explainer import explain_error, format_error_for_display
from src.config import BharatConfig


def demo_language_detection():
    """Demo: Language detection with various inputs."""
    print("\n" + "=" * 60)
    print("🔍 DEMO 1: Language Detection")
    print("=" * 60)

    test_inputs = [
        "flask app banao",
        "deploy karo mere server ko",
        "नमस्ते, मेरा server बनाओ",
        "create an EC2 instance",
        "EC2 instances dikhao",
        "server hatao purana wala",
        "mera naya S3 bucket banao",
    ]

    for text in test_inputs:
        result = detect_language(text)
        action = get_hinglish_action(text) if result["language"] == "hinglish" else "N/A"
        print(f"\nInput:    '{text}'")
        print(f"Language: {result['language_name']} (confidence: {result['confidence']:.0%})")
        if result["detected_keywords"]:
            print(f"Keywords: {result['detected_keywords']}")
        if action != "N/A":
            print(f"Action:   {action}")


def demo_prompt_packaging():
    """Demo: How prompts are packaged for the LLM."""
    print("\n" + "=" * 60)
    print("📦 DEMO 2: Prompt Packaging")
    print("=" * 60)

    user_input = "flask app banao EC2 pe"
    lang_result = detect_language(user_input)

    print(f"\nUser Input: '{user_input}'")
    print(f"Detected Language: {lang_result['language_name']}")

    messages = package_prompt(
        user_input=user_input,
        language=lang_result["language"],
        action="deploy",
        context={"aws_region": "ap-south-1"},
    )

    print(f"\nSystem Prompt (first 200 chars):")
    print(f"  {messages[0]['content'][:200]}...")
    print(f"\nUser Message:")
    print(f"  {messages[1]['content']}")


def demo_action_mapping():
    """Demo: Mapping simulated Groq responses to AWS commands."""
    print("\n" + "=" * 60)
    print("🗺️  DEMO 3: Action Mapping (Simulated LLM Response)")
    print("=" * 60)

    # Simulate what Groq would return for "flask app banao"
    simulated_groq_response = {
        "action": "deploy",
        "resource_type": "ec2",
        "resource_name": "flask-app",
        "aws_commands": [
            "aws ec2 run-instances --image-id ami-0522ab6e1ddcc7055 --instance-type t2.micro --count 1 --tag-specifications ResourceType=instance,Tags=[{Key=Name,Value=flask-app}]",
            "aws ec2 describe-instances --filters Name=tag:Name,Values=flask-app",
        ],
        "confidence": 0.87,
        "explanation_hindi": "Flask app ke liye EC2 instance t2.micro type ka banaya ja raha hai Mumbai region mein.",
    }

    print(f"\nSimulated Groq Response:")
    print(json.dumps(simulated_groq_response, indent=2, ensure_ascii=False))

    mapped = map_action(simulated_groq_response)

    print(f"\nMapped Action:")
    print(format_commands_for_display(mapped, dry_run=True))

    print(f"\nGenerated Bash Script:")
    print(mapped.generate_bash_script())


def demo_error_explanation():
    """Demo: Hindi error explanations for common AWS errors."""
    print("\n" + "=" * 60)
    print("❌ DEMO 4: Error Explanation in Hindi")
    print("=" * 60)

    errors = [
        ("An error occurred (AccessDenied): User is not authorized", "aws ec2 describe-instances"),
        ("An error occurred (NoSuchBucket): The specified bucket does not exist", "aws s3 ls s3://my-bucket"),
        ("An error occurred (InvalidClientTokenId): The security token included in the request is invalid", "aws ec2 describe-instances"),
    ]

    for error_msg, command in errors:
        print(f"\nCommand:  {command}")
        print(f"Error:    {error_msg[:60]}...")
        explanation = explain_error(error_msg, command)
        print(format_error_for_display(explanation))


def demo_dry_run():
    """Demo: Dry run mode - show commands without executing."""
    print("\n" + "=" * 60)
    print("🔬 DEMO 5: Dry Run Mode")
    print("=" * 60)

    executor = AWSExecutor(dry_run=True)

    commands = [
        "aws ec2 describe-instances",
        "aws s3 ls",
    ]

    print(f"\nExecuting in DRY RUN mode:")
    for cmd in commands:
        result = executor.execute(cmd)
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.stdout}")


def demo_config():
    """Demo: Configuration loading."""
    print("\n" + "=" * 60)
    print("⚙️  DEMO 6: Configuration")
    print("=" * 60)

    config = BharatConfig()

    print(f"\nConfiguration:")
    print(f"  Groq Model:   {config.get_groq_model()}")
    print(f"  AWS Region:   {config.get_aws_region()}")
    print(f"  Dry Run:      {config.is_dry_run()}")
    print(f"  Language:     {config.get_default_language()}")
    print(f"  Confirm Destructive: {config.should_confirm_destructive()}")

    api_key = config.get_groq_api_key()
    if api_key:
        print(f"  Groq API Key: {'*' * 8}...{api_key[-4:]} (set)")
    else:
        print(f"  Groq API Key: Not set (add to .env file)")


def main():
    """Run all demos."""
    print("\n🇮🇳 BharatDeploy - Demo")
    print("Multi-language DevOps CLI Agent for AWS")
    print("Deploy to AWS in Hindi, Hinglish, or English!")

    demo_language_detection()
    demo_prompt_packaging()
    demo_action_mapping()
    demo_error_explanation()
    demo_dry_run()
    demo_config()

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add GROQ_API_KEY to .env file")
    print("2. Run: aws configure")
    print("3. Try: python main.py deploy 'flask app banao'")
    print()


if __name__ == "__main__":
    main()
