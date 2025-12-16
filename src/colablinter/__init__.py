from colablinter.logger import logger

try:
    from colablinter.magics import ColabLinterMagics

    def load_ipython_extension(ipython):
        ipython.register_magics(ColabLinterMagics)
        logger.info("All commands registered.")

except Exception as e:
    logger.exception(f"Initialization failed: {e}")
    pass
