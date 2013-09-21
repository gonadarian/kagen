import os
import json
import polib
from kagen import utils


logger = utils.get_logger("transifex")


def work():
    transifex = utils.get_conn_transifex()
    resources = utils.get_response_json(transifex, "/api/2/project/kagen/resources/")

    pos = {}
    for item in resources:
        slug = item["slug"]
        logger.info("Processing resource '{}'".format(slug))
        query = "/api/2/project/kagen/resource/{}/?details".format(slug)
        res = utils.get_response_json(transifex, query)

        for lang in res["available_languages"]:
            lang_code = lang["code"]
            logger.info("\tProcessing language '{}'".format(lang_code))
            query = "/api/2/project/kagen/resource/{}/translation/{}/?file"
            query = query.format(slug, lang_code)
            file = utils.get_response(transifex, query)
            path = "./locale/{}/LC_MESSAGES".format(lang_code)
            if not os.path.exists(path):
                os.makedirs(path)
            filename = "{}/{}.po".format(path, slug)
            utils.save_text(filename, file)

            pofile = polib.pofile(filename)
            if lang_code not in pos:
                pos[lang_code] = pofile
            else:
                po = pos[lang_code]
                for entry in pofile:
                    po.append(entry)

    for lang, po in pos.items():
        logger.info("Compiling language file for '{}'".format(lang))
        po.save_as_mofile("./locale/{}/LC_MESSAGES/django.mo".format(lang))

@utils.entry_point
def main():
    logger.info("START transifex")
    work()
    logger.info("DONE transifex")
