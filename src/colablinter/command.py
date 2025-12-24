import re
import subprocess

from sqlfluff.core import FluffConfig, Linter

from colablinter.logger import logger

_FILE_NAME = "notebook_cell.py"
_RULESET = "F,E,I,B"
_CELL_REPORT_COMMAND = f"ruff check --select {_RULESET} --ignore F401 --line-length 100 --stdin-filename={_FILE_NAME}"
_CELL_CHECK_COMMAND = f"{_CELL_REPORT_COMMAND} --fix"
_CELL_FORMAT_COMMAND = f"ruff format --stdin-filename={_FILE_NAME}"
_NOTEBOOK_REPORT_COMMAND = (
    f"ruff check --select {_RULESET} --line-length 100 '{{notebook_path}}'"
)

_FLUFF_CONFIG = FluffConfig(
    configs={
        "core": {
            "dialect": "postgres",
            "indent_unit": "space",
        },
        "indentation": {
            "indent_unit": "space",
            "tab_space_size": 4,
            "indented_joins": True,
        },
        "rules": {
            "capitalisation.keywords": {"capitalisation_policy": "upper"},
            "capitalisation.types": {"capitalisation_policy": "upper"},
            "capitalisation.literals": {"capitalisation_policy": "upper"},
            "aliasing.column": {"aliasing": "explicit"},
            "aliasing.table": {"aliasing": "explicit"},
        },
    }
)
_SQL_LINTER = Linter(config=_FLUFF_CONFIG)


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
                logger.warning(f"Linter: {stderr_content}")
            elif "All checks passed" in stderr_content:
                pass
            else:
                logger.error(f"Subprocess: {stderr_content}")
        return result.stdout.strip()
    except Exception as e:
        logger.exception(f"Error running command: {e}")
        return None


def cell_report(cell: str) -> None:
    report = execute_command(_CELL_REPORT_COMMAND, input_data=cell)
    if report:
        logger.info(report)
    else:
        logger.info("No issues found. Code is clean.")


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
        _NOTEBOOK_REPORT_COMMAND.format(notebook_path=notebook_path),
        "",
    )


def cell_sql(cell: str, var_name: str) -> str | None:
    pattern = rf'([\s\S]*?){var_name}\s*=\s*([frb]*?)(?P<q>"""|\'\'\'|"|\')([\s\S]*?)(?P=q)(?P<suffix>[\s\S]*)'
    match = re.search(pattern, cell)
    if not match:
        return None

    prefix, py_prefix, _, raw_sql, suffix = match.groups()
    try:
        lint_result = _SQL_LINTER.lint_string(raw_sql.strip(), fix=True)
        formatted_sql, is_success = lint_result.fix_string()
        if not is_success:
            raise Exception
        return f'{prefix}{var_name} = {py_prefix}"""\n{formatted_sql.strip()}\n"""{suffix}'.strip()
    except Exception:
        return None
