import os

from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import cell_check, cell_format, cell_report, notebook_report
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


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._is_autofix_active = False

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
    def clreport(self, line: str) -> None:
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
