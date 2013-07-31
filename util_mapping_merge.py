from os import listdir
from os.path import isfile, join
import json
import amara


config = amara.get_config()
folder = config["paths"]["dir_output"]


def work():
    d = {}
    for f in (f for f in listdir("{}Mapping".format(folder)) if isfile(join(folder,"Mapping",f))):
        j = amara.load_json("{}Mapping/{}".format(folder, f))
        for k, v in j.items():
            d[k]=v

    amara.save_json("{}{}".format(folder, "mapping.txt"), d)


@amara.entry_point
def main():
    work()
