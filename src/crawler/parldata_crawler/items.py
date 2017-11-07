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
    sitting_uid = scrapy.Field()
    sitting_nr = scrapy.Field()
    note = scrapy.Field() # 2002-
    video_url = scrapy.Field() # 2002-
    video_time = scrapy.Field()  # 2002-



class Speech(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    speaker = scrapy.Field()
    speaker_party = scrapy.Field()  # 1998-
    speaker_url = scrapy.Field() # 1994-
    text = scrapy.Field()
    prev_speech_url = scrapy.Field()
    next_speech_url = scrapy.Field()
    plenary_sitting_details = scrapy.Field()
    topic = scrapy.Field() # 1994-
    bill_details = scrapy.Field()  # 1994-
    bill_title = scrapy.Field() # 1994-
    bill_url = scrapy.Field() # 1994-
    type = scrapy.Field() # 1998-
    committee = scrapy.Field() # 1998-
    started_at = scrapy.Field()  # 1998-
    duration = scrapy.Field()  # 1998-
    video_url = scrapy.Field()  # 2002-
