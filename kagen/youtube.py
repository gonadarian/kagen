import os
import csv
import json
import pymongo
from kagen import utils
from kagen.utils import config
from datetime import datetime


logger = utils.get_logger("youtube")


def work():
    dtf = "%Y-%m-%dT%H:%M:%S.%fZ"
    yt_key = config["keys"]["youtube_key"]
    yt_user = config["run"]["youtube_user"]
    youtube = utils.get_conn_youtube()
    db = utils.get_conn_mongo()

    query_base = "/youtube/v3/channels?part=id&forUsername={}&maxResults=50&key={}"
    query = query_base.format(yt_user, yt_key)
    doc = utils.get_response_json(youtube, query)
    chid = doc["items"][0]["id"]
    logger.info("Channel ID: {}".format(chid))

    playlists = []
    query_base = "/youtube/v3/playlists?part=snippet&channelId={}&maxResults=50&key={}"
    query = query_base.format(chid, yt_key)
    doc = utils.get_response_json(youtube, query)
    playlists.extend(doc["items"])
    logger.info("Playlist count: {}".format(len(playlists)))

    query_base = "/youtube/v3/playlistItems?part=contentDetails&playlistId={}&maxResults=50&key={}"
    for playlist in playlists:
        plid = playlist["id"]
        query = query_base.format(plid, yt_key)
        doc = utils.get_response_json(youtube, query)
        playlist["items"] = doc["items"]

    for playlist in playlists:
        playlist["_id"] = playlist["id"]
        playlist["etag"] = playlist["etag"].strip("\"")
        playlist.update(playlist["snippet"])
        del(playlist["snippet"])
        playlist["publishedAt"] = datetime.strptime(playlist["publishedAt"], dtf)
        for item in playlist["items"]:
            item["ytid"] = item["contentDetails"]["videoId"]
            del(item["contentDetails"])

    db.youtube_playlists.drop()
    db.youtube_playlists.insert(playlists)

    videos = []
    ytids = []
    for playlist in playlists:
        message = "\tPlaylist '{}' count: {}"
        logger.info(message.format(playlist["_id"], len(playlist["items"])))
        for item in playlist["items"]:
            ytid = item["ytid"]
            query = "/youtube/v3/videos?part=snippet&id={}&maxResults=50&key={}"
            query = query.format(ytid, yt_key)
            doc = utils.get_response_json(youtube, query)
            for video in doc["items"]:
                if ytid not in ytids:
                    videos.append(video)
                    ytids.append(ytid)
                else:
                    logger.warn("\t\tDuplicate video ID: {}".format(ytid))

    for video in videos:
        video["_id"] = video["id"]
        video["etag"] = video["etag"].strip("\"")
        video.update(video["snippet"])
        del(video["snippet"])
        video["publishedAt"] = datetime.strptime(video["publishedAt"], dtf)
        video["categoryId"] = int(video["categoryId"])

    db.youtube_videos.drop()
    db.youtube_videos.insert(videos)


@utils.entry_point
def main():
    logger.info("START youtube")
    work()
    logger.info("DONE youtube")
