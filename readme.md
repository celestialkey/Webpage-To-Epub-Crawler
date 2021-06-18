# SpiderLeg
SpiderLeg is a webcrawler designed for popular publishing sites where translated reading material typically congregates. After being provided a link, SpiderLeg will 
- Go out and download each chapter of the series
- Extract the contents of each chapter
- Generate a .epub file to represent those actions

SpiderLeg itself is rather mundane, but most great things are!

# Installation
- ```apt install python3 -y```
- ```pip3 install EbookLib```
  <br><br>
  
  
# Usage
- ```python3 spiderleg.py <sitecode> <bookLink> [<startChapter>-<stopChapter>]```
<br><br><br><br>
  
# Supported Websites
- NF - NovelFull
- NH - NovelHall
  
## Examples (NovelFull)
### Download the entire series as a single Epub
- ```python3 spiderleg.py NF https://novelfull.com/release-that-witch.html```

### Download only the first 200 chapters of the series
- ```python3 spiderleg.py NF https://novelfull.com/release-that-witch.html 1-200```
- ```python3 spiderleg.py NF 'https://novelfull.com/index.php/release-that-witch.html?page=1&per-page=50' 1-200``` 
- - *Note the link has changed to include where the 'starting chapter' shows up on the webpage's listing*

### Download starting from where the last one left off
- ```python3 spiderleg.py NF 'https://novelfull.com/index.php/release-that-witch.html?page=5&per-page=50' 201-891```
- - *Note the link has changed to include where the 'starting chapter' shows up on the webpage's listing*

Pay attention to the single quotes surrounding the weblink. The typical shell will try to escape out of the link and do amazing things without them.
The output file will use the series title and append a range if you specified one.


<br><br><br><br>
## (NovelHall)
### Download the entire series as a single Epub
- ```python3 spiderleg.py NH 'https://www.novelhall.com/the-villainess-turns-the-hourglass-10137/'```

### Download only the first 200 chapters of the series
- ```python3 spiderleg.py NH 'https://www.novelhall.com/the-villainess-turns-the-hourglass-10137/' 1-200```
- - *Note the unlike novelfull, all the chapters are presented on the same page with novelhall, so no need to change links.*

### Download starting from where the last one left off
- ```python3 spiderleg.py NH 'https://www.novelhall.com/the-villainess-turns-the-hourglass-10137/' 201-288```
- - *Note the unlike novelfull, all the chapters are presented on the same page with novelhall, so no need to change links.*

Pay attention to the single quotes surrounding the weblink. The typical shell will try to escape out of the link and do amazing things without them.

The output file will use the series title and append a range if you specified one.
