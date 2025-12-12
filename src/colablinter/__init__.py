from colablinter.logger import logger

try:
    from colablinter.magics import ColabLinterMagics, RequiredDriveMountMagics

    def load_ipython_extension(ipython):
        ipython.register_magics(ColabLinterMagics)
        ipython.register_magics(RequiredDriveMountMagics)
        logger.info("cl commands registered.")

except Exception as e:
    logger.exception(f"Initialization failed: {e}")
    pass
