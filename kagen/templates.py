import os
import re
import json
import shutil
import gettext
from kagen import utils
from kagen.utils import config
from django import template
from datetime import datetime
from django.conf import settings
from django.utils import translation
from django.utils.text import slugify
from django.utils.datastructures import SortedDict
from django.template import Context, Template, loader
from django.utils.translation import ugettext as _


logger = utils.get_logger("templates")
whitespace = re.compile('^\s*\n', re.MULTILINE)
dir_data = config["paths"]["dir_data"]
dir_pages = config["paths"]["dir_pages"]
dir_resources = config["paths"]["dir_resources"]


def work():
    lang = config["main"]["language"]
    translation.activate(lang)
    db = utils.get_conn_mongo()
    mappings = utils.load_json("{}{}".format(dir_data, "youtube-mappings.json"))

    # preparing data for tutorial htmls

    files = []
    template = loader.get_template("playlist.html")
    hierarchy = db.video_hierarchy.find()
    pages = prep_pages(hierarchy)
    tutorials = []
    for slug in pages:
        page = pages[slug]
        data = prep_page(page, db, mappings)
        if data and data["tutorials"]:
            tutorials.extend(data["tutorials"])
        if data:
            filename = "index.html"
            path = "{}{}{}/".format(dir_pages, data["path"], data["page"])
            save_page(template, data, path, filename)
            files.append("{}{}/{}".format(data["path"], data["page"], filename))

    # preparing data for index html

    filename = "index.html"
    template = loader.get_template(filename)
    data = prep_index(tutorials)
    save_page(template, data, dir_pages, filename)

    # preparing data for videos html

    filename = "videos.html"
    template = loader.get_template(filename)
    videos = db.video_languages.find()
    data = prep_videos(db, videos)
    save_page(template, data, dir_pages, filename)
    files.append(filename)

    # preparing data for video htmls

    template = loader.get_template("video.html")
    for tutorial in tutorials:
        message = "Generating video pages for {} at {}"
        logger.info(message.format(tutorial["path"], tutorial["page"]))
        for video in tutorial["videos"]:
            amid = video["amid"]
            data = prep_video(tutorial, video)
            if data:
                path = "{}{}{}/".format(dir_pages, tutorial["path"], tutorial["page"])
                filename = "video-en-{}.html".format(video["ytid"])
                save_page(template, data, path, filename)
                if "sync" in video:
                    data["sr"] = True
                    ytid_sr = video["sync"]["id"]
                    filename = "video-sr-{}.html".format(ytid_sr)
                    save_page(template, data, path, filename)

    # preparing data for sitemap xml

    filename = "sitemap.xml"
    template = loader.get_template(filename)
    data = prep_sitemap(files)
    save_page(template, data, dir_pages, filename)

    copy_resources(dir_resources, dir_pages)

def prep_index(data):
    return {"tutorials": data, "root": ""}

def prep_sitemap(files):
    return {"files": files, "root": ""}

def prep_pages(hierarchy):
    pages = {}
    for tutorial in hierarchy:
        slug = slugify(tutorial["subject"])
        slug = "{}/{}".format(slug, slugify(tutorial["topic"]))
        slug = "{}/{}".format(slug, slugify(tutorial["sub_topic"]))
        if slug not in pages:
            pages[slug] = []
        pages[slug].append(tutorial)

    return pages

