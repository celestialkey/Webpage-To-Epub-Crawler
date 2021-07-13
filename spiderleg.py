#!/usr/bin/env python3
import datetime
import sys
import queue

from ebooklib import epub

# ./spiderleg.py NF 'https://novelfull.com/index.php/war-sovereign-soaring-the-heavens.html?page=25&per-page=50' 1248-1250

SPIDERLEG_NAME      = "SpiderLeg"
SPIDERLEG_VERSION   = "1.4"
SPIDERLEG_AUTHOR    = "Celestialkey"
SPIDERLEG_HOME      = "https://github.com/celestialkey/spiderleg-web-to-epub-crawler"

INFODUMP = \
"""<p>Chapters Pulled:&nbsp;{1}</p>
<p>Series Source:&nbsp;<a href="{2}">{2}</a></p>
<p>Home Website:&nbsp;<a href="{3}">{3}</a></p><br>
<hr>
<p>SpiderLeg Version: v{4}</p>
<p>SpiderLeg Home: <a href="{5}">SpiderLeg Crawler</a></p>
<p style="padding-left: 80px;"><a href="{5}">{5}</a></p>
<br><hr><br>
<p>Date Created:&nbsp;{0}</p>
"""

def EPUB_GenerateEpub(bookTitle, chapterQueue, authors, startChapter=0, endChapter=0, sourceLink="", sourceSite=""):
    outBook = epub.EpubBook()

    # Setup generals
    outBook.set_title(bookTitle)
    outBook.set_language("en")

    # Assign authors
    for author in authors:
        outBook.add_author(author)

    # Create chapters
    chapters = []
    
    chapter = epub.EpubHtml(title="{} Generated EPUB".format(SPIDERLEG_NAME), file_name="entry.xhtml", lang="en")
    chapter.content = u"<html><body>"
    chapter.content = "".join([ chapter.content,
                                u"<center><h2>- {} -</h2><br><h3>Generated EPUB</h3></center><br><br>".format(SPIDERLEG_NAME)])
    chapter.content = "".join([ chapter.content, 
                                u"<h1><center><i>{}</i></center></h1><br><hr>".format(bookTitle),
                                INFODUMP.format(
                                    datetime.datetime.now(),
                                    chapterQueue.qsize(),
                                    sourceLink,
                                    sourceSite,
                                    SPIDERLEG_VERSION,
                                    SPIDERLEG_HOME
                                )])
    chapter.content = "".join([chapter.content, u"</body></html>"])
    outBook.add_item(chapter)
    chapters.append(chapter)
    while True:
        try:
            chapterTitle, chapterContent, chapterNumber = chapterQueue.get(block=False)
            chapterFilename = "".join(["ch_", str(chapterNumber), ".xhtml"])
            chapter = epub.EpubHtml(title=chapterTitle, file_name=chapterFilename, lang="en")
            chapter.content = "".join([u"<html><body><center><h1>", chapterTitle, u"</h1></center><br>", chapterContent, u"</body></html>"])
            outBook.add_item(chapter)
            # Preserve it for later
            chapters.append(chapter)
        except queue.Empty:
            break
        except KeyboardInterrupt:
            break

    # Create Table of Contents
    outBook.toc = (
        (
            epub.Section("".join([bookTitle, " Chapters"])),
            tuple(chapters)
        ),
    )

    # Default NCX/NAV file
    outBook.add_item(epub.EpubNcx())
    outBook.add_item(epub.EpubNav())
    
    # define CSS style
    style = 'BODY {color: white; font-size: 13px;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    outBook.add_item(nav_css)

    # Create Table of Contents

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

