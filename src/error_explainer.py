"""
Error Explainer for BharatDeploy
Explains AWS errors in Hindi/Hinglish for beginner-friendly experience
"""

import re
from typing import Optional


# Common AWS error patterns and their Hindi explanations
ERROR_EXPLANATIONS = {
    # IAM / Permissions
    "AccessDenied": {
        "hindi": "Aapke paas yeh kaam karne ki permission nahin hai.",
        "fix_steps": [
            "AWS Console mein IAM service kholen",
            "Apna user ya role dhundhen",
            "Zaroorat ki permissions add karen",
            "Ya apne admin se permission maangen",
        ],
        "docs_url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_denied.html",
    },
    "UnauthorizedOperation": {
        "hindi": "Yeh operation karne ki aapko permission nahin hai.",
        "fix_steps": [
            "IAM policy mein zaroorat ki permission check karen",
            "Agar EC2 use kar rahe hain to IAM role attach karen",
        ],
        "docs_url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html",
    },
    # Resource not found
    "NoSuchBucket": {
        "hindi": "Yeh S3 bucket exist nahin karta. Shayad aapne galat naam diya hai.",
        "fix_steps": [
            "Bucket ka naam dobara check karen",
            "`aws s3 ls` se available buckets dekhein",
            "Nayi bucket banane ke liye `aws s3 mb s3://bucket-naam` use karen",
        ],
        "docs_url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/",
    },
    "InvalidInstanceID": {
        "hindi": "Yeh EC2 instance ID galat hai ya exist nahin karta.",
        "fix_steps": [
            "Instance ID dobara check karen (i- se shuru hota hai)",
            "`aws ec2 describe-instances` se active instances dekhein",
            "Sahi region set hai yeh verify karen",
        ],
        "docs_url": "https://docs.aws.amazon.com/ec2/",
    },
    "ResourceNotFoundException": {
        "hindi": "Jo resource aap dhundh rahe hain woh nahin mila.",
        "fix_steps": [
            "Resource ka naam ya ID dobara check karen",
            "Correct AWS region select kiya hai na?",
            "List command se available resources dekhein",
        ],
        "docs_url": "https://docs.aws.amazon.com/",
    },
    # Credentials
    "InvalidClientTokenId": {
        "hindi": "AWS credentials galat hain. API key ya secret key check karen.",
        "fix_steps": [
            "`aws configure` command chalayein",
            "AWS Access Key ID sahi hai check karen",
            "AWS Secret Access Key sahi hai check karen",
            "IAM Console se nayi keys generate kar sakte hain",
        ],
        "docs_url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html",
    },
    "ExpiredTokenException": {
        "hindi": "Aapka AWS session token expire ho gaya hai.",
        "fix_steps": [
            "AWS credentials dobara configure karen",
            "Agar IAM role use kar rahe hain to nayi credentials lein",
            "STS se nayi temporary credentials lein",
        ],
        "docs_url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html",
    },
    # Quota/Limits
    "InstanceLimitExceeded": {
        "hindi": "Aapki AWS account mein instances ki limit poori ho gayi hai.",
        "fix_steps": [
            "AWS Console mein Service Quotas check karen",
            "Kuch purane instances delete/stop karen",
            "AWS Support se limit increase request karen",
        ],
        "docs_url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html",
    },
    "LimitExceededException": {
        "hindi": "AWS service ki limit poori ho gayi hai.",
        "fix_steps": [
            "AWS Service Quotas console check karen",
            "Purani ya unused resources clean up karen",
            "AWS Support se quota increase maangen",
        ],
        "docs_url": "https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html",
    },
    # Network
    "NetworkingError": {
        "hindi": "Network connection problem hai.",
        "fix_steps": [
            "Internet connection check karen",
            "VPN band karna try karen",
            "AWS service status check karen: https://status.aws.amazon.com",
            "AWS region sahi set hai check karen",
        ],
        "docs_url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-proxy.html",
    },
    # Config
    "InvalidParameterValue": {
        "hindi": "Galat parameter value di gayi hai.",
        "fix_steps": [
            "Command ke parameters dobara check karen",
            "AWS documentation mein valid values dekhein",
            "Example commands ke liye EXAMPLES.md dekhein",
        ],
        "docs_url": "https://docs.aws.amazon.com/",
    },
    "MissingParameter": {
        "hindi": "Zaroorat ki parameter missing hai.",
        "fix_steps": [
            "Command mein saari required parameters di hain check karen",
            "AWS CLI help dekhein: aws <service> <command> help",
        ],
        "docs_url": "https://docs.aws.amazon.com/",
    },
}


