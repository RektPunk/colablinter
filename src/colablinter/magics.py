import sys

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from .notebook import ColabLinter
from .utils import execute_command

_FILE_NAME = "notebook_cell.py"
_CHECK_COMMAND = f"ruff check --stdin-filename={_FILE_NAME}"
_FORMAT_COMMAND = f"ruff format --stdin-filename={_FILE_NAME}"
_ISORT_COMMAND = "isort --profile=black -"


@magics_class
class LintCellMagics(Magics):
    @cell_magic
    def cl_check(self, line: str, cell: str) -> None:
        self.__check(cell)
        self.__execute(cell)

    @cell_magic
    def cl_format(self, line: str, cell: str) -> None:
        self.__format(cell)
        self.__execute(cell)

    def __check(self, cell: str) -> None:
        print("---- Code Quality & Style Check Report ----")
        report = execute_command(_CHECK_COMMAND, input_data=cell)
        if report:
            print(report)
        else:
            print("[ColabLinter:INFO] No issues found. Code is clean.")
        print("-------------------------------------------")

    def __format(self, cell: str) -> None:
        _formatted_code = execute_command(_FORMAT_COMMAND, input_data=cell)
        if _formatted_code is None:
            print("[ColabLinter:ERROR] Formatting failed.")
            return
        formatted_code = execute_command(_ISORT_COMMAND, input_data=_formatted_code)
        code_to_print = formatted_code if formatted_code else _formatted_code

        if cell.strip() != code_to_print.strip():
            print("# Formatted Code")
            print(code_to_print.strip())
        else:
            print("[ColabLinter:INFO] Code already formatted. No changes needed.")
        return

    def __execute(self, cell: str) -> None:
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            print(f"[ColabLinter:ERROR] Code execution failed: {e}")


@magics_class
class LintLineMagic(Magics):
    _linter_instance = None

    @line_magic
    def cl_check(self, line):
        if not self.__ensure_linter_initialized():
            return

        try:
            LintLineMagic._linter_instance.check()
        except Exception as e:
            print(f"[ColabLinter:ERROR] %cl_check command failed: {e}", file=sys.stderr)

    def __ensure_linter_initialized(self) -> bool:
        if LintLineMagic._linter_instance:
            return True

        try:
            LintLineMagic._linter_instance = ColabLinter()
            return True
        except Exception as e:
            print(
                f"[ColabLinter:ERROR] Line magic initialization failed: {e}",
                file=sys.stderr,
            )
            LintLineMagic._linter_instance = None
            return False
