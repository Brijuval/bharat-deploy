"""
Prompt Packager for BharatDeploy.

Formats user input together with detected language metadata into a
structured prompt that can be sent to the Groq LLM.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# System prompt shared across all operations
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """You are BharatDeploy, an expert AWS DevOps assistant that understands
commands in Hindi, Hinglish (Roman-script Hindi), and English.

Your job is to convert the user's natural-language request into a precise AWS CLI
command and return a JSON response with the following schema:

{
  "action": "<aws_service>_<operation>",   // e.g. "ec2_create_instance"
  "service": "<aws_service>",              // e.g. "ec2", "s3", "rds"
  "operation": "<operation>",              // e.g. "create", "delete", "list"
  "aws_cli_command": "<full aws cli cmd>", // e.g. "aws ec2 run-instances ..."
  "parameters": { ... },                  // key/value pairs for the command
  "is_destructive": true | false,         // whether command deletes/modifies resources
  "confirmation_required": true | false,  // should user confirm before executing
  "explanation_hi": "<Hindi explanation>", // what you are about to do, in Hindi
  "explanation_en": "<English explanation>",
  "confidence": 0.0-1.0                   // how confident you are in the mapping
}

Rules:
- ALWAYS respond with valid JSON only, no markdown fences.
- If the request is ambiguous, set confidence < 0.5 and ask for clarification in explanation_hi.
- Mark destructive operations (delete, terminate, drop) with "is_destructive": true.
- For destructive operations always set "confirmation_required": true.
- Use ap-south-1 (Mumbai) as the default AWS region unless specified.
- Be concise but accurate in the explanations.
"""

# ---------------------------------------------------------------------------
# Per-language instruction snippets appended to the user message
# ---------------------------------------------------------------------------
_LANGUAGE_HINTS: Dict[str, str] = {
    "hi": "The user wrote in Hindi (Devanagari). Respond with explanation_hi in Hindi.",
    "hinglish": (
        "The user wrote in Hinglish (Roman-script Hindi). "
        "Respond with explanation_hi in easy Hindi or Hinglish."
    ),
    "en": "The user wrote in English. You may keep explanation_hi brief.",
}


class PromptPackager:
    """Packages user input + language metadata into a structured LLM prompt."""

    def package(
        self,
        user_input: str,
        lang_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return a dict with ``system`` and ``user`` message strings.

        Parameters
        ----------
        user_input:
            Raw text from the user.
        lang_result:
            Output from :func:`~src.lang_detector.detect_language`.
        context:
            Optional extra context (e.g. current AWS region, account ID).
        """
        language = str(lang_result.get("language", "en"))
        lang_hint = _LANGUAGE_HINTS.get(language, _LANGUAGE_HINTS["en"])

        # Build context block
        ctx_lines: List[str] = []
        if context:
            if context.get("aws_region"):
                ctx_lines.append(f"AWS Region: {context['aws_region']}")
            if context.get("account_id"):
                ctx_lines.append(f"AWS Account: {context['account_id']}")

        context_block = ""
        if ctx_lines:
            context_block = "\n\nContext:\n" + "\n".join(ctx_lines)

        user_message = (
            f"{lang_hint}\n\n"
            f"User request: {user_input}"
            f"{context_block}"
        )

        return {
            "system": _SYSTEM_PROMPT.strip(),
            "user": user_message,
        }

    def get_system_prompt(self) -> str:
        """Return just the system prompt (useful for testing)."""
        return _SYSTEM_PROMPT.strip()
