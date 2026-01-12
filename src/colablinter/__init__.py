from IPython.core.interactiveshell import InteractiveShell

from colablinter.logger import logger

try:
    from colablinter.magics import ColabLinterMagics

    def load_ipython_extension(ipython: InteractiveShell):
        ipython.register_magics(ColabLinterMagics)
        logger.info("All commands registered.")
        ipython.run_line_magic("clautofix", "on")

except Exception as e:
    logger.exception(f"Initialization failed: {e}")
    pass
