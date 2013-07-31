import json
import pymongo
from kagen import utils
from kagen.utils import config


logger = utils.get_logger("hierarchy")


def work():
    pl_subject = ""
    pl_topic = ""
    pl_sub_topic = ""
    pl_tutorial = ""

    db = utils.get_conn_mongo()
    subjects = db.playlists_library.find()
    playlists = []
    for subject in subjects:
        pl_subject = subject["name"]
        for topic in subject["items"]:
            pl_topic = topic["name"]
            if "playlist" in topic:
                handle(playlists, topic["playlist"], pl_subject, pl_topic, "", pl_topic)
            else:
                for sub_topic in topic["items"]:
                    pl_sub_topic = sub_topic["name"]
                    if "playlist" in sub_topic:
                        handle(playlists, sub_topic["playlist"], pl_subject, pl_topic, pl_sub_topic, pl_sub_topic)
                    else:
                        for tutorial in sub_topic["items"]:
                            pl_tutorial = tutorial["name"]
                            if "playlist" in tutorial:
                                handle(playlists, tutorial["playlist"], pl_subject, pl_topic, pl_sub_topic, pl_tutorial)

    db.video_hierarchy.drop()
    db.video_hierarchy.insert(playlists)

def handle(playlists, playlist, subject, topic, sub_topic, tutorial):
    pl = {}
    pl["_id"] = playlist["id"]
    pl["subject"] = subject
    pl["topic"] = topic
    pl["sub_topic"] = sub_topic
    pl["tutorial"] = tutorial
    pl["ytids"] = [video["youtube_id"] for video in playlist["videos"]]

    playlists.append(pl)
    logger.info("{} - {} - {} - {}".format(subject, topic, sub_topic, tutorial))


@utils.entry_point
def main():
    logger.info("START hierarchy")
    work()
    logger.info("DONE hierarchy")
