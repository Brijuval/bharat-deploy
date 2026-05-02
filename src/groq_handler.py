"""
Groq Integration Handler for BharatDeploy.

Sends structured prompts to the Groq API and returns parsed JSON responses.
Implements exponential-backoff retry logic.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GroqHandlerError(Exception):
    """Raised when the Groq handler encounters an unrecoverable error."""


class GroqHandler:
    """Wrapper around the Groq Python SDK.

    Parameters
    ----------
    api_key:
        Groq API key. If omitted, the ``GROQ_API_KEY`` env var is used.
    model:
        Groq model name (default: ``llama3-8b-8192``).
    max_retries:
        Maximum number of retry attempts on transient failures.
    retry_delay:
        Initial delay in seconds between retries (doubled each time).
    """

    DEFAULT_MODEL = "llama3-8b-8192"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.model = model or self.DEFAULT_MODEL
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = self._build_client(api_key)

    # ------------------------------------------------------------------
    # Client construction
    # ------------------------------------------------------------------

    def _build_client(self, api_key: Optional[str]):
        """Initialise and return a Groq client instance."""
        try:
            from groq import Groq

            if api_key:
                return Groq(api_key=api_key)
            # Let the SDK pick up GROQ_API_KEY from the environment
            return Groq()
        except ImportError as exc:
            raise GroqHandlerError(
                "The 'groq' package is not installed. "
                "Run: pip install groq"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_prompt(
        self,
        system_prompt: str,
        user_message: str,
    ) -> Dict[str, Any]:
        """Send a prompt to Groq and return the parsed JSON response.

        Parameters
        ----------
        system_prompt:
            The system-level instruction string.
        user_message:
            The user-facing message string.

        Returns
        -------
        dict
            Parsed JSON object from the LLM response.

        Raises
        ------
        GroqHandlerError
            On authentication errors, invalid JSON, or max retries exceeded.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        last_exc: Optional[Exception] = None
        delay = self.retry_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                raw = response.choices[0].message.content
                return json.loads(raw)

            except json.JSONDecodeError as exc:
                logger.error("Groq returned non-JSON response: %s", exc)
                raise GroqHandlerError(
                    f"LLM returned invalid JSON: {exc}"
                ) from exc

            except Exception as exc:
                last_exc = exc
                err_msg = str(exc).lower()

                # Do not retry on authentication errors
                if "authentication" in err_msg or "api key" in err_msg or "401" in err_msg:
                    raise GroqHandlerError(
                        f"Authentication failed. Check your GROQ_API_KEY. Details: {exc}"
                    ) from exc

                # Do not retry on rate-limit — the caller should handle this
                if "rate_limit" in err_msg or "429" in err_msg:
                    raise GroqHandlerError(
                        f"Rate limit exceeded: {exc}"
                    ) from exc

                if attempt < self.max_retries:
                    logger.warning(
                        "Groq request failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt,
                        self.max_retries,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2

        raise GroqHandlerError(
            f"Groq request failed after {self.max_retries} attempts: {last_exc}"
        ) from last_exc
