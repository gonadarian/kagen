import os
import csv
import json
import pymongo
from kagen import utils
from kagen.utils import config
from datetime import datetime


logger = utils.get_logger("khan")


def work():
    khan = utils.get_conn_khan()
    db = utils.get_conn_mongo()
    dtf = "%Y-%m-%dT%H:%M:%SZ"

    doc = utils.get_response_json(khan, "/api/v1/playlists")
    for item in doc:
        item["_id"] = item["id"]
    for playlist in doc:
        playlist["backup_timestamp"] = datetime.strptime(playlist["backup_timestamp"], dtf)
    db.playlists.drop()
    db.playlists.insert(doc)
    logger.info("loaded {} items in playlists collection".format(len(doc)))

    doc = utils.get_response_json(khan, "/api/v1/playlists/library")
    db.playlists_library.drop()
    db.playlists_library.insert(doc)
    logger.info("loaded {} items in playlists_library collection".format(len(doc)))

    doc = utils.get_response_json(khan, "/api/v1/playlists/library/list")
    for playlist in doc:
        playlist["_id"] = playlist["id"]
        playlist["backup_timestamp"] = datetime.strptime(playlist["backup_timestamp"], dtf)
    db.playlists_library_list.drop()
    db.playlists_library_list.insert(doc)
    logger.info("loaded {} items in playlists_library_list collection".format(len(doc)))

    videos = []
    ids = []
    for playlist in doc:
        for video in playlist["videos"]:
            video_id = video["id"]
            if video_id not in ids:
                video["_id"] = video_id
                videos.append(video)
                ids.append(video_id)
            video["date_added"] = datetime.strptime(video["date_added"], dtf)
            video["backup_timestamp"] = datetime.strptime(video["backup_timestamp"], dtf)
    db.video_list.drop()
    db.video_list.insert(videos)
    logger.info("loaded {} items in video_list collection".format(len(videos)))


@utils.entry_point
def main():
    logger.info("START khan")
    work()
    logger.info("DONE khan")
