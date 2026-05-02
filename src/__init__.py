"""
BharatDeploy - Multi-language DevOps CLI Agent for AWS.

Deploy AWS infrastructure using natural language commands in Hindi.
"""

from src.lang_detector import LangDetector, detect_language
from src.config import Config
from src.groq_handler import GroqHandler
from src.action_mapper import ActionMapper
from src.aws_executor import AWSExecutor
from src.error_explainer import ErrorExplainer
from src.prompt_packager import PromptPackager

__version__ = "0.1.0"
__author__ = "Brijuval"

__all__ = [
    "LangDetector",
    "detect_language",
    "Config",
    "GroqHandler",
    "ActionMapper",
    "AWSExecutor",
    "ErrorExplainer",
    "PromptPackager",
]
