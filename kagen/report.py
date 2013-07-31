import json
from kagen import utils
from kagen.utils import config


logger = utils.get_logger("report")
dir_videos = config["paths"]["dir_videos"]
dir_mapping = config["paths"]["dir_mapping"]
dir_langs = config["paths"]["dir_languages"]
dir_subs = config["paths"]["dir_subtitles"]
dir_reports = config["paths"]["dir_reports"]


def work(filename):
    path = "{}{}".format(dir_videos, filename)
    jpls = utils.load_json(path)
    for playlist, videos in jpls["playlists"].items():
        logger.info("Playlist: %s", playlist)
        report(playlist, videos)

def report(playlist, videos):
    rpls = []
    report = {"report": {"playlist": playlist, "data": rpls}}

    jlngs = utils.load_json("{}playlist-lang-{}.json".format(dir_langs, playlist))
    jmaps = utils.load_json("{}playlist-{}.json".format(dir_mapping, playlist))
    jsubs = utils.load_json("{}subtitle-{}.json".format(dir_subs, playlist))

    jlngspl = jlngs[playlist]
    jsubspl = jsubs[playlist]

    for ytid, amid in jmaps[playlist].items():
        jlng = jlngspl[amid]
        if ytid not in videos:
            continue
        video = videos[ytid]
        rvid = {"amara_id": amid, "youtube_id": ytid, "serial": video["serial"]}
        rpls.append(rvid)

        if "id" in jlng:
            rvid["ka_url"] = video["ka_url"]
            rvid["subtitle_id"] = jlng["id"]
            rvid["title"] = jlng["title"]
            rvid["description"] = jlng["description"]
            rvid["subtitle_count"] = jlng["subtitle_count"]
            rvid["percent_done"] = jlng["percent_done"]

            rvidrevs = []
            rvid["revisions"] = rvidrevs
            for jlngver in jlng["versions"]:
                rev = jlngver["version_no"]
                author = jlngver["author"]
                change = jlngver["text_change"]
                count = jlng["subtitle_count"]
                if count == 0:
                    change = 0
                elif jlngver["version_no"] == 0:
                    change = jsubspl[amid] / count

                rvidrev = {"no": rev, "author": author, "change": change*100}
                rvidrevs.append(rvidrev)

    filename = "{}playlist-report-{}.json".format(dir_reports, playlist)
    utils.save_json(filename, report)
    logger.info("SAVED FILE - %s", filename)


@utils.entry_point
def main():
    logger.info("START reports")
    work("videos-all-structured.json")
    logger.info("DONE reports")
