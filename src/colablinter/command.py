import subprocess

from colablinter.logger import logger

CELL_CHECK_COMMAND = (
    "ruff check --select F,E,I,B --ignore F401,E501 --stdin-filename=tmp.py"
)
CELL_FIX_ISORT_COMMAND = "ruff check --select I --fix --stdin-filename=tmp.py"
CELL_FORMAT_COMMAND = "ruff format --stdin-filename=tmp.py"


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
        return result.stdout.strip()
    except Exception as e:
        logger.exception(f"Error running command: {e}")
        return None


def cell_check(cell: str) -> None:
    report = execute_command(CELL_CHECK_COMMAND, input_data=cell)
    if report:
        logger.info(report)
    else:
        logger.info("No issues found. Code is clean.")


def cell_check_isort(cell: str) -> str | None:
    fixed_code = execute_command(CELL_FIX_ISORT_COMMAND, input_data=cell)
    if isinstance(fixed_code, str) and fixed_code.strip():
        return fixed_code.strip()
    return None


def cell_format(cell: str) -> str | None:
    formatted_code = execute_command(CELL_FORMAT_COMMAND, input_data=cell)
    if isinstance(formatted_code, str) and formatted_code.strip():
        return formatted_code.strip()
    return None
