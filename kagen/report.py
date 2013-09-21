import json
from kagen import utils
from kagen.utils import config
from datetime import date, datetime


logger = utils.get_logger("report")


def work(sub_topic):
    no = 0
    db = utils.get_conn_mongo()
    dtf = "%Y-%m-%dT%H:%M:%SZ"
    limit = datetime(2013, 5, 1, 0, 0)
    print(limit)
    tutorials = db.video_hierarchy.find({"sub_topic": sub_topic})
    for tutorial in tutorials:
        playlist = db.playlists_library_list.find_one({"_id": tutorial["_id"]})
        for video in playlist["videos"]:
            no += 1
            title = video["title"]
            url = video["ka_url"]
            ytid = video["youtube_id"]
            amid = db.video_mappings.find_one({"_id": ytid})["amid"]
            added = datetime.strptime(video["date_added"], dtf)
            skipped = "x" if limit < added else ""
            print("{}\t{}\t\t{}\t\t\t{}\t{}\t\t\t{}".format(no, title, skipped, url, amid, ytid ))


@utils.entry_point
def main():
    logger.info("START report")
##    work("Addition and subtraction")
##    work("Multiplication and division")
##    work("Factors and multiples")
    work("Negative numbers and absolute value")
##    work("Decimals")
##    work("Fractions")
##    work("Ratios, proportions, units and rates")
##    work("Applying mathematical reasoning")
##    work("Exponents, radicals, and scientific notation")
##    work("Arithmetic properties")
##    work("Telling time")
    logger.info("DONE report")
