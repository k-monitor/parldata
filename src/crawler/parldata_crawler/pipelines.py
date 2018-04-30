# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import parldata_crawler.items
from cgi import valid_boundary
from collections.abc import Sequence


def _seq_but_not_str(obj):
    return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray))


def _bulk_normalize(item):
    keys_to_remove = []
    for key, value in item.items():
        if value is None:
            keys_to_remove.append(key)
        elif _seq_but_not_str(value):
            if len(value) == 0:
                keys_to_remove.append(key)
        elif isinstance(value, str):
            v = value.replace('\xa0', ' ').strip(' \n')
            if v == '':
                keys_to_remove.append(key)
            else:
                item[key] = v
        elif isinstance(value, parldata_crawler.items.PlenarySitting):
            _bulk_normalize(item[key])
    for key in keys_to_remove:
        del item[key]


class ParldataCrawlerPipeline(object):

    speaker_patterns = ["-\s*Elnök:\s*([^\-\)\r\n]+)\s*[\-\)\r\n]", "Az elnöki széket (.*) foglalja"]

    def process_item(self, item, spider):

        # Normalize parsed speech text
        if 'text' in item:
            item['text'] = item['text'].replace('A felszólalás szövege:', '').replace(u'\xa0', u' ')

        if 'speaker' in item and item['speaker']:
            item['speaker'] = item['speaker'].strip(' :')


        header_match_probe = True
        # 1990-94/31
        speaker_with_party_match = re.search("([^\(]+)\(([^\)]+)\)", item['speaker'])
        if speaker_with_party_match:
            header_match_probe = False
            g1 = speaker_with_party_match.group(1).strip()
            g2 = speaker_with_party_match.group(2).strip()
            if g1.lower() == 'elnök':
                item['speaker'] = g2
                item['speaker_title'] = 'Elnök'
            else:
                item['speaker'] = g1
                item['speaker_party'] = g2

        # 1990-1994: chairman info in header
        if header_match_probe and 'header' in item['plenary_sitting_details']:
            if item['speaker'].lower() == 'elnök':
                item['speaker_title'] = item['speaker']
                h = item['plenary_sitting_details']['header']
                for p in self.speaker_patterns:
                    match = re.search(p, h)
                    if match:
                        item['speaker'] = match.group(1).strip(' .\r\n')
                        break

        if 'speaker' in item and item['speaker'].isupper():
            item['speaker'] = item['speaker'].title()

        item['text'] = re.sub('\s*[\r\n]+', '\n', item['text']).strip(' \n')

        if 'bill_title' in item:
            if _seq_but_not_str(item['bill_title']):
                item['bill_title'] = [t.strip(' \n') for t in item['bill_title']]

        _bulk_normalize(item)

        return item
