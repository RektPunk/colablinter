import os
import time

from IPython.core.interactiveshell import ExecutionInfo, ExecutionResult
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import (
    cell_check,
    cell_check_isort,
    cell_format,
    notebook_report,
)
from colablinter.logger import logger

_BASE_PATH = "/content/drive"


def _is_invalid_cell(cell: str) -> bool:
    if cell.startswith(("%", "!")):
        return True
    return False


def _ensure_drive_mounted():
    if os.path.exists(_BASE_PATH):
        return

    try:
        from google.colab import drive

        logger.info("Mounting Google Drive required.")
        drive.mount(_BASE_PATH)
    except ImportError as e:
        raise ImportError(
            "This command requires the 'google.colab' environment.\n"
            "The command must be run inside a Google Colab notebook to access the Drive."
        ) from e


class CellTimer:
    def __init__(self):
        self.start_time = None

    def start(self, info: ExecutionInfo | None = None):
        self.start_time = time.perf_counter()

    def stop(self, result: ExecutionResult | None = None):
        if self.start_time:
            duration = time.perf_counter() - self.start_time
            logger.info(f"\033[92m✔ Done | {duration:.3f}s\033[0m")
            self.start_time = None


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._is_autoformat_active = True
        self.timer = CellTimer()

    @cell_magic
    def ccheck(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        cell_check(stripped_cell)
        self.__execute(stripped_cell)

    @cell_magic
    def cformat(self, line: str, cell: str) -> None:
        stripped_cell = cell.strip()
        if _is_invalid_cell(stripped_cell):
            logger.info(
                "Format skipped. Cell starts with magic (%, %%) or shell (!...) command."
            )
            self.__execute(stripped_cell)
            return None

        formatted_code = cell_format(stripped_cell)
        if formatted_code is None:
            logger.error("Formatter failed. Code not modified.")
            self.__execute(stripped_cell)
            return None

        fixed_code = cell_check_isort(formatted_code)
        if fixed_code:
            self.shell.set_next_input(fixed_code, replace=True)
            self.__execute(fixed_code)
        else:
            logger.error("Formatter failed. Formatted code executed.")
            self.__execute(formatted_code)

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

    @line_magic
    def clcheck(self, line: str) -> None:
        _ensure_drive_mounted()
        notebook_path = line.strip().strip("'").strip('"')
        if not notebook_path:
            logger.warning(
                "Usage: %clreport /content/drive/MyDrive/Colab Notebooks/path/to/notebook.ipynb"
            )
            return

        logger.info("---- Notebook Quality & Style Check Report ----")
        try:
            report = notebook_report(notebook_path)
            if report:
                logger.info(report)
            else:
                logger.info("No issues found in the entire notebook. Code is clean.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not founded: {notebook_path}, {e}") from e
        except Exception as e:
            raise RuntimeError(f"Notebook report command failed: {e}") from e
        logger.info("-------------------------------------------------------------")

    def __execute(self, cell: str) -> None:
        if self._is_autoformat_active:
            logger.info(
                "autoformat is temporarily suppressed to prevent dual execution. "
                "To disable, run: %clautoformat off"
            )
            self.__unregister()
        try:
            self.shell.run_cell(cell, silent=False, store_history=True)
        except Exception as e:
            logger.exception(f"Code execution failed: {e}")
        finally:
            if self._is_autoformat_active:
                self.__register()

    def __autoformat(self, info: ExecutionInfo) -> None:
        stripped_cell = info.raw_cell.strip()
        if _is_invalid_cell(stripped_cell):
            logger.info("autoformat is skipped for cell with magic or terminal.")
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
        for event, callback in [
            ("pre_run_cell", self.__autoformat),
            ("pre_run_cell", self.timer.start),
            ("post_run_cell", self.timer.stop),
        ]:
            try:
                self.shell.events.unregister(event, callback)
            except Exception:
                pass
