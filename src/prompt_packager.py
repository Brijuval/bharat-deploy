"""
Prompt Packager for BharatDeploy
Formats user input + language into structured prompts for Groq LLM
"""

from typing import Optional


# Action-specific prompt templates
ACTION_PROMPTS = {
    "deploy": """You are a DevOps assistant that helps Indian developers deploy applications to AWS.
The user wants to DEPLOY something. Extract the deployment details and generate the appropriate AWS CLI commands.

Return a JSON object with:
- action: "deploy"
- resource_type: type of resource (ec2/s3/lambda/ecs/elastic-beanstalk/etc)
- resource_name: name of the resource
- aws_commands: list of AWS CLI command strings
- confidence: confidence score 0.0-1.0
- explanation_hindi: brief explanation in Hindi/Hinglish
- estimated_cost: rough cost estimate if possible""",

    "list": """You are a DevOps assistant that helps Indian developers manage AWS resources.
The user wants to LIST or SHOW resources. Generate the appropriate AWS CLI commands to list resources.

Return a JSON object with:
- action: "list"
- resource_type: type of resource to list (ec2/s3/lambda/etc, or "all")
- aws_commands: list of AWS CLI command strings
- confidence: confidence score 0.0-1.0
- explanation_hindi: brief explanation in Hindi/Hinglish""",

    "delete": """You are a DevOps assistant that helps Indian developers manage AWS resources.
The user wants to DELETE a resource. Generate the appropriate AWS CLI commands.
IMPORTANT: This is a destructive operation. Include safety warnings.

Return a JSON object with:
- action: "delete"
- resource_type: type of resource
- resource_name: name/id of the resource
- aws_commands: list of AWS CLI command strings
- confidence: confidence score 0.0-1.0
- is_destructive: true
- warning_hindi: warning message in Hindi/Hinglish
- explanation_hindi: brief explanation in Hindi/Hinglish""",

    "explain": """You are a DevOps assistant that helps Indian developers understand AWS concepts.
The user wants an EXPLANATION of something AWS-related. Provide a clear explanation.

Return a JSON object with:
- action: "explain"
- topic: the topic being explained
- explanation_english: clear English explanation
- explanation_hindi: explanation in Hindi/Hinglish (mix is fine)
- aws_docs_url: relevant AWS documentation URL if applicable
- confidence: confidence score 0.0-1.0""",

    "default": """You are a DevOps assistant that helps Indian developers with AWS deployments.
Analyze the user's request and determine the appropriate AWS action.

Return a JSON object with:
- action: detected action (deploy/list/delete/explain/status/start/stop)
- resource_type: type of AWS resource
- resource_name: resource name if mentioned
- aws_commands: list of AWS CLI command strings
- confidence: confidence score 0.0-1.0
- explanation_hindi: brief explanation in Hindi/Hinglish""",
}

# Language-specific instruction additions
LANGUAGE_INSTRUCTIONS = {
    "hi": "The user is writing in Hindi (Devanagari script). Understand their request and respond with JSON.",
    "hinglish": "The user is writing in Hinglish (Roman script Hindi mixed with English). Common words: banao=create, karo=do, hatao=delete, dikhao=show, chalao=run. Understand their request and respond with JSON.",
    "ta": "The user is writing in Tamil. Understand their request and respond with JSON.",
    "kn": "The user is writing in Kannada. Understand their request and respond with JSON.",
    "en": "The user is writing in English. Understand their request and respond with JSON.",
}


def package_prompt(
    user_input: str,
    language: str,
    action: Optional[str] = None,
    context: Optional[dict] = None,
) -> list:
    """
    Package user input into a structured prompt for the LLM.

    Args:
        user_input: The user's raw input text
        language: Detected language code (hi/ta/kn/en/hinglish)
        action: Optional action hint (deploy/list/delete/explain)
        context: Optional additional context (aws_region, etc.)

    Returns:
        List of message dicts suitable for Groq API
    """
    # Get action-specific system prompt
    action_key = action if action in ACTION_PROMPTS else "default"
    system_prompt = ACTION_PROMPTS[action_key]

    # Add language-specific instructions
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])
    system_prompt = f"{system_prompt}\n\nLanguage Note: {lang_instruction}"

    # Add context if provided
    if context:
        aws_region = context.get("aws_region", "ap-south-1")
        system_prompt += f"\n\nAWS Context:\n- Region: {aws_region}"
        if context.get("existing_resources"):
            system_prompt += f"\n- Existing resources: {context['existing_resources']}"

    # Add JSON format reminder
    system_prompt += "\n\nIMPORTANT: Always respond with valid JSON only. No markdown, no code blocks, just pure JSON."

    # Build user message
    user_message = _build_user_message(user_input, language, action)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def _build_user_message(user_input: str, language: str, action: Optional[str]) -> str:
    """Build a structured user message."""
    parts = []

    if action:
        parts.append(f"Action: {action}")

    parts.append(f"User Request: {user_input}")
    parts.append(f"Language: {language}")
    parts.append("Please generate the appropriate AWS CLI commands as JSON.")

    return "\n".join(parts)


def package_error_prompt(error_message: str, command: str, language: str = "hi") -> list:
    """
    Package an error explanation prompt.

    Args:
        error_message: The AWS error message
        command: The command that failed
        language: Language for explanation (default: Hindi)

    Returns:
        List of message dicts for Groq API
    """
    system_prompt = """You are a DevOps assistant helping Indian developers understand AWS errors.
Explain the error in simple Hindi/Hinglish that a beginner can understand.

Return a JSON object with:
- error_type: category of error (permission/not-found/quota/network/config/unknown)
- explanation_hindi: clear explanation in Hindi/Hinglish
- fix_steps: list of steps to fix the error (in Hindi/Hinglish)
- aws_docs_url: relevant AWS documentation URL
- confidence: confidence score 0.0-1.0

IMPORTANT: Respond with valid JSON only."""

    user_message = f"""AWS Command Failed:
Command: {command}
Error: {error_message}

Please explain this error in simple Hindi/Hinglish and suggest how to fix it."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