if __name__ == "__main__":
    pageQueue = queue.Queue()

    if len(sys.argv) < 3:
        print("Usage: spiderleg.py <site> <bookLink> [<startOnChapter>-<endOnChapter>]\n\n")
        if len(sys.argv) == 2:
            if sys.argv[1] == "-h":
                print("Site Codes")
                print("\tNF\t-\tNovelFull\n")
                print("\tNH\t-\tNovelHall\n")
    
    startChapter = 1
    endChapter = 0
    if len(sys.argv) == 4:
        startChapter, endChapter = sys.argv[3].split("-")
    if sys.argv[1] == "NF":
        # Novel Full Module
        from modules.novelfull import ParseMainBookPage
        from modules.novelfull import ChainLoadPages
        bookTitle, firstChapter = ParseMainBookPage(sys.argv[2], startChapter)
        ChainLoadPages(firstChapter, pageQueue, int(endChapter), int(startChapter))
        EPUB_GenerateEpub(  bookTitle, pageQueue, [],
                            int(startChapter), int(endChapter),
                            sys.argv[2], "https://www.novelfull.com/")
    elif sys.argv[1] == "NH":
        # Novel Hall Module
        from modules.novelhall import ParseMainBookPage
        from modules.novelhall import ChainLoadPages
        bookTitle, firstChapter = ParseMainBookPage(sys.argv[2], startChapter)
        ChainLoadPages(firstChapter, pageQueue, int(endChapter), int(startChapter))
        EPUB_GenerateEpub(  bookTitle, pageQueue, [],
                            int(startChapter), int(endChapter),
                            sys.argv[2], "https://www.novelhall.com/")
    elif sys.argv[1] == "1KN":
        # 1stKissNovel Module
        from modules.firstkiss import ParseMainBookPage
        from modules.firstkiss import ChainLoadPages
        bookTitle, firstChapter = ParseMainBookPage(sys.argv[2], startChapter)
        ChainLoadPages(firstChapter, pageQueue, int(endChapter), int(startChapter))
        EPUB_GenerateEpub(  bookTitle, pageQueue, [],
                            int(startChapter), int(endChapter),
                            sys.argv[2], "https://www.1stkissnovel.love/")
    elif sys.argv[1] == "RR":
        # Royal Road Module
        exit()
    elif sys.argv[1] == "WP":
        # Watt Pad Module
        exit()
    elif sys.argv[1] == "GT":
        # Gravity Tales Module
        exit()
    elif sys.argv[1] == "WW":
        # Wuxia World Module
        exit()
    elif sys.argv[1] == "WN":
        # Web Novel Module
        exit()
    elif sys.argv[1] == "WFG":
        # Web Fiction Guide Module
        exit() 
    elif sys.argv[1] == "SH":
        # Scribble Hub Module
        exit()
    elif sys.argv[1] == "LNMTL":
        # Light Novel Machine Translations Module
        exit()
    elif sys.argv[1] == "VN":
        # Volare Novels Module
        exit()
    elif sys.argv[1] == "TR":
        # Tap Read Module
        exit()
    elif sys.argv[1] == "MS":
        # Muse's Success Module
        exit()
    elif sys.argv[1] == "WB":
        # Wordy Buzz Module
        exit()
    elif sys.argv[1] == "MQ":
        # Moon Quill Module
        exit()
    elif sys.argv[1] == "TP":
        # Tapas Module
        exit()
    elif sys.argv[1] == "FP":
        # Fiction Press Module
        exit()
    elif sys.argv[1] == "FM":
        # FANmily Module
        exit()
    elif sys.argv[1] == "FL":
        # Flying Lines Module
        exit()
    elif sys.argv[1] == "WE":
        # Word Excerpt Module
        exit()
    elif sys.argv[1] == "CN":
        # Creative Novels Module
        exit()
    elif sys.argv[1] == "FR":
        # Final Reads Module
        exit()
    elif sys.argv[1] == "BN":
        # Box Novels Module
        exit()
    elif sys.argv[1] == "BLN":
        # Best Light Novel Module
        exit()
    elif sys.argv[1] == "RLN":
        # Read Light Novel Module
        exit()
    elif sys.argv[1] == "WNO":
        # Web Novel Online Module
        exit()
    elif sys.argv[1] == "BSN":
        # Best Novel Module
        exit()
    elif sys.argv[1] == "IK":
        # Inkitt Module
        # Requires special consideration
        exit()
        # 
    #elif sys.argv[1] == "NU":
        # Novel Updates Module
        # Requires special consideration as it's a catelog, not a host
        #exit()
    exit()
