from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import (
    cell_check,
    cell_check_isort,
    cell_format,
)
from colablinter.logger import logger
from colablinter.timer import CellTimer


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._is_autoformat_active = True
        self.timer = CellTimer()

    @cell_magic
    def clcheck(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        cell_check(stripped_cell)
        self.__execute(stripped_cell)

    @line_magic
    def clautoformat(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self.__register()
            self._is_autoformat_active = True
            logger.info("Auto-format activated for pre-run cells.")
        elif action == "off":
            self.__unregister()
            self._is_autoformat_active = False
            logger.info("Auto-format deactivated.")
        else:
            logger.info("Usage: %clautoformat on or %clautoformat off.")

    def __execute(self, cell: str) -> None:
        if self._is_autoformat_active:
            logger.info(
                "autoformat is temporarily suppressed to prevent dual execution. "
                "To disable, run: %clautoformat off"
            )
            self.__unregister()

        try:
            if self.shell is None:
                raise Exception
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            logger.exception(f"Code execution failed: {e}")
        finally:
            if self._is_autoformat_active:
                self.__register()

    def __autoformat(self, info: ExecutionInfo) -> None:
        if (
            self.shell is None
            or info.raw_cell is None
            or not isinstance(info.raw_cell, str)
        ):
            return None

        stripped_cell = info.raw_cell.strip()
        if stripped_cell.startswith(("%", "!")) or stripped_cell == "":
            return None

        formatted_code = cell_format(stripped_cell)
        if formatted_code is None:
            logger.error("Formatter failed during auto-format.")
            return None

        fixed_code = cell_check_isort(formatted_code)
        if fixed_code is None:
            logger.error("Linter check failed during auto-format.")
            return None

        self.shell.set_next_input(fixed_code, replace=True)

    def __register(self) -> None:
        if self.shell is None:
            return None

        for event, callback in [
            ("pre_run_cell", self.__autoformat),
            ("pre_run_cell", self.timer.start),
            ("post_run_cell", self.timer.stop),
        ]:
            try:
                self.shell.events.register(event, callback)
            except Exception:
                pass

    def __unregister(self) -> None:
        if self.shell is None:
            return None

        for event, callback in [
            ("pre_run_cell", self.__autoformat),
            ("pre_run_cell", self.timer.start),
            ("post_run_cell", self.timer.stop),
        ]:
            try:
                self.shell.events.unregister(event, callback)
            except Exception:
                pass
