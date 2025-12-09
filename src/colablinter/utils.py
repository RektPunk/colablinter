import subprocess
import sys


def execute_command(command: str, input_data: str) -> str | None:
    try:
        result = subprocess.run(
            command,
            input=input_data,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.stderr:
            print(
                f"[ColabLinter: Subprocess Warning/Error]: {result.stderr.strip()}",
                file=sys.stderr,
            )
        return result.stdout.strip()
    except Exception as e:
        print(f"[ColabLinter:ERROR] Error running command: {e}")
        return
