import subprocess
import sys

_FILE_NAME = "notebook_cell.py"
_RULESET = "F,E,I,B"
_CELL_REPORT_COMMAND = f"ruff check --select {_RULESET} --ignore F401 --line-length 100 --stdin-filename={_FILE_NAME}"
_CELL_CHECK_COMMAND = f"{_CELL_REPORT_COMMAND} --fix"
_CELL_FORMAT_COMMAND = f"ruff format --stdin-filename={_FILE_NAME}"


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
            stderr_content = result.stderr.strip()
            if "Found" in stderr_content:
                print(
                    f"[ColabLinter: Linter Warning/Error]: {stderr_content}",
                    file=sys.stderr,
                )
            elif "All checks passed" in stderr_content:
                pass
            else:
                print(
                    f"[ColabLinter: Subprocess Warning/Error]: {stderr_content}",
                    file=sys.stderr,
                )
        return result.stdout.strip()
    except Exception as e:
        print(f"[ColabLinter:ERROR] Error running command: {e}")
        return None


def cell_report(cell: str) -> None:
    report = execute_command(_CELL_REPORT_COMMAND, input_data=cell)
    if report:
        print(f"[ColabLiter:INFO] {report}")
    else:
        print("[ColabLinter:INFO] No issues found. Code is clean.")


def cell_check(cell: str) -> str | None:
    fixed_code = execute_command(_CELL_CHECK_COMMAND, input_data=cell).strip()
    if fixed_code.strip():
        return fixed_code.strip()
    return None


def cell_format(cell: str) -> str | None:
    formatted_code = execute_command(_CELL_FORMAT_COMMAND, input_data=cell)
    if formatted_code.strip():
        return formatted_code.strip()
    return None


def notebook_report(notebook_path: str) -> None:
    return execute_command(
        f"ruff check --select F,E,I,B '{notebook_path}'",
        "",
    )
