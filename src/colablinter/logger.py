import sys

from loguru import logger

logger.remove()
_ = logger.add(
    sys.stdout,
    format="<cyan><bold>[ColabLinter]</bold></cyan> <level>{message}</level>",
    level="INFO",
    colorize=True,
)
