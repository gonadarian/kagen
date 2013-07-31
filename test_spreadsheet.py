import os
import json
import amara
import csv


def test():
    sample1 = "1,Math,Arithmetic and Pre-Algebra,Addition and subtraction,Basic Addition,http://www.khanacademy.org/video/basic-addition,AuX7nPBqDts,2/1/2012,2/20/2011,Y,B5k-CoJfmLs,YXBcJNWUwGo,izVE03egWV8,,G8YSITorz8E,bfDACTDYQy0,,,CRw6SfrA11I,MZ2TVE7bYlE,xG5w2fe0v-I,zeWxoUEL6u0,,,,ECPcrOWhihM,b2h-VdNbh68,W41_ld28jJI,,lmKJb9-ib48,,U-q-Y2CKMlM,"
    sample2 = "2,Math,Arithmetic and Pre-Algebra,Addition and subtraction,Basic Subtraction,http://www.khanacademy.org/video/basic-subtraction,aNqG4ChKShI,2/1/2012,2/20/2011,Y,OIyFSAb9m6Y,4r4bGqjPBak,iBZkAj70j20,,Dn_tv0leLHM,74uOYHYy0vU,,,RdI6ax_fThw,,4oUHdjxy09U,,,,,pbksceHcC2M,3H2OFMVzHqw,b_-ulxjtlTw,,,,hR_qaLojlTY,"
    sample3 = "3,Math,Arithmetic and Pre-Algebra,Addition and subtraction,Addition 2,http://www.khanacademy.org/video/addition-2,t2L3JFOqTEk,2/1/2012,2/20/2011,Y,z7qRs8c1G-I,8lGOJ3vxLoc,Xlwc1vx1kKo,,YJKUTh-8Ic4,b3gAxIl3XA0,,,78gvHgHrsbk,-ZbyF5VEo8M,zZniuXdZHP4,DI2zbqNrWJI,,,,ZBV9i7Cr50s,aQo9AAV_QcQ,aVjVAtV7s2s,,ghQ8zOn7rWE,,yvzdnAWl0Cg,"
    samples = [sample1, sample2, sample3]
    fields = ["serial", "subject", "topic", "sub_topic", "title", "ka_url", "ytid_en", "date_added", "date_created", "subtitled", "ytid_ar", "ytid_bi", "ytid_ba", "ytid_bu", "ytid_de", "ytid_es", "ytid_fa", "ytid_fr", "ytid_gr", "ytid_he", "ytid_it", "ytid_ki", "ytid_ma", "ytid_mo", "ytid_no", "ytid_pl", "ytid_po", "ytid_ru", "ytid_th", "ytid_tu", "ytid_uk", "ytid_ur", "ytid_xs"]
    reader = csv.DictReader(samples, fields, delimiter=",", quoting=csv.QUOTE_NONE, quotechar="", strict=True)
    out = json.dumps([row for row in reader], indent=1 )
    print(out)

@amara.entry_point
def main():
    test()
