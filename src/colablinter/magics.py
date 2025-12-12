from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import cell_check, cell_format, cell_report
from colablinter.drive_mount import RequiredDriveMountColabLinter
from colablinter.logger import logger


def is_invalid_cell(cell: str) -> bool:
    if cell.startswith(("%", "!")):
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
            logger.info(
                "Fix skipped. Cell starts with magic (%, %%) or shell (!...) command."
            )
            self.__execute(stripped_cell)
            return None

        fixed_code = cell_check(stripped_cell)
        if fixed_code is None:
            logger.error("Linter check failed. Code not modified.")
            self.__execute(stripped_cell)
            return None

        formatted_code = cell_format(fixed_code)
        if formatted_code:
            self.shell.set_next_input(formatted_code, replace=True)
            self.__execute(formatted_code)
        else:
            logger.error("Formatter failed. Check-fixed code executed.")
            self.__execute(fixed_code)

    @line_magic
    def cl_autofix(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self.shell.events.register("pre_run_cell", self.__autofix)
            logger.info("Auto-fix activated for pre-run cells.")
        elif action == "off":
            try:
                self.shell.events.unregister("pre_run_cell", self.__autofix)
            except Exception:
                pass
            logger.info("Auto-fix deactivated.")
        else:
            logger.info("Usage: %%cl_autofix on or %%cl_autofix off.")

    def __execute(self, cell: str) -> None:
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            logger.exception(f"Code execution failed: {e}")

    def __autofix(self, info: ExecutionInfo) -> None:
        stripped_cell = info.raw_cell.strip()
        if is_invalid_cell(stripped_cell):
            logger.info("Autofix is skipped for cell with magic or terminal.")
            return None

        fixed_code = cell_check(stripped_cell)
        if fixed_code is None:
            logger.error("Linter check failed during auto-fix.")
            return None

        formatted_code = cell_format(fixed_code)
        if formatted_code is None:
            logger.error("Formatter failed during auto-fix.")
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
            logger.exception(f"%%cl_report command failed during execution: {e}")

    def __ensure_linter_initialized(self) -> bool:
        if RequiredDriveMountMagics._linter_instance:
            return True

        try:
            RequiredDriveMountMagics._linter_instance = RequiredDriveMountColabLinter()
            return True
        except Exception as e:
            logger.exception(f"Required drive mount magic initialization failed.: {e}")
            RequiredDriveMountMagics._linter_instance = None
            return False
