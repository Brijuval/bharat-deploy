from typing import Dict


class ActionMapper:
    DESTRUCTIVE_OPERATIONS = ['delete', 'terminate', 'destroy', 'remove']

    def map_action(self, groq_response: Dict) -> Dict:
        """Parse a Groq response dict and produce an execution-ready action dict."""
        action = groq_response.get('action', '')
        confidence = groq_response.get('confidence', 0)

        is_destructive = any(
            op in action.lower() for op in self.DESTRUCTIVE_OPERATIONS
        )

        return {
            "command": groq_response.get('aws_command', ''),
            "is_destructive": is_destructive,
            "confidence": confidence,
            "requires_confirmation": is_destructive or confidence < 0.75,
            "explanation": groq_response.get('explanation', ''),
        }
