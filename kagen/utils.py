import os
import sys
import json
import base64
import logging
import pymongo
import http.client
from time import time
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation


path = os.path.dirname(os.path.realpath(__file__))
os.chdir("{}/..".format(path))
config = ConfigParser(interpolation = ExtendedInterpolation())
config.read("kagen.ini")
config.read("auth.ini")
config.read("run.ini")
version = config["run"]["version"]

transifex_user = config["keys"]["transifex_user"]
transifex_pass = config["keys"]["transifex_pass"]
transifex_auth = "{}:{}".format(transifex_user, transifex_pass)
transifex_auth = base64.b64encode(bytes(transifex_auth, "latin-1"))
transifex_auth = "Basic {}".format(str(transifex_auth, "latin-1"))
headers = {
    "www.transifex.com": {
        "Authorization": transifex_auth
    },
    "www.amara.org": {
        "X-api-username": config["keys"]["amara_user"],
        "X-apikey":  config["keys"]["amara_key"]
    }
}


def entry_point(fn):
    """ Main method decorator. """
    if fn.__module__ == "__main__":
        fn()
    return fn

def decode_datetime(obj):
    """ Converts string into date time object. """
    if "created" not in obj:
        return obj
    dt = datetime.strptime(obj["created"], "%Y-%m-%dT%H:%M:%S")
    obj["created"] = dt
    return obj

def get_logger(name, level=logging.INFO):
    """ Create a logger instance with file and console handlers. """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fmt_date = config["main"]["fmt_date"]

    dir_output = config["paths"]["dir_output"]
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    fh = logging.FileHandler("{}log-{}.log".format(dir_output, name), mode="a")
    fh.setLevel(level)
    fmt_message_fh = config["main"]["fmt_message_fh"]
    fmt_fh = logging.Formatter(fmt_message_fh, datefmt=fmt_date)
    fh.setFormatter(fmt_fh)
    logger.addHandler(fh)
    fh.close()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    fmt_message_ch = config["main"]["fmt_message_fh"]
    fmt_ch = logging.Formatter(fmt_message_ch, datefmt=fmt_date)
    ch.setFormatter(fmt_ch)
    logger.addHandler(ch)

    return logger

def get_conn():
    """ Create a HTTP connection to Amara API. """
    conn = http.client.HTTPSConnection("www.amara.org")
    return conn

def get_conn_mongo():
    """ Create a MongoDB connection. """
    db = pymongo.Connection("mongodb://localhost", safe=True).kagen
    return db

def get_conn_google():
    """ Create a HTTP connection to Google Docs. """
    conn = http.client.HTTPSConnection("docs.google.com")
    return conn

def get_conn_khan():
    """ Create a HTTP connection to Khan Academy API. """
    conn = http.client.HTTPConnection("www.khanacademy.org")
    return conn

def get_conn_youtube():
    """ Create a HTTP connection to Google API. """
    conn = http.client.HTTPSConnection("www.googleapis.com")
    return conn

def get_conn_transifex():
    """ Create a HTTP connection to Transifex. """
    conn = http.client.HTTPSConnection("www.transifex.com")
    return conn

def get_response(conn, query, decode=True):
    """ Execute API request specified by path with default authentication data
    and return unformatted content.

    """
    conn.putrequest("GET", query)
    conn.putheader("Content-type", "application/json; charset=utf-8")
    conn.putheader("Accept", "*/*")
    if conn.host in headers:
        for name, value in headers[conn.host].items():
            conn.putheader(name, value)
    conn.endheaders()

    response  = conn.getresponse().read()
    if decode:
        response = response.decode()

    return response

def get_response_json(conn, path, decode=True):
    """ Load content for given URL query using given connection
    and parse it as JSON.

    """
    doc = get_response(conn, path, decode)
    return json.loads(doc, encoding="utf-8")

def get_video_csv(key, gid):
    """ Load content for given URL query using given connection
    and parse it as JSON.

    """
    conn = get_conn_google()
    path = "/spreadsheet/pub?key={}&single=true&gid={}&output=csv"
    path = path.format(key, gid)
    doc = get_response(conn, path)
    return doc

def save_json(filename, jdoc):
    """ Save JSON object to file with given filename
    using some default formating rules,
    overwritting existing content in the process.

    """
    fout = open(filename, "wt", encoding="utf-8")
    doc = json.dump(jdoc, fout, indent=1, sort_keys=True, ensure_ascii=False)
    fout.close()

def save_text(filename, doc):
    """ Save text to file with given filename,
    overwritting existing content in the process.

    """
    fout = open(filename, "wt", encoding="utf-8")
    fout.write(doc)
    fout.close()

def save_text_binary(filename, doc):
    """ Save text to file with given filename using binary mode,
    overwritting existing content in the process.

    """
    fout = open(filename, "wb")
    fout.write(doc)
    fout.close()

def load_json(filename):
    """ Load file content and parse it as JSON expression."""
    fin = open(filename, encoding="utf-8")
    doc = json.load(fin, encoding="utf-8", object_hook=decode_datetime)
    fin.close
    return doc

def load_text(filename):
    """ Load file content and return it without any processing."""
    fin = open(filename, encoding="utf-8")
    doc = fin.read()
    fin.close
    return doc

def check_time(text, tstart):
    """ Get time progress information. """
    tend = time()
    return "Total time for {} was: {:.2f} sec".format(text, tend - tstart)
