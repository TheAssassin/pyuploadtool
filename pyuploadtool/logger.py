import logging


def make_logger(name):
    return logging.getLogger(f"pyuploadtool.{name}")
