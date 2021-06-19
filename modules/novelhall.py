import urllib
import urllib.request
import queue

from modules.utilities import *


def ParseMainBookPage(bookLink, startChapter=1):
    print("NovelFull - \"{}\"".format(bookLink))
    req = urllib.request.Request(bookLink, headers={'User-Agent' : "NovelHall-Lover"})
    con = urllib.request.urlopen( req )
    html = con.read().decode()

    ret = []
    # Book Title
    readLoc = HTML_LocatePosition("<div class=\"book-info\">", html)
    readLoc = HTML_LocateEndPosition("<h1>", html, readLoc)
    ret.append(HTML_ExtractContents(html[readLoc:], '</h1>')[:-1])

    # Authors - TODO
    #readLoc = HTML_LocatePosition("<h3 class=\"title\">", html)
    #readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    
    # Chapter startChapter
    generatedName = "".join(["Chapter ", str(startChapter)])
    readLoc = HTML_LocatePosition("All Section Catalog", html)
    readLoc = HTML_LocatePosition(generatedName, html, readLoc)
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    readLoc = HTML_LocateEndPosition("href=", html, readLoc)
    chapterUrl = HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]
    ret.append(chapterUrl)
    return ret

def ExtractNextLink(baseLink, html):
    readLoc = HTML_LocatePosition("rel=\"next\">Next</a>", html)
    # Is this the last chapter?
    if readLoc == 0:
        return None
        # Continue on...
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    readLoc = HTML_LocateEndPosition("href=", html, readLoc)
    return "".join([baseLink, HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]])
def ExtractChapterTitle(html):
    readLoc = HTML_LocateEndPosition("<div class=\"single-header\">", html)
    readLoc = HTML_LocateEndPosition("<h1 style=\"text-align: center;\">", html, readLoc)
    return HTML_ExtractContents(html[readLoc:], "</h1>")[:-1]
def ExtractChapterContent(html):
    readLoc = HTML_LocatePosition("class=\"entry-content\" id=\"htmlContent\"", html)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    stopLoc = HTML_LocatePosition("</article>", html, readLoc)
    return html[readLoc:stopLoc-1]
def ChainLoadPages(startLink, pageQueue, haltAfterChapter=0, startChapter=1):
    baseLink = "https://novelhall.com"
    nextLink = "".join([baseLink,startLink])
    currentChapter = startChapter
    while True:
        try:
            req = urllib.request.Request(nextLink, headers={'User-Agent' : "Magic Browser"})
            con = urllib.request.urlopen( req )
            html = con.read().decode()
            print("Chapter - \"{}\"".format(nextLink))
            if haltAfterChapter and currentChapter > haltAfterChapter:
                break
            # Extract the title of the page
            chapterTitle = ExtractChapterTitle(html)
            # Extract page contents
            chapterContent = ExtractChapterContent(html)
            
            # Remove ad tags
            chapterContent = HTML_WipeTagContents(chapterContent, "<script", "</script>")
            chapterContent = HTML_WipeTag(chapterContent, "</div>").strip()

            # Add the final result to the queue for writing
            pageQueue.put((chapterTitle, chapterContent, currentChapter))
            # Extract the NEXT link
            nextLink = ExtractNextLink(baseLink, html)
            if nextLink == None:
                break
            currentChapter+=1
        except KeyboardInterrupt:
            return









































a = """


_preScan    = "All Section Catalog"
_startTag   = "<li id=\"post-11\" class"
_endTag     = "</li>"

url = "https://www.novelhall.com/the-yun-familys-ninth-child-is-an-imp-14966/"
_urlBase = "https://www.novelhall.com/"

_chapterList = {}


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
    except KeyboardInterrupt:
        exit()
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
    except KeyboardInterrupt:
        exit()
    except:
        print("Skipping chapter {0}".format(x))
        continue




"""