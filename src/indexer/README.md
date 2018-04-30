Parldata Elasticsearch Indexer
==============================

Python script to index the scraped debates into Elasticsearch

Running the script:
-------------------

    python3 indexer.py --esHost=127.0.0.1:9200 --esIdx=parldata_v2 --file ./parldata_1994-1998-35.json -l INFO


Arguments:
 - `esHost`: Elasticsearch server ip or hostname with port
 - `esIdx`: Target index name in Elasticsearch
 - `file`: path to the file to be indexed. The script expects the output of the scrapy crawler, which is a json file containing an array of [Speech](https://github.com/k-monitor/parldata/blob/master/src/crawler/parldata_crawler/items.py) records, each record on a separate line.
 - `limit`: stop indexing after reaching the number of the records specified by this parameter
 - `l`: log level, choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
