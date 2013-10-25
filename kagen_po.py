import re
import os

##path = "C:\Workspace\Khan\_high_priority_content"

def do_file(path, filename):
    f = open("{}\{}".format(path, filename), "r", encoding="utf-8")
    ten = ""
    tsr = ""
    tcnt = 0
    tcntsr = 0

    for line in f:
        if line[:5] == "msgid":
            ten = line[6:].strip('"\n')
        if line[:6] == "msgstr":
            tsr = line[7:].strip('"\n')
            print(ten, end='\n')
            cnt = len(re.findall(r'\w+', tsr))
            tcnt += cnt
            print("\twords: {}".format(cnt))
            print("\ttrans: {}".format(tsr if ten != tsr else "none"), end='\n')
            tcntsr += cnt if ten != tsr else 0

    return [tcnt, tcntsr]

def do_folder(path):
    total = 0
    total_l10n = 0

    for filename in os.listdir(path):
        if filename.endswith(".po"):
            cnt = do_file(path, filename)
            total += cnt[0]
            total_l10n += cnt[1]
            print("File {}\n\tTotal words: {}".format(filename, cnt))

    print("\nTotal words: {}, translated: {}".format(total, total_l10n))


do_file("C:\Workspace\Khan\_high_priority_content", "learn.math.algebra.exercises-sr.po")
print("\n\n")

##do_folder("C:\Workspace\Khan\_high_priority_content")
##print("\n\n")
##
##do_folder("C:\Workspace\Khan\_high_priority_platform")
##print("\n\n")
