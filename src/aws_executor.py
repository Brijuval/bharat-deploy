import subprocess
from typing import Dict


class AWSExecutor:
    def execute(self, command: str, dry_run: bool = False) -> Dict:
        """Execute an AWS CLI command.

        Args:
            command: The full AWS CLI command string.
            dry_run: When True the command is not executed; only a preview is
                     returned.

        Returns:
            A dict with keys ``success``, ``output``, and ``error``.
        """
        if dry_run:
            return {
                "success": True,
                "output": f"[DRY RUN] {command}",
                "error": None,
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
