from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import cell_check, cell_format, cell_report
from colablinter.drive_mount import RequiredDriveMountLinter
from colablinter.logger import logger


def _is_invalid_cell(cell: str) -> bool:
    if cell.startswith(("%", "!")):
        return True
    return False


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_autofix_active = False
        self._require_drive_mount_linter_instance = None

    @cell_magic
    def creport(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        cell_report(stripped_cell)
        self.__execute(stripped_cell)

    @cell_magic
    def cfix(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        if _is_invalid_cell(stripped_cell):
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
    def clautofix(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self.shell.events.register("pre_run_cell", self.__autofix)
            self._is_autofix_active = True
            logger.info("Auto-fix activated for pre-run cells.")
        elif action == "off":
            try:
                self.shell.events.unregister("pre_run_cell", self.__autofix)
            except Exception:
                pass
            self._is_autofix_active = False
            logger.info("Auto-fix deactivated.")
        else:
            logger.info("Usage: %clautofix on or %clautofix off.")

    @line_magic
    def clreport(self, line):
        if not self.__ensure_linter_initialized():
            return None
        try:
            self._require_drive_mount_linter_instance.check()
        except Exception as e:
            logger.exception(f"%clreport command failed during execution: {e}")

    def __execute(self, cell: str) -> None:
        if self._is_autofix_active:
            logger.info(
                "Autofix is temporarily suppressed to prevent dual execution. "
                "To disable, run: %clautofix off"
            )
            try:
                self.shell.events.unregister("pre_run_cell", self.__autofix)
            except ValueError:
                pass
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            logger.exception(f"Code execution failed: {e}")
        finally:
            if self._is_autofix_active:
                try:
                    self.shell.events.register("pre_run_cell", self.__autofix)
                except Exception:
                    pass

    def __autofix(self, info: ExecutionInfo) -> None:
        stripped_cell = info.raw_cell.strip()
        if _is_invalid_cell(stripped_cell):
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

    def __ensure_linter_initialized(self) -> bool:
        if self._require_drive_mount_linter_instance:
            return True
        try:
            self._require_drive_mount_linter_instance = RequiredDriveMountLinter()
            return True
        except Exception as e:
            logger.exception(f"Required drive mount magic initialization failed.: {e}")
            self._require_drive_mount_linter_instance = None
            return False
