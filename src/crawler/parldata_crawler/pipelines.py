# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ParldataCrawlerPipeline(object):

    def process_item(self, item, spider):

        # Normalize parsed speech text
        if item['text']:
            item['text'] = item['text'].replace('A felszólalás szövege:', '').replace(u'\xa0', u' ')
        return item
