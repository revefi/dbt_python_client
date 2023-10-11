from logging import getLogger, Formatter, StreamHandler


def configure_logging(level: str) -> None:
    logger = getLogger()
    logger.setLevel(level)

    log_formatter = Formatter("[%(process)d] %(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console_handler = StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
