import json
from typing import Dict

from groq import Groq


class GroqHandler:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def parse_command(self, prompt: str) -> Dict:
        """Send a prompt to Groq and return the parsed JSON response."""
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
