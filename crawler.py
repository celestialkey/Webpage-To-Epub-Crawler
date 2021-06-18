#!/usr/bin/env python3

import re
#from urllib.request import urlopen
import urllib
import urllib.request
import time

_preScan    = "All Section Catalog"
_startTag   = "<li id=\"post-11\" class"
_endTag     = "</li>"

url = "https://www.novelhall.com/the-yun-familys-ninth-child-is-an-imp-14966/"
_urlBase = "https://www.novelhall.com/"

_chapterList = {}
_volumeBreakEvery = 40
_expectedTotalChapters = 5780
_outFileBase = ""

def GrabChunk(_str, _off):
    _s = _off
    _e = _str.find("</li>", _s)
    if _e > 0:
        _out = _str[_off:_e]
        return _out,_e+1
    else:
        return None,_e

# main page that has the chapter list
print("Targeting ULR [{}]".format(url))
req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
con = urllib.request.urlopen( req )
html = con.read().decode()

# Grab each link for each chapter from the main page
_off = html.find(_preScan) + 1
if _off < 0:
    print("Unable to find starting point [{}]".format(_preScan))
    sys.exit()

import sys
lastChapter = 0
while True:
    _off = html.find("<li id=\"post-11\" class", _off)+1
    if _off < 0: break
    _tag,_off = GrabChunk(html, _off)
    if _off < 0: break
    if _tag.find("Chapter") < 0: break
    _tagParts = _tag.split("\"")
    _tagChapter = _tagParts[-1].split(" ")[1].split("<")[0]
    try:
        if int(_tagChapter) - lastChapter != 1:
            print("{0} = {1} - {2}".format(int(_tagChapter) - lastChapter, int(_tagChapter), lastChapter))
            print("Missing chapter {0}!\n-------------------\n{1}\n---------------".format(lastChapter+1, _tagParts))
            lastChapter += (int(_tagChapter) - lastChapter)
            continue
        _chapterList[int(_tagChapter)] = _tagParts[-2]
        print("Snagged {1} - [{0}]".format(_tagParts[-2], _tagChapter))
        lastChapter += 1
    except Exception as e:
        print(_tagParts)
        print("Invalid chapter, skipping... {0}".format(e))
    
_iter = 1
_startCh = 1
_outContent = ""
_volumeBreakEvery = 200
_expectedTotalChapters = 1000
_outFileBase = "TheYunFamilysNinthChildIsAnImp_"
for x in range(_startCh,_expectedTotalChapters+1):
    try:
        _outContent += "Chapter {}\n\n".format(x)
        print("Grabbing page for chapter {0}".format(x))
        _target = _urlBase + _chapterList[x]
        req = urllib.request.Request(_target, headers={'User-Agent' : "Magic Browser"})
        con = urllib.request.urlopen( req )
        html = con.read().decode()

        _startContent = html.find('<div class="entry-content" id="htmlContent">')
        if _startContent < 0:
            print("Error! a")
        _endContent = html.find('</article>', _startContent)
        if _endContent < 0:
            print("Error! b")

        _outContent += html[_startContent:_endContent]
        _outContent += "\n\n"

        if _iter == _volumeBreakEvery or x >= _expectedTotalChapters:
            _out = _outFileBase+"{}-{}".format(_startCh,x)+".html"
            print("Writing... {}".format(_out))
            with open(_out, "a") as fout:
                fout.write(_outContent+"\n\n")
            _startCh += _iter
            _iter = 0
            _outContent = ""
        _iter += 1
    except:
        print("Skipping chapter {0}".format(x))
        continue


