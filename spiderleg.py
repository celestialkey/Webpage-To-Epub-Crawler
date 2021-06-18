#!/usr/bin/env python3
# pip3 install EbookLib
import re
#from urllib.request import urlopen
import urllib
import urllib.request
import time

import sys
import queue

from ebooklib import epub

def EPUB_GenerateEpub(bookTitle, chapterQueue, authors, startChapter=0, endChapter=0):
    outBook = epub.EpubBook()

    # Setup generals
    outBook.set_title(bookTitle)
    outBook.set_language("en")

    # Assign authors
    for author in authors:
        outBook.add_author(author)

    # Create chapters
    chapters = []
    while True:
        try:
            chapterTitle, chapterContent, chapterNumber = chapterQueue.get(block=False)
            chapterFilename = "".join(["ch_", str(chapterNumber), ".xhtml"])
            chapter = epub.EpubHtml(title=chapterTitle, file_name=chapterFilename, lang="en")
            chapter.content = "".join(["<html><body>", chapterContent, "</body></html>"])
            outBook.add_item(chapter)
            # Preserve it for later
            chapters.append(chapter)
        except queue.Empty:
            break
        except KeyboardInterrupt:
            break

    # Default NCX/NAV file
    outBook.add_item(epub.EpubNcx())
    outBook.add_item(epub.EpubNav())
    
    # define CSS style
    style = 'BODY {color: white; font-size: 13px;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    outBook.add_item(nav_css)

    # Create book spine
    outBook.spine = ['nav'] + chapters

    # Generate filename
    tmpTitle = bookTitle.replace(" ", "")
    outTitle = ""
    if endChapter > 0:
        outTitle = "".join([tmpTitle, "_", str(startChapter), "-", str(endChapter), ".epub"])
    else:
        outTitle = "".join([tmpTitle, ".epub"])
    epub.write_epub(outTitle, outBook, {})
    print(f"Done! - {outTitle}")

def HTML_LocatePosition(uniqueId, searchBuffer, startOffset=0):
    return searchBuffer.find(uniqueId, startOffset)+1
def HTML_LocateEndPosition(uniqueId, searchBuffer, startOffset=0):
    return searchBuffer.find(uniqueId, startOffset)+len(uniqueId)
def HTML_LocateTagStartFromPosition(searchBuffer, stopPosition):
    return searchBuffer.rfind("<", 0, stopPosition)
def HTML_LocateParentTagStartFromInsideCurrentTag(searchBuffer, stopPosition, searchTag="<"):
    exitCurrentTag = searchBuffer.rfind("<", 0, stopPosition)
    return searchBuffer.rfind(searchTag, 0, exitCurrentTag)
def HTML_LocateTagEndFromPosition(searchBuffer, startOffset=0):
    return searchBuffer.find(">", startOffset)+1
def HTML_ExtractContents(contentBuffer, endDelimiter="\""):
    lastPos = HTML_LocatePosition(endDelimiter, contentBuffer)
    return contentBuffer[:lastPos]
def HTML_WipeTag(html, targetTag):
    outText = []
    startLoc = 0
    while True:
        badStart = HTML_LocatePosition(targetTag, html, startLoc)-1
        if badStart == -1:
            outText.append(html[startLoc:])
            break
        outText.append(html[startLoc:badStart])
        startLoc = badStart+len(targetTag)
    if len(outText):
        return "".join(outText)
    else:
        return html 
def HTML_WipeTagContents(html, openTag, closeTag):
    outText = []
    startLoc = 0
    while True:
        badStart = HTML_LocatePosition(openTag, html, startLoc)-1
        if badStart == -1:
            outText.append(html[startLoc:])
            break
        outText.append(html[startLoc:badStart])
        badEnd = HTML_LocateEndPosition(closeTag, html, badStart)
        startLoc = badEnd
    if len(outText):
        return "".join(outText)
    else:
        return html

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

if __name__ == "__main__":
    pageQueue = queue.Queue()

    # Grab from NovelFull
    if len(sys.argv) < 3:
        print("Usage: crawler.py <site> <bookLink> [<startOnChapter>-<endOnChapter>]\n\n")
        if len(sys.argv) == 2:
            if sys.argv[1] == "-h":
                print("Site Codes")
                print("\tNF\t-\tNovelFull\n")
    
    startChapter = 1
    endChapter = 0
    if len(sys.argv) == 4:
        startChapter, endChapter = sys.argv[3].split("-")
    if sys.argv[1] == "NF":
        bookTitle, firstChapter = ParseMainBookPage(sys.argv[2], startChapter)
        ChainLoadPages(firstChapter, pageQueue, int(endChapter), int(startChapter))
        EPUB_GenerateEpub(bookTitle, pageQueue, [], int(startChapter), int(endChapter))
        
    exit()
