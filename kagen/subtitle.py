import sys
import json
import pymongo
from time import time
from kagen import utils
from queue import Queue
from threading import Thread
from kagen.utils import config


logger = utils.get_logger("subtitle")
dir_pages_srt = config["paths"]["dir_pages_srt"]
q = Queue()


def work():
    tstart = time()
    lang = config["main"]["language"]
    pool_size = int(config["main"]["thread_pool_size"])

    db = utils.get_conn_mongo()
    db.video_subtitles.drop()
    db.video_subtitles_srt.drop()
    [SubGetter(db, lang) for i in range(pool_size)]

    criteria = {"$nor": [{"versions": {"$exists": False}}, {"versions": {"$size": 0}}]}
    [q.put(language) for language in db.video_languages.find(criteria)]

    q.join()

    logger.info(utils.check_time("subtitles", tstart))


class SubGetter(Thread):

    def __init__(self, db, lang):
        Thread.__init__(self)
        self.db = db
        self.lang = lang
        self.conn = utils.get_conn()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            language = q.get()
            amid = language["_id"]
            langid = language["id"]
            self.do_json(amid, langid)
            self.do_srt(amid, langid)
            q.task_done()

    def do_json(self, amid, langid):
        query = "/api2/partners/videos/{}/languages/{}/subtitles/?format=json"
        query = query.format(amid, langid)
        logger.debug("Query: {}".format(query))
        try:
            doc = utils.get_response_json(self.conn, query)
            doc["_id"] = amid
            self.db.video_subtitles.insert(doc)
        except:
            message = "JSON problem on {}/{} - {}"
            logger.error(message.format(amid, langid, sys.exc_info()[0]))

    def do_srt(self, amid, langid):
        query = "/api2/partners/videos/{}/languages/{}/subtitles/?format=srt"
        query = query.format(amid, langid)
        logger.debug("Query: {}".format(query))
##        try:
        response = utils.get_response(self.conn, query)
##            response = re.sub("\r\r","\r", response, re.MULTILINE)
        doc = {"_id": amid, "srt": response}
        self.db.video_subtitles_srt.insert(doc)
        filename = "{}{}.srt".format(dir_pages_srt, amid)
        utils.save_text_binary(filename, response.encode('utf8'))
##        except:
##            message = "SRT problem on {}/{} - {}"
##            logger.error(message.format(amid, langid, sys.exc_info()[0]))


@utils.entry_point
def main():
    logger.info("START subtitles")
    work()
    logger.info("DONE subtitles")
