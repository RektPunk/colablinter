import sys

from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from .drive_mount import RequiredDriveMountColabLinter
from .utils import execute_command

_FILE_NAME = "notebook_cell.py"
_CHECK_COMMAND = f"ruff check --stdin-filename={_FILE_NAME}"
_FORMAT_COMMAND = f"ruff format --stdin-filename={_FILE_NAME}"
_ISORT_COMMAND = "isort --profile=black -"


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self._auto_format_active = False

    @cell_magic
    def cl_check(self, line: str, cell: str) -> None:
        self.__check(cell)
        self.__execute(cell)

    @cell_magic
    def cl_format(self, line: str, cell: str) -> None:
        if self._auto_format_active:
            print(
                "[ColabLinter:INFO] %%cl_format skipped."
                "Auto code formatting is currently ON (%cl_auto_format off to disable)."
            )
            self.__execute(cell)  # 포맷만 건너뛰고 실행은 유지
            return
        self.__execute(cell)

    @line_magic
    def cl_auto_format(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self._auto_format_active = True
            self.shell.events.register("pre_run_cell", self.__format_info)
            print("[ColabLinter:INFO] Auto code formatting activated.")
        elif action == "off":
            self._auto_format_active = False
            self.shell.events.unregister("pre_run_cell", self.__format_info)
            print("[ColabLinter:INFO] Auto code formatting deactivated.")
        else:
            print(
                "[ColabLinter:INFO] Usage: %cl_auto_format on or %cl_auto_format off."
            )

    def __check(self, cell: str) -> None:
        print("---- Code Quality & Style Check Report ----")
        report = execute_command(_CHECK_COMMAND, input_data=cell)
        if report:
            print(report)
        else:
            print("[ColabLinter:INFO] No issues found. Code is clean.")
        print("-------------------------------------------")

    def __format(self, cell: str) -> None:
        stripped_cell = cell.strip()
        if (
            stripped_cell.startswith(("%", "!"))
            and len(stripped_cell.splitlines()) == 1
        ):
            return

        _formatted_code = execute_command(_FORMAT_COMMAND, input_data=cell)
        if _formatted_code is None:
            print("[ColabLinter:ERROR] Formatting failed.")
            return
        formatted_code = execute_command(_ISORT_COMMAND, input_data=_formatted_code)
        code_to_print = formatted_code if formatted_code else _formatted_code

        if cell.strip() != code_to_print.strip():
            self.shell.set_next_input(code_to_print, replace=True)
        return

    def __execute(self, cell: str) -> None:
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            print(f"[ColabLinter:ERROR] Code execution failed: {e}")

    def __format_info(self, info: ExecutionInfo) -> None:
        self.__format(info.raw_cell)


@magics_class
class RequiredDriveMountMagics(Magics):
    _linter_instance = None

    @line_magic
    def cl_check(self, line):
        if not self.__ensure_linter_initialized():
            return

        try:
            RequiredDriveMountMagics._linter_instance.check()
        except Exception as e:
            print(f"[ColabLinter:ERROR] %cl_check command failed: {e}", file=sys.stderr)

    def __ensure_linter_initialized(self) -> bool:
        if RequiredDriveMountMagics._linter_instance:
            return True

        try:
            RequiredDriveMountMagics._linter_instance = RequiredDriveMountColabLinter()
            return True
        except Exception as e:
            print(
                f"[ColabLinter:ERROR] Line magic initialization failed: {e}",
                file=sys.stderr,
            )
            RequiredDriveMountMagics._linter_instance = None
            return False
