"""
BharatDeploy CLI
Multi-language DevOps agent - Deploy to AWS in Hindi!

Commands: deploy, list, delete, explain
"""

import sys
import click
import json
import logging

from src.lang_detector import detect_language, get_hinglish_action
from src.prompt_packager import package_prompt, package_error_prompt
from src.groq_handler import GroqHandler, GroqHandlerError
from src.action_mapper import map_action, format_commands_for_display, ActionMapperError
from src.aws_executor import AWSExecutor, CommandResult
from src.error_explainer import explain_error, format_error_for_display
from src.config import get_config

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging level."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.group()
@click.version_option(version="0.1.0", prog_name="BharatDeploy")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """
    🇮🇳 BharatDeploy - AWS CLI Agent for Indian Developers

    Deploy to AWS in Hindi, Hinglish, or English!

    \b
    Examples:
      bharat deploy "flask app banao"
      bharat list --language hi
      bharat delete "purana server hatao"
      bharat explain "S3 bucket kya hota hai"
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@cli.command()
@click.argument("description")
@click.option("--language", "-l", default=None,
              type=click.Choice(["hi", "ta", "kn", "en", "hinglish", "auto"]),
              help="Override language detection")
@click.option("--dry-run", is_flag=True, help="Show commands without executing")
@click.option("--confirm/--no-confirm", default=True,
              help="Ask for confirmation before executing")
@click.pass_context
def deploy(ctx, description, language, dry_run, confirm):
    """
    Deploy an application or resource to AWS.

    \b
    Examples:
      bharat deploy "flask app banao"
      bharat deploy "create an EC2 instance"
      bharat deploy "Lambda function deploy karo"
    """
    _execute_action(ctx, description, "deploy", language, dry_run, confirm)


@cli.command(name="list")
@click.argument("description", default="all resources")
@click.option("--language", "-l", default=None,
              type=click.Choice(["hi", "ta", "kn", "en", "hinglish", "auto"]),
              help="Override language detection")
@click.option("--output", "-o", default="table",
              type=click.Choice(["table", "json", "text"]),
              help="Output format")
@click.pass_context
def list_resources(ctx, description, language, output):
    """
    List AWS resources.

    \b
    Examples:
      bharat list
      bharat list "EC2 instances dikhao"
      bharat list "S3 buckets"
    """
    _execute_action(ctx, description, "list", language, dry_run=False, confirm=False)


@cli.command()
@click.argument("description")
@click.option("--language", "-l", default=None,
              type=click.Choice(["hi", "ta", "kn", "en", "hinglish", "auto"]),
              help="Override language detection")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete(ctx, description, language, force):
    """
    Delete an AWS resource.

    \b
    Examples:
      bharat delete "purana EC2 instance hatao"
      bharat delete "test bucket delete karo"
    """
    _execute_action(ctx, description, "delete", language, dry_run=False, confirm=not force)


@cli.command()
@click.argument("topic")
@click.option("--language", "-l", default=None,
              type=click.Choice(["hi", "ta", "kn", "en", "hinglish", "auto"]),
              help="Override language detection")
@click.pass_context
def explain(ctx, topic, language):
    """
    Explain an AWS concept in Hindi.

    \b
    Examples:
      bharat explain "S3 bucket kya hota hai"
      bharat explain "EC2 vs Lambda"
      bharat explain "What is a VPC?"
    """
    _execute_action(ctx, topic, "explain", language, dry_run=False, confirm=False)


def _execute_action(ctx, description: str, action: str, language_override,
                    dry_run: bool, confirm: bool):
    """
    Core execution flow for all CLI commands.
    """
    verbose = ctx.obj.get("verbose", False)
    config = get_config()

    # Step 1: Detect language
    if language_override and language_override != "auto":
        lang_result = {
            "language": language_override,
            "language_name": language_override.capitalize(),
            "confidence": 1.0,
            "detected_keywords": [],
        }
    else:
        lang_result = detect_language(description)

    if verbose or dry_run:
        click.echo(f"🔍 Language detected: {lang_result['language_name']} "
                   f"(confidence: {lang_result['confidence']:.0%})")

    # Step 2: Package prompt
    context = {"aws_region": config.get_aws_region()}
    messages = package_prompt(description, lang_result["language"], action, context)

    # Step 3: Call Groq API
    click.echo(f"🤖 Processing your request...")
    try:
        handler = GroqHandler()
        groq_response = handler.call(messages, action)
    except GroqHandlerError as e:
        click.echo(f"❌ Error calling Groq API: {e}", err=True)
        click.echo("\nTip: Make sure GROQ_API_KEY is set in your .env file", err=True)
        sys.exit(1)

    # Handle explain action separately
    if action == "explain":
        _display_explanation(groq_response, verbose)
        return

    # Step 4: Map to AWS commands
    try:
        mapped_action = map_action(groq_response)
    except ActionMapperError as e:
        click.echo(f"❌ Failed to map action: {e}", err=True)
        if verbose:
            click.echo(f"Groq response: {json.dumps(groq_response, indent=2)}", err=True)
        sys.exit(1)

    # Step 5: Display commands
    click.echo("")
    click.echo(format_commands_for_display(mapped_action, dry_run or config.is_dry_run()))
    click.echo("")

    # Step 6: Confirm if needed
    if dry_run or config.is_dry_run():
        click.echo("ℹ️  Dry run mode - no changes made")
        return

    if confirm and mapped_action.is_destructive:
        warning = mapped_action.raw_response.get(
            "warning_hindi", "Yeh operation irreversible ho sakta hai!"
        )
        click.echo(f"⚠️  {warning}")
        if not click.confirm("Kya aap sure hain? (Are you sure?)"):
            click.echo("❌ Operation cancelled / रद्द किया गया")
            return
    elif confirm and len(mapped_action.aws_commands) > 0:
        if not click.confirm("Execute these commands?"):
            click.echo("❌ Operation cancelled")
            return

    # Step 7: Execute
    executor = AWSExecutor(
        dry_run=False,
        timeout=config.get("aws", "timeout", default=30),
        region=config.get_aws_region(),
    )

    click.echo("⚙️  Executing commands...")
    results = executor.execute_many(mapped_action.aws_commands)

    # Step 8: Display results
    for result in results:
        if result.success:
            click.echo(f"✅ {result.command}")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"❌ {result.command}")
            click.echo(f"Error: {result.stderr}", err=True)

            # Explain the error in Hindi
            explanation = explain_error(result.stderr, result.command)
            click.echo("")
            click.echo(format_error_for_display(explanation))


def _display_explanation(groq_response: dict, verbose: bool = False):
    """Display an explanation response from Groq."""
    topic = groq_response.get("topic", "")
    explanation_en = groq_response.get("explanation_english", "")
    explanation_hi = groq_response.get("explanation_hindi", "")
    docs_url = groq_response.get("aws_docs_url", "")

    if topic:
        click.echo(f"\n📚 {topic}")
        click.echo("─" * 50)

    if explanation_hi:
        click.echo(f"\nHindi/Hinglish:\n{explanation_hi}")

    if explanation_en:
        click.echo(f"\nEnglish:\n{explanation_en}")

    if docs_url:
        click.echo(f"\n📖 AWS Docs: {docs_url}")


def main():
    """Entry point for the BharatDeploy CLI."""
    cli()


if __name__ == "__main__":
    main()
