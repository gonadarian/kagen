import sys
import json
import time
import pymongo
import threading
from kagen import utils
from queue import Queue
from threading import Thread
from datetime import datetime
from kagen.utils import config


logger = utils.get_logger("languages")
dir_data = config["paths"]["dir_data"]
q = Queue()
dtf = "%Y-%m-%dT%H:%M:%S"


def work():
    tstart = time.time()
    lang = config["main"]["language"]
    mode = config["run"]["mode"]
    pool_size = int(config["main"]["thread_pool_size"])

    db = utils.get_conn_mongo()
    mappings = db.video_mappings.find({}, {"amid": True })
    amids = [mapping["amid"] for mapping in mappings]
    errors = utils.load_json("{}language-errors.json".format(dir_data))

    [LangGetter(db, lang, errors) for i in range(pool_size)]

    db.video_languages.drop()
    for amid in amids:
        # get all entries for "full" mode, only new ones otherwise (faster)
        if mode == "full" or not db.video_languages.find_one({"_id": amid}):
            q.put(amid)

    q.join()

    logger.info(utils.check_time("languages", tstart))


class LangGetter(Thread):

    def __init__(self, db, lang, errors):
        Thread.__init__(self)
        self.db = db
        self.lang = lang
        self.errors = errors
        self.conn = utils.get_conn()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            amid = q.get()
            self.doit(amid)
            q.task_done()

    def doit(self, amid):
        langid = self.lang
        if amid in self.errors:
            langid = self.errors[amid]["good"]
        query = "/api2/partners/videos/{}/languages/{}/"
        query = query.format(amid, langid)

        response = utils.get_response(self.conn, query)
        if response == "No such language for this video":
            return
        try:
            doc = json.loads(response, encoding="utf-8")
            doc["_id"] = amid
            doc["created"] = datetime.strptime(doc["created"], dtf)
            self.db.video_languages.insert(doc)
            message = "found new title in {} for {}"
            logger.debug(message.format(self.lang, amid))
        except:
            message = "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1])
            logger.error(message)


@utils.entry_point
def main():
    logger.info("START languages")
    work()
    logger.info("DONE languages")