def prep_page(page, db, mappings):
    data = {}
    subject = page[0]["subject"]
    topic = page[0]["topic"]
    sub_topic = page[0]["sub_topic"]
    data["subject"] = subject
    data["topic"] = topic
    data["sub_topic"] = sub_topic
    if sub_topic:
        data["level"] = 2
        data["page"] = slugify(sub_topic)
        data["path"] = "{}/{}/".format(slugify(subject), slugify(topic))
        data["subtitle"] = "{} - {} - {}".format(_(sub_topic), _(topic), _(subject))
    elif topic:
        data["level"] = 1
        data["page"] = slugify(topic)
        data["path"] = "{}/".format(slugify(subject), )
        data["subtitle"] = "{} - {}".format(_(topic), _(subject))
    else:
        data["level"] = 0
        data["page"] = slugify(subject)
        data["path"] = ""
        data["subtitle"] = _(subject)

    tutorials = []
    for tutorial in page:
        videos = []
        tutorial["videos"] = videos
        tutorial["page"] = data["page"]
        tutorial["path"] = data["path"]
        tutorial["level"] = data["level"]
        for ytid in tutorial["ytids"]:
            video = {"ytid": ytid}
            # TODO should be done on mongo side...
            mapping = db.video_mappings.find_one({"_id": ytid})
            if not mapping:
                logger.warning("\tMissing mapping for ytid {}".format(ytid))
                continue
            amid = mapping["amid"]
            if not amid:
                continue
            video["amid"] = amid
            language = db.video_languages.find_one({"_id": amid})
            if not language:
                continue
            versions = language["versions"]
            if not versions or not len(versions):
                continue
            for version in versions:
                version["time_change"] = version["time_change"] * 100
                version["text_change"] = version["text_change"] * 100
            video["amara"] = language
            ka = db.video_list.find_one({"youtube_id": ytid})
            video["ka"] = ka
            sub = db.video_subtitles.find_one({"_id": amid})
            video["subtitle"] = sub
            # TODO prepare on mongo side...
            sheet = db.spreadsheet.find_one({"_id": ytid}, {"ytid_sr": 1})
            ytid_sr = sheet["ytid_sr"]
            if not ytid_sr and ytid in mappings:
                ytid_sr = mappings[ytid]
            if ytid_sr:
                sync = db.youtube_videos.find_one({"_id": ytid_sr})
                video["sync"] = sync
            videos.append(video)

        if len(videos):
            tutorials.append(tutorial)

    if not len(tutorials):
        return None

    data["tutorials"] = tutorials
    data["root"] = "../" * (data["level"] + 1)

    return data

def prep_video(tutorial, video):
    language = video["amara"]
    if "versions" not in language or len(language["versions"]) == 0:
        logger.warning("\tEmpty...")
        return None
    subtitle = _(language["title"])
    level = tutorial["level"]
    data = {"video": video, "subtitle": subtitle, "root": "../" * (level + 1)}

    return data

def prep_videos(db, videos):
    list = []
    for video in videos:
        if "versions" in video and len(video["versions"]) > 0:
            list.append(video)
            sub = db.video_subtitles.find_one({"_id": video["_id"]})
            video["subtitle"] = sub
    subtitle = _("List of All Videos")
    data = {"videos": list, "subtitle": subtitle, "root": ""}

    return data

def empty(doc):
    for video in doc["report"]["data"]:
        if "revisions" in video and len(video["revisions"]) > 0:
            return False
    return True

def save_page(template, data, path, filename):
    context = Context(data)
    page = template.render(context)
    page = whitespace.sub('', page)
    if not os.path.exists(path):
        os.makedirs(path)
    path = "{}{}".format(path, filename)
    utils.save_text(path, page)
    logger.info("Saved page {}".format(path))

def copy_resources(src, dest):
    files = os.listdir(src)
    for filename in files:
        path = os.path.join(src, filename)
        if (os.path.isfile(path)):
            shutil.copy(path, dest)


@utils.entry_point
def main():
    logger.info("START templates")
    settings.configure(
        DEBUG=True,
        USE_I18N=True,
        LANGUAGES = (('sr', 'Serbian'), ('en', 'English'), ('de', 'German')),
        TEMPLATE_DEBUG=True,
        LOCALE_PATHS=["locale"],
        INSTALLED_APPS=["kagen", "django.contrib.humanize"]
    )
    work()
    logger.info("DONE templates")
