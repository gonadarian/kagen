# coding: utf-8

import re
import time
import unittest
import pysrt
from kagen import utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

def work(filename, path):
    base_url = "http://www.amara.org"
    subs = pysrt.SubRipFile.open(filename)
    subs_len = len(subs)
    print(subs_len)
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(base_url + path)
    for i in range(len(subs)):
        print("{}/{} - {}".format(i, subs_len, subs[i].text))
        element = driver.find_element_by_xpath("//li[{}]/textarea".format(i+1))
        element.clear()
        element.send_keys(subs[i].text)

@utils.entry_point
def main():
    #filename = "Dividing_Whole_Numbers_and_Applications_1.sr.srt"
    #path = "/en/onsite_widget/?config=%7B%22languageCode%22%3A+%22sr%22%2C+%22task%22%3A+null%2C+%22videoURL%22%3A+%22http%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D4I9iibPLdBw%22%2C+%22mode%22%3A+null%2C+%22subLanguagePK%22%3A+611905%2C+%22baseLanguagePK%22%3A+30559%2C+%22originalLanguageCode%22%3A+%22en%22%2C+%22videoID%22%3A+%22gL8a6H74F7Ty%22%2C+%22effectiveVideoURL%22%3A+%22http%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D4I9iibPLdBw%22%7D"
    filename = "Comparing_Absolute_Values.sr.srt"
    path = "/en/onsite_widget/?config=%7B%22languageCode%22%3A+%22sr%22%2C+%22task%22%3A+null%2C+%22videoURL%22%3A+%22http%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DhKkBlcnU9pw%22%2C+%22mode%22%3A+null%2C+%22subLanguagePK%22%3A+452312%2C+%22baseLanguagePK%22%3A+156809%2C+%22originalLanguageCode%22%3A+%22en%22%2C+%22videoID%22%3A+%22R6PKFVsCuZ0t%22%2C+%22effectiveVideoURL%22%3A+%22http%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DhKkBlcnU9pw%22%7D"
    work(filename, path)
