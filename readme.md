# Installation
- ```apt install python3 -y```
- ```pip3 install EbookLib```

# Usage
### Download the entire series as a single Epub
- ```python3 spiderleg.py NF https://novelfull.com/release-that-witch.html```

### Download only the first 200 chapters of the series
- ```python3 spiderleg.py NF https://novelfull.com/release-that-witch.html 1-200```
- ```python3 spiderleg.py NF 'https://novelfull.com/index.php/release-that-witch.html?page=1&per-page=50' 1-201``` 
- - *Note the link has changed to include where the 'starting chapter' shows up on the webpage's listing*

### Download starting from where the last one left off
- ```python3 spiderleg.py NF 'https://novelfull.com/index.php/release-that-witch.html?page=5&per-page=50' 201-201```
- - *Note the link has changed to include where the 'starting chapter' shows up on the webpage's listing*

Pay attention to the single quotes surrounding the weblink. The typical shell will try to escape out of the link and do amazing things without them.

The output file will use the series title and append a range if you specified one.
