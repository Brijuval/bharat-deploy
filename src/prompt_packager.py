class PromptPackager:
    def package_deploy_prompt(self, user_input: str, language: str) -> str:
        """Format a deploy prompt for Groq with structured JSON output."""
        return f"""
User language: {language}
User command: {user_input}

Return JSON:
{{
    "action": "deploy|list|delete",
    "parameters": {{}},
    "confidence": 0.0-1.0,
    "aws_command": "aws cli command",
    "explanation": "what this does"
}}
"""

    def package_list_prompt(self, user_input: str, language: str) -> str:
        """Format a list-resources prompt for Groq."""
        return f"""
User language: {language}
User command: {user_input}

Return JSON:
{{
    "action": "list",
    "parameters": {{}},
    "confidence": 0.0-1.0,
    "aws_command": "aws cli command to list resources",
    "explanation": "what this does"
}}
"""

    def package_delete_prompt(self, resource_id: str, language: str) -> str:
        """Format a delete prompt for Groq."""
        return f"""
User language: {language}
Resource to delete: {resource_id}

Return JSON:
{{
    "action": "delete",
    "parameters": {{"resource_id": "{resource_id}"}},
    "confidence": 0.0-1.0,
    "aws_command": "aws cli command to delete resource",
    "explanation": "what this does"
}}
"""
