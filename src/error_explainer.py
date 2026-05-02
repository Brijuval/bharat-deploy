"""
Error Explainer for BharatDeploy.

Translates cryptic AWS CLI error messages into beginner-friendly explanations
in Hindi (and English), with actionable next steps.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Pattern → (Hindi explanation, English explanation, suggested fix)
# ---------------------------------------------------------------------------
_ERROR_PATTERNS: List[Tuple[str, str, str, str]] = [
    (
        r"UnauthorizedOperation|AccessDenied|AuthFailure",
        "आपके पास इस ऑपरेशन की अनुमति नहीं है।",
        "You don't have permission for this operation.",
        "अपने IAM permissions चेक करें या admin से मदद लें।",
    ),
    (
        r"InvalidClientTokenId|InvalidAccessKeyId",
        "AWS Access Key सही नहीं है।",
        "The AWS Access Key ID is invalid.",
        ".env फ़ाइल में AWS_ACCESS_KEY_ID सही से सेट करें।",
    ),
    (
        r"SignatureDoesNotMatch",
        "AWS Secret Key गलत है।",
        "The AWS Secret Key does not match.",
        ".env फ़ाइल में AWS_SECRET_ACCESS_KEY सही से सेट करें।",
    ),
    (
        r"NoCredentialProviders|Unable to locate credentials",
        "AWS credentials नहीं मिले।",
        "No AWS credentials found.",
        "`aws configure` चलाएं या .env में credentials सेट करें।",
    ),
    (
        r"ResourceNotFoundException|does not exist",
        "यह resource मौजूद नहीं है।",
        "The requested resource does not exist.",
        "Resource का नाम/ID दोबारा चेक करें।",
    ),
    (
        r"LimitExceeded|ServiceLimitExceeded|InstanceLimitExceeded",
        "आपका AWS limit पूरा हो गया है।",
        "AWS service limit exceeded.",
        "AWS console में limit increase request करें।",
    ),
    (
        r"OptInRequired",
        "इस service के लिए आपको पहले opt-in करना होगा।",
        "You need to opt in to this service first.",
        "AWS console में जाकर इस service को enable करें।",
    ),
    (
        r"InvalidParameterValue|InvalidParameterCombination|MissingParameter",
        "Command में गलत parameter दिया गया है।",
        "Invalid or missing parameter in the command.",
        "Command को दोबारा चेक करें और सही values दें।",
    ),
    (
        r"ThrottlingException|RequestLimitExceeded|TooManyRequestsException",
        "बहुत ज़्यादा requests भेजी गईं, थोड़ी देर बाद try करें।",
        "Too many requests — you are being throttled.",
        "कुछ सेकंड रुकें और फिर try करें।",
    ),
    (
        r"EndpointResolutionError|Could not connect|connection refused|timed out",
        "AWS से connection नहीं हो पा रहा।",
        "Cannot connect to AWS endpoint.",
        "इंटरनेट कनेक्शन और AWS region चेक करें।",
    ),
]

_GENERIC_HI = "AWS में कोई error आई है।"
_GENERIC_EN = "An error occurred in AWS."
_GENERIC_FIX = "ऊपर दिए गए error message को ध्यान से पढ़ें।"


class ErrorExplainer:
    """Explains AWS error messages in Hindi with actionable suggestions."""

    def explain(
        self,
        error_message: str,
        command: Optional[str] = None,
    ) -> Dict[str, str]:
        """Return a human-friendly explanation of *error_message*.

        Parameters
        ----------
        error_message:
            Raw error string from the AWS CLI or Boto3.
        command:
            The AWS CLI command that produced the error (optional, for context).

        Returns
        -------
        dict with keys:
            - ``error_original`` – the original error text
            - ``explanation_hi`` – plain Hindi explanation
            - ``explanation_en`` – English explanation
            - ``suggestion_hi``  – suggested fix in Hindi
            - ``command``        – the command (may be None)
        """
        explanation_hi = _GENERIC_HI
        explanation_en = _GENERIC_EN
        suggestion_hi = _GENERIC_FIX

        for pattern, hi, en, fix in _ERROR_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                explanation_hi = hi
                explanation_en = en
                suggestion_hi = fix
                break

        return {
            "error_original": error_message,
            "explanation_hi": explanation_hi,
            "explanation_en": explanation_en,
            "suggestion_hi": suggestion_hi,
            "command": command,
        }