def explain_error(error_message: str, command: Optional[str] = None) -> dict:
    """
    Explain an AWS error in Hindi/Hinglish.

    Args:
        error_message: The AWS error message
        command: The AWS command that failed (optional)

    Returns:
        Dictionary with explanation and fix steps
    """
    if not error_message:
        return _default_explanation()

    # Try to match known error patterns
    for error_code, explanation in ERROR_EXPLANATIONS.items():
        if error_code.lower() in error_message.lower():
            return {
                "error_type": _categorize_error(error_code),
                "error_code": error_code,
                "explanation_hindi": explanation["hindi"],
                "fix_steps": explanation["fix_steps"],
                "aws_docs_url": explanation["docs_url"],
                "command": command,
                "confidence": 0.9,
            }

    # Try pattern matching for common error patterns
    error_lower = error_message.lower()

    if "permission" in error_lower or "access" in error_lower or "deny" in error_lower:
        return {
            "error_type": "permission",
            "error_code": "AccessDenied",
            "explanation_hindi": "Aapke paas zaroorat ki AWS permission nahin hai.",
            "fix_steps": [
                "IAM Console mein apni permissions check karen",
                "Admin se zaroorat ki permission maangen",
            ],
            "aws_docs_url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/",
            "command": command,
            "confidence": 0.7,
        }

    if "not found" in error_lower or "does not exist" in error_lower:
        return {
            "error_type": "not-found",
            "error_code": "ResourceNotFound",
            "explanation_hindi": "Joh resource dhundh rahe hain woh exist nahin karta.",
            "fix_steps": [
                "Resource ka naam dobara check karen",
                "Correct AWS region mein hain check karen",
                "List command se available resources dekhein",
            ],
            "aws_docs_url": "https://docs.aws.amazon.com/",
            "command": command,
            "confidence": 0.7,
        }

    if "region" in error_lower:
        return {
            "error_type": "config",
            "error_code": "RegionError",
            "explanation_hindi": "AWS region galat set hai ya specify nahin kiya.",
            "fix_steps": [
                "`aws configure` se default region set karen",
                "Command mein --region flag add karen",
                "Indian developers ke liye ap-south-1 (Mumbai) recommended hai",
            ],
            "aws_docs_url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-options.html",
            "command": command,
            "confidence": 0.75,
        }

    if "credential" in error_lower or "token" in error_lower or "key" in error_lower:
        return {
            "error_type": "credentials",
            "error_code": "CredentialsError",
            "explanation_hindi": "AWS credentials galat hain ya configure nahin hain.",
            "fix_steps": [
                "`aws configure` command chalayein",
                "AWS Access Key aur Secret Key sahi darj karen",
                "IAM Console se nayi credentials generate kar sakte hain",
            ],
            "aws_docs_url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html",
            "command": command,
            "confidence": 0.8,
        }

    return _default_explanation(command, error_message)


def _categorize_error(error_code: str) -> str:
    """Categorize an error code into a type."""
    permission_errors = {"AccessDenied", "UnauthorizedOperation"}
    not_found_errors = {"NoSuchBucket", "InvalidInstanceID", "ResourceNotFoundException"}
    credential_errors = {"InvalidClientTokenId", "ExpiredTokenException"}
    quota_errors = {"InstanceLimitExceeded", "LimitExceededException"}
    network_errors = {"NetworkingError"}
    config_errors = {"InvalidParameterValue", "MissingParameter"}

    if error_code in permission_errors:
        return "permission"
    if error_code in not_found_errors:
        return "not-found"
    if error_code in credential_errors:
        return "credentials"
    if error_code in quota_errors:
        return "quota"
    if error_code in network_errors:
        return "network"
    if error_code in config_errors:
        return "config"
    return "unknown"


def _default_explanation(command: Optional[str] = None, error: Optional[str] = None) -> dict:
    """Return a default explanation for unknown errors."""
    return {
        "error_type": "unknown",
        "error_code": "UnknownError",
        "explanation_hindi": (
            "Koi anjaan error aayi hai. "
            "Kripya error message dhyan se padhen aur dubara try karen."
        ),
        "fix_steps": [
            "Error message dobara padhen",
            "AWS documentation check karen",
            "SETUP.md mein troubleshooting section dekhein",
            "Agar problem continue kare to GitHub Issues mein report karen",
        ],
        "aws_docs_url": "https://docs.aws.amazon.com/",
        "command": command,
        "original_error": error,
        "confidence": 0.3,
    }


def format_error_for_display(explanation: dict) -> str:
    """
    Format an error explanation for display to the user.

    Args:
        explanation: Error explanation dictionary from explain_error()

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append("❌ Error Explanation:")
    lines.append(f"   {explanation['explanation_hindi']}")
    lines.append("")

    fix_steps = explanation.get("fix_steps", [])
    if fix_steps:
        lines.append("🔧 Fix karne ke steps:")
        for i, step in enumerate(fix_steps, 1):
            lines.append(f"   {i}. {step}")
        lines.append("")

    docs_url = explanation.get("aws_docs_url")
    if docs_url:
        lines.append(f"📚 AWS Docs: {docs_url}")

    return "\n".join(lines)
