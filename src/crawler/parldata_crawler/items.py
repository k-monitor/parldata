# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PlenarySitting(scrapy.Item):
    # Dátum | Nap | Ülésszak | Ülés jellege | Nap | Tárgy. idő (óra:perc) |	Ülésidő (óra:perc)| Ülés |Nap

    term = scrapy.Field()
    date = scrapy.Field()
    toc_url = scrapy.Field()
    day = scrapy.Field()
    session = scrapy.Field()
    type = scrapy.Field()
    day_of_session = scrapy.Field()
    duration_raw = scrapy.Field()
    duration = scrapy.Field()
    sitting_id = scrapy.Field()
    sitting_day = scrapy.Field()
    title = scrapy.Field()


class Speech(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    speaker = scrapy.Field()
    speaker_url = scrapy.Field() # 1994-
    text = scrapy.Field()
    prev_speech_url = scrapy.Field()
    next_speech_url = scrapy.Field()
    plenary_sitting_details = scrapy.Field()
    topic = scrapy.Field() # 1994-
    bill_details = scrapy.Field()  # 1994-
    bill_title = scrapy.Field() # 1994-
    bill_url = scrapy.Field() # 1994-