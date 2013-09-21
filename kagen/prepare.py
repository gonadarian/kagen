import os
import csv
import json
from kagen import utils
from kagen.utils import config


logger = utils.get_logger("prepare")


def work():
    logger.info("Creating folders under {}".format(os.getcwd()))
    print()
    for key, value in config["paths"].items():
        if not os.path.exists(value):
            os.makedirs(value)
            logger.info("  create: {}".format(value))

@utils.entry_point
def main():
    logger.info("START prepare")
    work()
    logger.info("DONE prepare")
