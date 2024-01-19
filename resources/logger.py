import logging

class Logger:
    @staticmethod
    def get_logger(name):
        # Set up the logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Create a console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        # Create a formatter
        formatter = logging.Formatter(
            "%(name)s - %(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        return logger