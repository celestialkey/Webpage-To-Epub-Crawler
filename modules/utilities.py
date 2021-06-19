###############################################
#
#                  utilities.py
#
#   Contains a bunch of helper functions
#   mostly related to parsing and navigating
#   through html documents and provides a 
#   mechanisms to extract data out without
#   relying on another library
#
###############################################






""" HTML_LocatePosition(uniqueId, searchBuffer, startOffset)
    Performs a standard search for text, however will return 
    the position immediately following the position.

    @param startOffset: can be used to start searching from
    a predefined location.

    Searching for "text" below will return

    <h3 class="example">text</h3>
    Pos-^               ^
          ______________|
         |
    Returns 't' position after call.

    Note that failure to find results in a 0 return rather
    than -1 like normal.
"""
def HTML_LocatePosition(uniqueId, searchBuffer, startOffset=0):
    return searchBuffer.find(uniqueId, startOffset)+1

""" HTML_LocateEndPosition(uniqueId, searchBuffer, startOffset)
    Performs a standard search for text, however will return 
    the position following the search term.

    @param startOffset: can be used to start searching from
    a predefined location.

    Searching for "text" below will return

    <h3 class="example">text</h3>
             Pos--^         ^
             _______________|
             |
    Returns '<' position after call.
    Note that failure to find results in -1 like normal.
"""
def HTML_LocateEndPosition(uniqueId, searchBuffer, startOffset=0):
    return searchBuffer.find(uniqueId, startOffset)+len(uniqueId)

""" HTML_LocateTagStartFromPosition(searchBuffer, stopPosition)
    Get the starting position of the tag containing the current position.

    <h3 class="example">text</h3>
    ^        Pos--^
    |_____
         |
    Returns '<' position after call.

    Functionally equal to HTML_LocateTagStartFromContent().
"""
def HTML_LocateTagStartFromPosition(searchBuffer, stopPosition):
    return searchBuffer.rfind("<", 0, stopPosition)



def HTML_LocateParentTagStartFromInsideCurrentTag(searchBuffer, stopPosition, searchTag="<"):
    exitCurrentTag = searchBuffer.rfind("<", 0, stopPosition)

""" HTML_LocateTagStartFromContent(searchBuffer, stopPosition, searchTag)
    Get the starting position of the tag containing the current position.

    <h3 class="example">text</h3>
    ^                Pos--^
    |_____
         |
    Returns '<' position after call.

    Functionally equal to HTML_LocateTagStartFromPosition().
"""
def HTML_LocateTagStartFromContent(searchBuffer, stopPosition, searchTag="<"):
    return searchBuffer.rfind("<", 0, stopPosition)

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
