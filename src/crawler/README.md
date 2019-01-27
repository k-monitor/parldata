# Hungarian parliament speech crawler

## 1. Requirements
- python 3.x
- scrapy 1.4.0

## 2. Running the crawlers


#### For term 1990-1994:

    scrapy crawl parldata_1990-1994

#### For term 1994-1998:

    scrapy crawl parldata_1994-1998

#### From 1998:

    scrapy crawl parldata -a term_id=36

Where term_id represents the parliamentary cycle:
* 36: 1998-2002
* 37: 2002-2006
* 38: 2006-2010
* 39: 2010-2014
* 40: 2014-


The results will be exported to json files named by the crawler, term and crawling timestamp.


If not all of the speeches are required to be crawled you can restrict each crawler to visit the pages only the specified sitting and speeches:

     scrapy crawl parldata_1990-1994 -a sitting_id=1

     scrapy crawl parldata_1990-1994 -a sitting_id=1 -a speech_id=1

You can check if there are new speeches uploaded which are not indexed yet and crawl only the missing plenary sittings to make a diff file to your index (this will only check the index on the level of plenary sittings, not speeches):

    scrapy crawl parldata -a term_id=41 -a index_url=http://127.0.0.1:9200/parldata

The `index_url` argument can not be used with the `sitting_id` and `speech_id` arguments, if all of the parameters are specified the id filters will be ignored.
