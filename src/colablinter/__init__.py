from IPython.core.interactiveshell import InteractiveShell

from colablinter.logger import logger
from colablinter.magics import ColabLinterMagics


def load_ipython_extension(ipython: InteractiveShell) -> None:
    try:
        ipython.register_magics(ColabLinterMagics)
        logger.info("All commands registered.")
        ipython.run_line_magic("clautofix", "on")
    except Exception:
        logger.exception("Initialization failed.")
        raise
