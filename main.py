"""
BharatDeploy — CLI entry point.

Usage:
    python main.py --help
    python main.py deploy "EC2 instance banao" --dry-run
    python main.py list "Saari instances dikhao"
    python main.py explain "AccessDenied: ec2:RunInstances"
"""

from src.cli import cli

if __name__ == "__main__":
    cli()
