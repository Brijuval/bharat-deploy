import os
import sys

import click
from dotenv import load_dotenv

from src.action_mapper import ActionMapper
from src.aws_executor import AWSExecutor
from src.config import ConfigHandler
from src.error_explainer import ErrorExplainer
from src.groq_handler import GroqHandler
from src.lang_detector import LanguageDetector
from src.prompt_packager import PromptPackager

load_dotenv()

detector = LanguageDetector()
packager = PromptPackager()
mapper = ActionMapper()
executor = AWSExecutor()
explainer = ErrorExplainer()
config_handler = ConfigHandler()


def _get_groq_handler() -> GroqHandler:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        click.echo("❌ GROQ_API_KEY environment variable is not set.", err=True)
        sys.exit(1)
    return GroqHandler(api_key)


@click.group()
def cli():
    """BharatDeploy - DevOps in Your Language 🇮🇳"""
    pass


@cli.command()
@click.argument('app_type')
@click.option('--language', default=None, help='Force language (hi/en/ta)')
@click.option('--dry-run', is_flag=True, default=False, help='Preview command without executing')
def deploy(app_type, language, dry_run):
    """Deploy application to AWS."""
    lang_result = detector.detect_language(app_type)
    lang = language or lang_result["language"]

    click.echo(f"🔍 Detected language: {lang}")
    prompt = packager.package_deploy_prompt(app_type, lang)

    groq = _get_groq_handler()
    try:
        groq_response = groq.parse_command(prompt)
    except Exception as e:
        click.echo(f"❌ Error communicating with Groq: {e}", err=True)
        sys.exit(1)

    action = mapper.map_action(groq_response)

    if action["requires_confirmation"]:
        click.echo(f"⚠️  Action requires confirmation: {action['command']}")
        if not click.confirm("क्या आप जारी रखना चाहते हैं? / Do you want to continue?"):
            click.echo("Operation cancelled.")
            return

    result = executor.execute(action["command"], dry_run=dry_run)

    if result["success"]:
        click.echo(f"✅ {result['output']}")
    else:
        error_msg = result.get("error") or ""
        explanation = explainer.explain_error(error_msg, lang)
        click.echo(f"❌ {explanation}", err=True)


@cli.command('list-resources')
@click.option('--language', default=None, help='Force language (hi/en/ta)')
@click.option('--dry-run', is_flag=True, default=False, help='Preview command without executing')
def list_resources(language, dry_run):
    """List AWS resources."""
    user_input = "list all AWS resources"
    lang_result = detector.detect_language(user_input)
    lang = language or lang_result["language"]

    prompt = packager.package_list_prompt(user_input, lang)

    groq = _get_groq_handler()
    try:
        groq_response = groq.parse_command(prompt)
    except Exception as e:
        click.echo(f"❌ Error communicating with Groq: {e}", err=True)
        sys.exit(1)

    action = mapper.map_action(groq_response)
    result = executor.execute(action["command"], dry_run=dry_run)

    if result["success"]:
        click.echo(result["output"])
    else:
        error_msg = result.get("error") or ""
        click.echo(f"❌ {explainer.explain_error(error_msg, lang)}", err=True)


@cli.command()
@click.argument('resource_id')
@click.option('--language', default=None, help='Force language (hi/en/ta)')
@click.option('--dry-run', is_flag=True, default=False, help='Preview command without executing')
def delete(resource_id, language, dry_run):
    """Delete AWS resource."""
    lang_result = detector.detect_language(resource_id)
    lang = language or lang_result["language"]

    prompt = packager.package_delete_prompt(resource_id, lang)

    groq = _get_groq_handler()
    try:
        groq_response = groq.parse_command(prompt)
    except Exception as e:
        click.echo(f"❌ Error communicating with Groq: {e}", err=True)
        sys.exit(1)

    action = mapper.map_action(groq_response)

    # Always confirm destructive operations
    click.echo(f"⚠️  About to delete: {resource_id}")
    click.echo(f"   Command: {action['command']}")
    if not click.confirm("क्या आप sure हैं? / Are you sure?"):
        click.echo("Operation cancelled.")
        return

    result = executor.execute(action["command"], dry_run=dry_run)

    if result["success"]:
        click.echo(f"✅ Resource {resource_id} deleted successfully.")
    else:
        error_msg = result.get("error") or ""
        click.echo(f"❌ {explainer.explain_error(error_msg, lang)}", err=True)


@cli.command()
@click.option('--config-path', default="config/bharat.yaml", help='Path to config file')
def show_config(config_path):
    """Show current configuration."""
    config = config_handler.load_config(config_path)
    click.echo("📋 Current Configuration:")
    for key, value in config.items():
        click.echo(f"  {key}: {value}")


if __name__ == '__main__':
    cli()
