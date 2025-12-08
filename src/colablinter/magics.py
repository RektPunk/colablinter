import subprocess
import sys

from IPython.core.magic import Magics, line_cell_magic, magics_class


def _execute_command(command: str, input_data: str) -> str | None:
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


@magics_class
class LintMagics(Magics):
    _FILE_NAME = "notebook_cell.py"

    @line_cell_magic
    def check(self, line: str, cell: str | None = None) -> str | None:
        if not cell or not cell.strip():
            return
        self.__check(cell)
        self.__execute(cell)

    @line_cell_magic
    def format(self, line: str, cell: str | None = None) -> str | None:
        if not cell or not cell.strip():
            return
        self.__format(cell)
        self.__execute(cell)

    def __check(self, cell: str) -> None:
        print("--- Code Quality & Style Check Report ---")
        if report := _execute_command(
            f"ruff check --stdin-filename={self._FILE_NAME}", input_data=cell
        ):
            print(report)
        else:
            print("[ColabLinter:INFO] No issues found. Code is clean.")
        print("-------------------------------------------")

    def __execute(self, cell: str) -> None:
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            print(f"[ColabLinter:ERROR] Code execution failed: {e}")

    def __format(self, cell: str) -> None:
        _formatted_code: str | None = _execute_command(
            f"ruff format --stdin-filename={self._FILE_NAME}", input_data=cell
        )
        if _formatted_code is None:
            print("[ColabLinter:ERROR] Formatting failed.")
            return

        formatted_code: str | None = _execute_command(
            "isort --profile=black -", input_data=_formatted_code
        )
        code_to_print = (
            formatted_code if formatted_code is not None else _formatted_code
        )
        if cell.strip() != code_to_print.strip():
            print("# Formatted Code (Copy & Paste Below)")
            print(formatted_code.strip())
        else:
            print("[ColabLinter:INFO] Code already formatted. No changes needed.")
