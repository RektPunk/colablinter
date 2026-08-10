import subprocess

from colablinter.logger import logger

CELL_CHECK_COMMAND = [
    "ruff",
    "check",
    "--quiet",
    "--select",
    "B,E,F,I,UP,SIM",
    "--ignore",
    "F401,E501",
    "--stdin-filename=tmp.py",
    "-",
]
CELL_CHECK_FIX_COMMAND = [
    "ruff",
    "check",
    "--fix",
    "--quiet",
    "--select",
    "B,E,F,I,UP,SIM",
    "--ignore",
    "F401,E501",
    "--stdin-filename=tmp.py",
    "-",
]
CELL_CHECK_UNSAFE_FIX_COMMAND = [
    "ruff",
    "check",
    "--fix",
    "--unsafe-fixes",
    "--quiet",
    "--select",
    "B,E,F,I,UP,SIM",
    "--ignore",
    "F401,E501",
    "--stdin-filename=tmp.py",
    "-",
]
CELL_FORMAT_COMMAND = [
    "ruff",
    "format",
    "--quiet",
    "--stdin-filename=tmp.py",
    "-",
]


def execute_command(command: list[str], input_data: str) -> str | None:
    try:
        result = subprocess.run(
            command,
            input=input_data,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        logger.exception("Error running command.")
        return

    return result.stdout


def cell_check(cell: str) -> None:
    report = execute_command(CELL_CHECK_COMMAND, input_data=cell)
    if report and report.strip():
        logger.info(report.strip())
    else:
        logger.info("No issues found. Code is clean.")


def cell_check_fix(cell: str) -> str | None:
    result = execute_command(CELL_CHECK_FIX_COMMAND, input_data=cell)
    return result.strip() if result and result.strip() else None


def cell_check_unsafe_fix(cell: str) -> str | None:
    result = execute_command(CELL_CHECK_UNSAFE_FIX_COMMAND, input_data=cell)
    return result.strip() if result and result.strip() else None


def cell_format(cell: str) -> str | None:
    result = execute_command(CELL_FORMAT_COMMAND, input_data=cell)
    return result.strip() if result and result.strip() else None
