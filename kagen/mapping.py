import json
import pymongo
import http.client
import urllib.parse
from time import time
from kagen import utils
from queue import Queue
from threading import Thread
from kagen.utils import config


logger = utils.get_logger("mapping")
dir_data = config["paths"]["dir_data"]
q = Queue()


def work(filename):
    tstart = time()
    conn = utils.get_conn()
    db = utils.get_conn_mongo()
    pool_size = int(config["main"]["thread_pool_size"])

    errors = utils.load_json("{}{}".format(dir_data, filename))
    videos = db.video_list.find({}, {"youtube_id": True })

    [MappingGetter(db, errors) for i in range(pool_size)]

    for video in videos:
        ytid = video["youtube_id"]
        if not db.video_mappings.find_one({"_id": ytid}):
            q.put(ytid)

    q.join()

    logger.info(utils.check_time("mapping", tstart))


class MappingGetter(Thread):

    def __init__(self, db, errors):
        Thread.__init__(self)
        self.db = db
        self.errors = errors
        self.conn = utils.get_conn()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            ytid = q.get()
            self.doit(ytid)
            q.task_done()

    def doit(self, ytid):
        amid = None
        yt = "http://www.youtube.com/watch?v=" + ytid
        query = "/api2/partners/videos/?{}"
        query = query.format(urllib.parse.urlencode({'video_url': yt}))
        doc = utils.get_response_json(self.conn, query)
        try:
            amid = doc["objects"][0]["id"]
        except:
            if ytid in self.errors["mappings"]:
                amid = self.errors["mappings"][ytid]["amid"]
                logger.warning("ERROR CORRECTED - ytid: %s, amid: %s", ytid, amid)
            else:
                logger.error("ERROR - ytid: %s", ytid)
        if amid:
            mapping = {"_id": ytid, "amid": amid }
            self.db.video_mappings.update({"_id": ytid}, mapping, upsert=True)


@utils.entry_point
def main():
    logger.info("START mapping")
    work("mapping-errors.json")
    logger.info("DONE mapping")

