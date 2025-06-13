import logging


class GGLogger:
    def __init__(self, name=__name__, level=logging.DEBUG):
        """
        Initialize the logger.

        :param name: The name of the logger, defaults to the current module name.
        :param level: Logging level, defaults to DEBUG.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid duplicate handlers if multiple instances are created
        if not self.logger.handlers:
            # Create a console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            formatter = logging.Formatter(
                '[%(name)s] [%(asctime)s] [%(levelname)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def exception(self, message):
        self.logger.exception(message)

    def set_level(self, level=logging.INFO):
        self.logger.setLevel(level)
