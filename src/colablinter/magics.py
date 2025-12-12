import sys

from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from .command import cell_check, cell_format, cell_report
from .drive_mount import RequiredDriveMountColabLinter


def is_invalid_cell(cell: str) -> bool:
    for line in cell.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith(("%", "!")):
            return True
    return False


@magics_class
class ColabLinterMagics(Magics):
    @cell_magic
    def cl_report(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        cell_report(stripped_cell)
        self.__execute(stripped_cell)

    @cell_magic
    def cl_fix(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        if is_invalid_cell(stripped_cell):
            print(
                "[ColabLinter:INFO] %%cl_fix is ignored for cell with magic or terminal command."
            )
            self.__execute(stripped_cell)
            return None

        fixed_code = cell_check(stripped_cell)
        if fixed_code is None:
            print("[ColabLinter:ERROR] Check failed.")
            self.__execute(stripped_cell)
            return None

        formatted_code = cell_format(fixed_code)
        if formatted_code:
            self.shell.set_next_input(formatted_code, replace=True)
            self.__execute(formatted_code)
        else:
            print("[ColabLinter:ERROR] Format failed.")
            self.__execute(fixed_code)

    @line_magic
    def cl_autofix(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self.shell.events.register("pre_run_cell", self.__auto)
            print("[ColabLinter:INFO] Auto code formatting activated.")
        elif action == "off":
            try:
                self.shell.events.unregister("pre_run_cell", self.__auto)
            except Exception:
                pass
            print("[ColabLinter:INFO] Auto code formatting deactivated.")
        else:
            print("[ColabLinter:INFO] Usage: %cl_autofix on or %cl_autofix off.")

    def __execute(self, cell: str) -> None:
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            print(f"[ColabLinter:ERROR] Code execution failed: {e}")

    def __auto(self, info: ExecutionInfo) -> None:
        stripped_cell = info.raw_cell.strip()
        if is_invalid_cell(stripped_cell):
            print(
                "[ColabLinter:INFO] Autofix is ignored with cell with magic or terminal."
            )
            return None

        fixed_code = cell_check(stripped_cell)
        if fixed_code is None:
            print("[ColabLinter:ERROR] Check failed.")
            return None

        formatted_code = cell_format(fixed_code)
        if formatted_code is None:
            print("[ColabLinter:ERROR] Format failed.")
            return None
        self.shell.set_next_input(formatted_code, replace=True)


@magics_class
class RequiredDriveMountMagics(Magics):
    _linter_instance = None

    @line_magic
    def cl_report(self, line):
        if not self.__ensure_linter_initialized():
            return None

        try:
            RequiredDriveMountMagics._linter_instance.check()
        except Exception as e:
            print(
                f"[ColabLinter:ERROR] %cl_report command failed: {e}", file=sys.stderr
            )

    def __ensure_linter_initialized(self) -> bool:
        if RequiredDriveMountMagics._linter_instance:
            return True

        try:
            RequiredDriveMountMagics._linter_instance = RequiredDriveMountColabLinter()
            return True
        except Exception as e:
            print(
                f"[ColabLinter:ERROR] Required drive mount magic initialization failed: {e}",
                file=sys.stderr,
            )
            RequiredDriveMountMagics._linter_instance = None
            return False
