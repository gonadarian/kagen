import kagen
from kagen import utils


logger = utils.get_logger("main")


def work():
    logger.info("GO prepare")
    kagen.prepare.main()
    logger.info("GO khan")
    kagen.khan.main()
    logger.info("GO spreadsheet")
    kagen.spreadsheet.main()
    logger.info("GO youtube")
    kagen.youtube.main()
    logger.info("GO hierarchy")
    kagen.hierarchy.main()
    logger.info("GO mapping")
    kagen.mapping.main()
    logger.info("GO languages")
    kagen.languages.main()
    logger.info("GO subtitle")
    kagen.subtitle.main()
    logger.info("GO templates")
    kagen.templates.main()


@utils.entry_point
def main():
    logger.info("START main")
    work()
    logger.info("DONE main")
