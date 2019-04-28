import json
import logging
import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class Indexer(object):

    def __init__(self, es_host, index_name, source_file, limit=None):
        self.es_host = es_host
        self.index_name = index_name
        self.source_file = source_file
        self.limit = limit
        self.logger = logging.getLogger(__name__)
        return

    def decode_parldata_record(self):
        self.logger.info("LIMIT: %s", self.limit)
        c = 0
        with open(self.source_file) as f:
            for line in f:

                if c % 1000 == 0:
                    self.logger.info("Processing: %d", c)

                if self.limit is not None and c >= int(self.limit):
                    self.logger.info("Limit was reached: %s", self.limit)
                    break

                c = c + 1
                if line == '[\n' or line == ']\n':
                    self.logger.debug('Expected invalid line, skipping')
                    continue
                try:
                    src = json.loads(line.strip(' ,\r\n'))
                    dest = {}
                    for w in ["id", "bill_title", "bill_url", "committee", "duration", "prev_speech_url",
                              "next_speech_url", "speaker", "speaker_title", "speaker_party", "speaker_url",
                              "url", "text", "type", "topic", "header"]:
                        try:
                            dest[w] = src[w]
                        except KeyError:
                            pass
                    for w in ["video_url", "video_time", "term", "toc_url", "session", "date", "day", "day_of_session",
                              "note", "sitting_nr", "sitting_uid", "sitting_id"]:
                        try:
                            dest[w] = src["plenary_sitting_details"][w]
                        except KeyError:
                            pass
                    for w in ["duration", "duration_raw", "day", "type"]:
                        try:
                            dest["sitting_%s" % w] = src["plenary_sitting_details"][w]
                        except KeyError:
                            pass
                    dest["suggest"] = [
                        {"input": dest["speaker"], "weight": 10},
                    ]
                    if "speaker_party" in dest:
                        dest["suggest"].append({"input": dest["speaker_party"], "weight": 5})
                    if "type" in dest:
                        dest["suggest"].append({"input": dest["type"], "weight": 7})
                    if "topic" in dest:
                        dest["suggest"].append({"input": dest["topic"], "weight": 5})
                    if "bill_title" in dest:
                        dest["suggest"].append({"input": dest["bill_title"], "weight": 5})

                    yield dest['id'], dest
                except ValueError as e:
                    self.logger.warning("Could not index record: %s", e)
        self.logger.info("Processed: %d", c)

    def run(self):
        es = Elasticsearch(hosts=[self.es_host])
        k = ({
            "_index": self.index_name,
            "_id": idx,
            "_source": data,
        } for idx, data in self.decode_parldata_record())

        bulk(es, k, request_timeout=60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Indexes scraped parldata files'
    )

    parser.add_argument('--esHost',
                        help='Elasticsearch host name with port',
                        required=True)

    parser.add_argument('--esIdx',
                        help='Elasticsearch index name',
                        required=True)

    parser.add_argument('--file',
                        help='Scrapy output file to be indexed',
                        required=True)

    parser.add_argument('--limit',
                        help='Limit input processing for # records',
                        required=False)

    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level")

    args = parser.parse_args()

    if args.logLevel:
        logging.basicConfig(level=getattr(logging, args.logLevel))

    Indexer(args.esHost, args.esIdx, args.file, args.limit).run()
