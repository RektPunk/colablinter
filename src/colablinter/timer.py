import time

from IPython.core.interactiveshell import ExecutionInfo, ExecutionResult

from colablinter.logger import logger


class CellTimer:
    def __init__(self):
        self.start_time = None

    def start(self, info: ExecutionInfo | None = None):
        self.start_time = time.perf_counter()

    def stop(self, result: ExecutionResult | None = None):
        if self.start_time:
            duration = time.perf_counter() - self.start_time
            if result and not result.success:
                logger.info(f"\033[91m✘ Failed | {duration:.3f}s\033[0m")
            else:
                logger.info(f"\033[92m✔ Done | {duration:.3f}s\033[0m")
            self.start_time = None
