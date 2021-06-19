import urllib
import urllib.request
import queue

from modules.utilities import *


def ParseMainBookPage(bookLink, startChapter=1):
    print("NovelFull - \"{}\"".format(bookLink))
    req = urllib.request.Request(bookLink, headers={'User-Agent' : "NovelFull-Lover"})
    con = urllib.request.urlopen( req )
    html = con.read().decode()

    ret = []
    # Book Title
    readLoc = HTML_LocatePosition("<h3 class=\"title\">", html)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    ret.append(HTML_ExtractContents(html[readLoc:], '</h3>')[:-1])

    # Authors - TODO
    #readLoc = HTML_LocatePosition("<h3 class=\"title\">", html)
    #readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    
    # Chapter startChapter
    generatedName = "".join(["title=\"Chapter ", str(startChapter)])
    readLoc = HTML_LocatePosition("<ul class=\"list-chapter\">", html)
    readLoc = HTML_LocateEndPosition(generatedName, html, readLoc)
    if html[readLoc] not in [':', ' ', '-', ';']:
        print(f"Error! Unable to locate starting chapter from provided page. {html[readLoc]}, {html[readLoc-5:readLoc+5]}")
        exit()
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    readLoc = HTML_LocateEndPosition("<a href=", html, readLoc)
    chapterUrl = HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]
    #print(f"{chapterUrl}")
    ret.append(chapterUrl)
    return ret
def ExtractNextLink(baseLink, html):
    readLoc = HTML_LocatePosition("id=\"next_chap\"", html)
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    # Is this the last chapter?
    endTestLoc = HTML_LocatePosition("disabled", html, readLoc)-1
    linkEnd = HTML_LocateTagEndFromPosition(html, readLoc)
    if endTestLoc != -1 and endTestLoc < linkEnd:
        return None
    # Continue on...
    readLoc = HTML_LocateEndPosition("href=", html, readLoc)
    return "".join([baseLink, HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]])
def ExtractChapterTitle(html):
    readLoc = HTML_LocatePosition("class=\"chapter-title\"", html)
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    readLoc = HTML_LocateEndPosition("title=", html, readLoc)
    return HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]
def ExtractChapterContent(html):
    readLoc = HTML_LocatePosition("id=\"chapter-content\"", html)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    readLoc = HTML_LocatePosition("<p>", html, readLoc)-1
    stopLoc = HTML_LocatePosition("class=\"chapter-end\"", html, readLoc)
    stopLoc = HTML_LocateTagStartFromPosition(html, stopLoc)
    return html[readLoc:stopLoc]
def ChainLoadPages(startLink, pageQueue, haltAfterChapter=0, startChapter=1):
    baseLink = "https://novelfull.com"
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
            chapterContent = HTML_WipeTagContents(chapterContent, "<div", "</div>")
            chapterContent = HTML_WipeTag(chapterContent, "</div>")
            # Add the final result to the queue for writing
            pageQueue.put((chapterTitle, chapterContent, currentChapter))
            # Extract the NEXT link
            nextLink = ExtractNextLink(baseLink, html)
            if nextLink == None:
                break
            currentChapter+=1
        except KeyboardInterrupt:
            return
