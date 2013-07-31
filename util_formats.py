import re
import sys
import json
import locale
import http.client
import amara


def work(amid, lang):
    conn = amara.get_conn()
    for filetype in ["srt", "ssa", "txt", "dfxp", "ttml"]:
        print(filetype)
        subtitle = get_subtitle(conn, amid, lang, filetype, 0)
        amara.save_json("Subtitles/test-subtitle-{}-{}.txt".format(filetype, amid), subtitle)

def get_subtitle(conn, amid, lang, filetype, version):
    path = "/api2/partners/videos/{}/languages/{}/subtitles/?format={}&version={}".format(amid, lang, filetype, version)
    try:
        response = amara.get_response(conn, path)
        return {"response": response}
    except:
        return {"path": path, "error": "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1])}


@amara.entry_point
def main():
    work("36ItOS7NS67B", "sr")

