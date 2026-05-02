"""
Groq Handler for BharatDeploy
Integrates with Groq API using LLaMA model for structured JSON responses
"""

import json
import time
import logging
from typing import Optional

try:
    from groq import Groq, APIError, APIConnectionError, RateLimitError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from src.config import get_config

logger = logging.getLogger(__name__)


class GroqHandlerError(Exception):
    """Raised when Groq API calls fail after all retries."""
    pass


class GroqHandler:
    """Handler for Groq API interactions with retry logic."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Groq handler.

        Args:
            api_key: Groq API key. If None, loads from config/environment.
            model: LLM model name. If None, uses config default.
        """
        config = get_config()
        self.api_key = api_key or config.get_groq_api_key()
        self.model = model or config.get_groq_model()
        self.max_retries = config.get("groq", "max_retries", default=3)
        self.retry_delay = config.get("groq", "retry_delay", default=1.0)
        self.temperature = config.get("groq", "temperature", default=0.1)
        self.max_tokens = config.get("groq", "max_tokens", default=1024)

        self._client = None
        if GROQ_AVAILABLE and self.api_key:
            self._client = Groq(api_key=self.api_key)

    def _get_client(self) -> "Groq":
        """Get or validate the Groq client."""
        if not GROQ_AVAILABLE:
            raise GroqHandlerError(
                "groq package not installed. Run: pip install groq"
            )
        if not self.api_key:
            raise GroqHandlerError(
                "GROQ_API_KEY not set. Add it to .env or set the environment variable."
            )
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def call(self, messages: list, action: Optional[str] = None) -> dict:
        """
        Call the Groq API with retry logic and return parsed JSON.

        Args:
            messages: List of message dicts (system + user messages)
            action: Optional action hint for logging

        Returns:
            Parsed JSON response as dictionary

        Raises:
            GroqHandlerError: If all retries fail
        """
        client = self._get_client()
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Groq API call attempt {attempt}/{self.max_retries}")

                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                )

                raw_content = response.choices[0].message.content
                logger.debug(f"Raw Groq response: {raw_content}")

                parsed = self._parse_json_response(raw_content)
                parsed["_metadata"] = {
                    "model": self.model,
                    "attempt": attempt,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    } if response.usage else {},
                }
                return parsed

            except (ValueError, json.JSONDecodeError) as e:
                last_error = e
                logger.warning(f"JSON parse error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)

            except Exception as e:
                last_error = e
                # Check for rate limit errors
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}")
                    if attempt < self.max_retries:
                        time.sleep(wait_time)
                elif "connection" in error_str or "timeout" in error_str:
                    logger.warning(f"Connection error on attempt {attempt}: {e}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * attempt)
                else:
                    # Don't retry on auth errors or other permanent failures
                    raise GroqHandlerError(f"Groq API error: {e}") from e

        raise GroqHandlerError(
            f"Groq API failed after {self.max_retries} attempts. Last error: {last_error}"
        )

    def _parse_json_response(self, content: str) -> dict:
        """
        Parse JSON from Groq response content.

        Args:
            content: Raw string content from LLM

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If content cannot be parsed as JSON
        """
        if not content or not content.strip():
            raise ValueError("Empty response from Groq API")

        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from Groq: {e}\nContent: {content[:200]}") from e

    def get_model_info(self) -> dict:
        """Return information about the configured model."""
        return {
            "model": self.model,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "client_ready": self._client is not None,
        }
