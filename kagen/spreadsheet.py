import os
import csv
import json
import pymongo
from kagen import utils
from datetime import datetime
from kagen.utils import config


logger = utils.get_logger("spreadsheet")
dir_data = config["paths"]["dir_data"]


def work(errors):
    key = config["keys"]["google_docs"]
    gid = config["keys"]["google_docs_id"]
    doc = load_doc(key, gid)
    errors = utils.load_json("{}{}".format(dir_data, errors))
    fix_doc(doc, errors)

    db = utils.get_conn_mongo()
    db.spreadsheet.drop()
    db.spreadsheet.insert(doc["data"])

def load_doc(key, gid):
    fields = ["serial", "added", "created", "title", "subject", "topic", "sub_topic", "tutorial", "titled_id", "duration", "ytid_en", "subtitled", "ytid_ar", "ytid_am", "ytid_bi", "ytid_bm", "ytid_ba", "ytid_bu", "ytid_cz", "ytid_da", "ytid_de", "ytid_du", "ytid_es", "ytid_fa", "ytid_fr", "ytid_gr", "ytid_he", "ytid_it", "ytid_ja", "ytid_ki", "ytid_ko", "ytid_no", "ytid_pl", "ytid_po", "ytid_ru", "ytid_sr", "ytid_si", "ytid_te", "ytid_th", "ytid_tu", "ytid_ur", "ytid_xs"]
    doc = utils.get_video_csv(key, gid)
    doc = [s for idx, s in enumerate(doc.splitlines()) if idx >= 7]
    reader = csv.DictReader(doc, fields, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar="\"", strict=True)
    jdoc = {"data": [row for row in reader]}
    return jdoc

def fix_doc(doc, errors):
    for video in doc["data"]:
        ytid_en = video["ytid_en"]
        if ytid_en in errors["ids"]:
            video["ytid_en"] = errors["ids"][ytid_en]["ytid"]
        video["_id"] = video["ytid_en"]
        video["created"] = datetime.strptime(video["created"], "%m/%d/%Y")
        video["added"] = datetime.strptime(video["added"], "%m/%d/%Y")
        video["serial"] = int(video["serial"])
        video["duration"] = int(video["duration"])


@utils.entry_point
def main():
    logger.info("START spreadsheet")
    work("mapping-errors.json")
    logger.info("DONE spreadsheet")
