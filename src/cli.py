"""
Click CLI Framework for BharatDeploy.

Provides the main ``bharat`` command group with the following subcommands:
  - deploy   : Deploy an application or service
  - list     : List existing AWS resources
  - delete   : Delete an AWS resource
  - explain  : Explain an error in Hindi
"""

from __future__ import annotations

import sys
import logging

import click

from src.lang_detector import detect_language
from src.config import Config
from src.prompt_packager import PromptPackager
from src.groq_handler import GroqHandler, GroqHandlerError
from src.action_mapper import ActionMapper, ActionMapperError
from src.aws_executor import AWSExecutor, AWSExecutorError
from src.error_explainer import ErrorExplainer

logger = logging.getLogger(__name__)


def _get_components(config: Config):
    """Initialise and return all pipeline components."""
    packager = PromptPackager()
    handler = GroqHandler(
        api_key=config.groq_api_key,
        model=config.groq_model,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
    )
    mapper = ActionMapper()
    executor = AWSExecutor(dry_run=config.dry_run)
    explainer = ErrorExplainer()
    return packager, handler, mapper, executor, explainer


def _run_pipeline(
    user_input: str,
    language: str | None,
    config: Config,
    confirm: bool,
) -> None:
    """Core pipeline: detect → package → LLM → map → execute."""
    packager, handler, mapper, executor, explainer = _get_components(config)

    # 1. Language detection
    if language:
        lang_result = {"language": language, "confidence": 1.0, "is_hinglish": language == "hinglish"}
    else:
        lang_result = detect_language(user_input)
        click.echo(f"🔍 Detected language: {lang_result['language']} (confidence: {lang_result['confidence']:.2f})")

    # 2. Package prompt
    prompt = packager.package(user_input, lang_result, context={"aws_region": config.aws_region})

    # 3. Send to Groq
    try:
        click.echo("🤖 Processing with AI...")
        groq_response = handler.send_prompt(prompt["system"], prompt["user"])
    except GroqHandlerError as exc:
        click.secho(f"❌ AI Error: {exc}", fg="red", err=True)
        sys.exit(1)

    # 4. Map to AWS command
    try:
        action = mapper.map(groq_response)
    except ActionMapperError as exc:
        click.secho(f"❌ Command Error: {exc}", fg="red", err=True)
        sys.exit(1)

    # 5. Show explanation
    click.echo(f"\n📝 {action['explanation_hi']}")
    click.echo(f"   {action['explanation_en']}")
    click.echo(f"\n💻 Command: {action['aws_cli_command']}")

    if action["is_destructive"]:
        click.secho("⚠️  यह एक destructive operation है!", fg="yellow")

    # 6. Confirm if required
    if action["confirmation_required"] or (action["is_destructive"] and confirm):
        if not click.confirm("\nक्या आप आगे बढ़ना चाहते हैं? (Continue?)"):
            click.echo("Operation cancelled.")
            return

    # 7. Execute
    try:
        result = executor.execute(action["aws_cli_command"])
    except AWSExecutorError as exc:
        explanation = explainer.explain(str(exc))
        click.secho(f"❌ {explanation['explanation_hi']}", fg="red", err=True)
        click.secho(f"   {explanation['explanation_en']}", fg="red", err=True)
        click.secho(f"💡 {explanation['suggestion_hi']}", fg="yellow", err=True)
        sys.exit(1)

    if result["success"]:
        click.secho("✅ Success!", fg="green")
        if result["stdout"]:
            click.echo(result["stdout"])
    else:
        explanation = explainer.explain(result["stderr"], command=action["aws_cli_command"])
        click.secho(f"❌ {explanation['explanation_hi']}", fg="red", err=True)
        click.secho(f"   {explanation['explanation_en']}", fg="red", err=True)
        click.secho(f"💡 {explanation['suggestion_hi']}", fg="yellow", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------

@click.group()
@click.option("--language", "-l", default=None, help="Force language (hi/en/hinglish)")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without executing")
@click.option("--config-file", default=None, help="Path to bharat.yaml config file")
@click.pass_context
def cli(ctx: click.Context, language: str | None, dry_run: bool, config_file: str | None) -> None:
    """BharatDeploy — AWS deployment commands in Hindi. 🇮🇳"""
    ctx.ensure_object(dict)
    config = Config(config_path=config_file)
    if dry_run:
        config._data["dry_run"] = True
    ctx.obj["config"] = config
    ctx.obj["language"] = language

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(levelname)s: %(message)s",
    )


@cli.command()
@click.argument("request", nargs=-1, required=True)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation")
@click.pass_context
def deploy(ctx: click.Context, request: tuple[str, ...], yes: bool) -> None:
    """Deploy an application or AWS resource.

    REQUEST is the natural-language description, e.g.:
    'Flask app ke liye EC2 instance banao'
    """
    user_input = " ".join(request)
    config: Config = ctx.obj["config"]
    language: str | None = ctx.obj["language"]
    _run_pipeline(user_input, language, config, confirm=not yes)


@cli.command(name="list")
@click.argument("request", nargs=-1, required=True)
@click.pass_context
def list_resources(ctx: click.Context, request: tuple[str, ...]) -> None:
    """List AWS resources.

    REQUEST is the natural-language description, e.g.:
    'Meri saari EC2 instances dikhao'
    """
    user_input = " ".join(request)
    config: Config = ctx.obj["config"]
    language: str | None = ctx.obj["language"]
    _run_pipeline(user_input, language, config, confirm=False)


@cli.command()
@click.argument("request", nargs=-1, required=True)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation")
@click.pass_context
def delete(ctx: click.Context, request: tuple[str, ...], yes: bool) -> None:
    """Delete an AWS resource.

    REQUEST is the natural-language description, e.g.:
    'test-bucket S3 bucket delete karo'
    """
    user_input = " ".join(request)
    config: Config = ctx.obj["config"]
    language: str | None = ctx.obj["language"]
    _run_pipeline(user_input, language, config, confirm=not yes)


@cli.command()
@click.argument("error_message", nargs=-1, required=True)
@click.pass_context
def explain(ctx: click.Context, error_message: tuple[str, ...]) -> None:
    """Explain an AWS error message in Hindi.

    ERROR_MESSAGE is the error text you received, e.g.:
    'AccessDeniedException: User is not authorized to perform: ec2:RunInstances'
    """
    error_text = " ".join(error_message)
    explainer = ErrorExplainer()
    result = explainer.explain(error_text)

    click.echo(f"\n📖 Hindi: {result['explanation_hi']}")
    click.echo(f"📖 English: {result['explanation_en']}")
    click.secho(f"💡 Suggestion: {result['suggestion_hi']}", fg="cyan")
