import os
import re
from kagen import utils

def work(filename):
    srt = open(filename, encoding="utf-8")
    lines = [line.strip("\ufeff\n") for line in srt.readlines()]
    srt.close()

    errs = []
    titles = []
    title = None
    data = None
    id = 0

    for i in range(len(lines)):
        line = lines[i]
        if i == 0 or line == "":
            id += 1
            data = []
            title = {"id": id, "row": i+2, "data": data}
            titles.append(title)
        if i == 0 or line != "":
            data.append(line)

    validate_sections(titles, errs)
    validate_order(titles, errs)
    validate_times(titles, errs)
    validate_trim(titles, errs)

    print("Errors in {}:".format(filename))
    [print("\t{}".format(err)) for err in errs]


def add_error(row, kind, message, errs):
    errs.append("{} error at [{}]: {}".format(kind, row, message))

def add_warning(row, kind, message, errs):
    errs.append("{} warning at [{}]: {}".format(kind, row, message))

def validate_sections(titles, errs):
    kind = "Sections"
    for title in titles:
        if len(title["data"]) < 3:
            add_error(title["row"], kind, "Not enough lines per title", errs)
        if len(title["data"]) > 4:
            add_warning(title["row"], kind, "Too many lines per title", errs)

def validate_order(titles, errs):
    kind = "Order"
    id = 1
    for title in titles:
        if not len(title["data"]):
            continue
        data0 = title["data"][0]
        if id == -1:
            try:
                id = int(data0)
            except ValueError:
                add_error(title["row"], kind, "Not a number", errs)
                id = -1
        if data0 != str(id):
            add_error(title["row"], kind, "ID missmatch", errs)
            id = -1
        else:
            id += 1

def validate_times(titles, errs):
    kind = "Times"
    pattern = r'^\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d$'
    for title in titles:
        if len(title["data"]) < 2:
            continue
        line = title["data"][1]
        if not(re.match(pattern, line, re.M|re.I)):
            add_error(title["row"]+1, kind, "Time missmatch", errs)

def validate_trim(titles, errs):
    kind = "Trim"
    for title in titles:
        for line in title["data"]:
            if len(line) != len(line.strip()):
                add_error(title["row"]+1, kind, "Extra spaces", errs)


@utils.entry_point
def main():
    for filename in os.listdir("."):
        if filename.endswith(".srt"):
            work(filename)
