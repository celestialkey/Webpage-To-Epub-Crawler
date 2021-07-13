import urllib
import urllib.request
import queue

from modules.utilities import *


def ParseMainBookPage(bookLink, startChapter=1):
    print("1stKissNovel - \"{}\"".format(bookLink))
    req = urllib.request.Request(bookLink, headers={'User-Agent' : "1stKissNovel-Lover"})
    con = urllib.request.urlopen( req )
    html = con.read().decode()

    ret = []
    # Book Title
    readLoc = HTML_LocatePosition(f"<title>", html)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    ret.append(HTML_ExtractContents(html[readLoc:], '</title>')[:-1].split("-")[0].strip())

    # Authors - TODO
    #readLoc = HTML_LocatePosition("<h3 class=\"title\">", html)
    #readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    
    # Chapter startChapter
    # No need to search for stuff. The way the main page loads
    # includes a delayed load for the chapter listings. Will have
    # to pass in the chapter link instead of book link
    ret.append(bookLink.replace("https://1stkissnovel.love/novel/", ""))
    return ret
def ExtractNextLink(baseLink, html):
    readLoc = HTML_LocatePosition("class=\"btn next_page\"", html)
    endTestLoc = HTML_LocatePosition("class=\"btn next_page\"", html)
    readLoc = HTML_LocateTagStartFromPosition(html, readLoc)
    # Is this the last chapter?
    if endTestLoc != -1 and endTestLoc == 0:
        return None
    # Continue on...
    readLoc = HTML_LocateEndPosition("href=", html, readLoc)
    return "".join(["", HTML_ExtractContents(html[readLoc+1:], "\"")[:-1]])
def ExtractChapterTitle(html):
    readLoc = HTML_LocatePosition(f"<title>", html)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    return HTML_ExtractContents(html[readLoc:], '</title>')[:-1].strip()
def ExtractChapterContent(html):
    readLoc = HTML_LocatePosition("<div class=\"reading-content\">", html)
    readLoc = HTML_LocatePosition("<div class=\"text-left\">", html, readLoc)
    readLoc = HTML_LocateTagEndFromPosition(html, readLoc)
    readLoc = HTML_LocatePosition("<p>", html, readLoc)-1
    return HTML_ExtractContents(html[readLoc:], "</div>")[:-1]
def ChainLoadPages(startLink, pageQueue, haltAfterChapter=0, startChapter=1):
    baseLink = "https://1stkissnovel.love/novel/"
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
            # ! No need to remove ads with 1stKissNovel
            #chapterContent = HTML_WipeTagContents(chapterContent, "<div class", "</div>") # Potential issue
            #chapterContent = HTML_WipeTag(chapterContent, "</div>")
            # Add the final result to the queue for writing
            pageQueue.put((chapterTitle, chapterContent, currentChapter))
            #print(f"Queue of size: {pageQueue.qsize()} : {chapterContent[:30]}")
            # Extract the NEXT link
            nextLink = ExtractNextLink(baseLink, html)
            if nextLink == None:
                break
            currentChapter+=1
        except KeyboardInterrupt:
            return
