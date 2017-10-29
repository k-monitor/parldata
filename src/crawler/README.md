# Hungarian parliament speech crawler

### 1. Requirements
- python 3.x
- scrapy 1.4.0

### 2. Running the crawlers
    scrapy crawl parldata_1990-1994

    scrapy crawl parldata_1994-1998

    scrapy crawl parldata_1998-2002

The results will be exported to json files named by the crawler and crawliing timestamp.


If not all of the speeches are required to be crawled you can restrict the crawler to visit the pages only the specified sitting and speeches:

     scrapy crawl parldata_1990-1994 -a sitting_id=1

     scrapy crawl parldata_1990-1994 -a sitting_id=1 -a speech_id=1