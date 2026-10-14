import contextlib
import time

from IPython.core.interactiveshell import ExecutionInfo
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from colablinter.command import (
    cell_check,
    cell_check_fix,
    cell_check_unsafe_fix,
    cell_format,
)
from colablinter.logger import logger


@magics_class
class ColabLinterMagics(Magics):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._is_autofix_active = True
        self._is_processing = False

    @cell_magic
    def clcheck(self, line: str, cell: str) -> None:
        if self._is_processing:
            return

        start_time = time.perf_counter()
        stripped_cell = cell.strip()
        report = cell_check(stripped_cell)
        if report:
            logger.info(report)
            msg = "Check completed"
        else:
            msg = "No issues found"

        self._execute(stripped_cell)
        duration = time.perf_counter() - start_time
        logger.success(f"✔ {msg} ({duration:.3f}s)")

    @cell_magic
    def clunsafefix(self, line: str, cell: str) -> None:
        if self._is_processing:
            return

        if self.shell is None:
            raise RuntimeError("IPython shell is not initialized.")

        start_time = time.perf_counter()
        stripped_cell = cell.strip()
        fixed_code = cell_check_unsafe_fix(stripped_cell)
        if fixed_code and fixed_code != stripped_cell:
            code = fixed_code
            msg = "Unsafe fixes applied"
        else:
            code = stripped_cell
            msg = "No fixes needed"

        self._execute(code)
        self.shell.set_next_input(code, replace=True)
        duration = time.perf_counter() - start_time
        logger.success(f"✔ {msg} ({duration:.3f}s)")

    @line_magic
    def clautofix(self, line: str) -> None:
        action = line.strip().lower()
        if action == "on":
            self._is_autofix_active = True
            self._register()
            logger.info("Auto-fix activated for pre-run cells.")
        elif action == "off":
            self._is_autofix_active = False
            self._unregister()
            logger.info("Auto-fix deactivated.")
        else:
            logger.info("Usage: %clautofix on or %clautofix off.")

    def _execute(self, cell: str) -> None:
        if self._is_processing:
            return

        if self.shell is None:
            raise RuntimeError("IPython shell is not initialized.")

        self._is_processing = True
        if self._is_autofix_active:
            self._unregister()

        try:
            self.shell.run_cell(cell, silent=False, store_history=False)
        finally:
            self._is_processing = False
            if self._is_autofix_active:
                self._register()

    def _autofix(self, info: ExecutionInfo) -> None:
        if (
            self._is_processing
            or not self._is_autofix_active
            or self.shell is None
            or info.raw_cell is None
            or not isinstance(info.raw_cell, str)
            or (stripped_cell := info.raw_cell.strip()) == ""
        ):
            return

        if stripped_cell.startswith(("%", "!", "?")):
            logger.info(
                "Autofix skipped: System or Magic command detected. "
                "To disable autofix, run: %clautofix off",
            )
            return

        start_time = time.perf_counter()
        fixed_code = cell_check_fix(stripped_cell)
        if fixed_code is None:
            logger.error("Linter check failed during auto-format.")
            return

        formatted_code = cell_format(fixed_code)
        if formatted_code is None:
            logger.error("Formatter failed during auto-format.")
            return

        if stripped_cell == formatted_code:
            return

        self.shell.set_next_input(formatted_code, replace=True)
        duration = time.perf_counter() - start_time
        logger.success(f"✔ Auto-format completed ({duration:.3f}s)")

    def _register(self) -> None:
        if self.shell is None:
            raise RuntimeError("IPython shell is not initialized.")

        self._unregister()
        with contextlib.suppress(Exception):
            self.shell.events.register("pre_run_cell", self._autofix)

    def _unregister(self) -> None:
        if self.shell is None:
            raise RuntimeError("IPython shell is not initialized.")

        with contextlib.suppress(Exception):
            self.shell.events.unregister("pre_run_cell", self._autofix)
