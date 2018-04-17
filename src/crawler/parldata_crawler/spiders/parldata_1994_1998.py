# -*- coding: utf-8 -*-
import scrapy
import unicodedata
from ..items import PlenarySitting
from ..items import Speech
from urllib.parse import urljoin


class Parldata_1994_1998_Spider(scrapy.Spider):

    name = 'parldata_1994-1998'

    allowed_domains = [
        'www.parlament.hu'
    ]
    start_urls = [
        'http://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'
    ]

    def __init__(self, sitting_id=None, speech_id=None, *args, **kwargs):
        super(Parldata_1994_1998_Spider, self).__init__(*args, **kwargs)
        self.sitting_id = sitting_id
        self.speech_id = speech_id
        self.term_id = 35

    def parse(self, response):
        term_url = response.xpath("//a[text()='1994-98']/@href").extract_first()
        self.logger.debug("Intermediate page URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_intermediate_page)

    def parse_intermediate_page(self, response):
        term_url = response.xpath("//a[text()='Ülésnap felszólalásai']/@href").extract_first()
        self.logger.debug("Term URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_35)

    def parse_35(self, response):
        self.logger.debug("processing page: %s" % response.url)
        rows = response.xpath('//table/tbody/tr')
        for index, row in enumerate(rows):
            #self.logger.debug("  processing row: %s" % index)
            toc_url = row.xpath('td[1]/a/@href').extract_first()
            if toc_url: # and toc_url.startswith('http://www.parlament.hu/naplo35/004/'):
                sitting_date = row.xpath('td[1]/a/text()').extract_first()
                sitting_id = sitting_date.partition("(")[2].partition(")")[0]
                ps = PlenarySitting(
                    term='35',
                    date=sitting_date.partition("(")[0],
                    toc_url=toc_url,
                    day=row.xpath('td[2]/text()').extract_first(),
                    session=row.xpath('td[3]/text()').extract_first(),
                    type=row.xpath('td[4]/text()').extract_first(),
                    day_of_session=row.xpath('td[5]/text()').extract_first(),
                    duration_raw=row.xpath('td[6]/a/text()').extract_first(),
                    duration=row.xpath('td[7]/text()').extract_first(),
                    sitting_id=row.xpath('td[8]/text()').extract_first(),
                    sitting_day=row.xpath('td[9]/text()').extract_first(),
                    sitting_uid="35-%s" % (sitting_id)
                )
                request = scrapy.Request(toc_url, callback=self.parse_sitting_toc)
                request.meta['plenary_sitting'] = ps
                #self.logger.debug("  parsed obj: %s" % ps)
                if self.sitting_id is None or self.sitting_id == sitting_id:
                    yield request
            else:
                continue

    def parse_sitting_toc(self, response):
        self.logger.debug("processing toc url: %s" % response.url)
        ps = response.meta['plenary_sitting']
        speeches = response.xpath('//li')
        topic = ""
        topic_url = ""
        for index, speech in enumerate(speeches):

            speech_refs = speech.xpath('a')
            speech_id = str(index + 1)
            s = Speech(
                id = "%s-%s" % (ps['sitting_uid'], speech_id),
                url = urljoin(response.url, unicodedata.normalize('NFKD', speech_refs[0].xpath('@href').extract_first())),
                #speaker = speech.xpath('a/following-sibling::text()').extract(),
                topic=topic,
                bill_url=topic_url

            )

            # find speaker
            if len(speech_refs) == 1:
                s['speaker'] = speech_refs[0].xpath('following-sibling::text()').extract(),
            elif len(speech_refs) == 2:
                s['speaker'] = speech_refs[1].xpath('text()').extract_first()
                s['speaker_url'] = urljoin(response.url, unicodedata.normalize('NFKD', speech_refs[1].xpath('@href').extract_first()))

            #self.logger.debug("Found speech: %s" % s)

            # find topic of next speech
            topics = speech.xpath('h4')
            if topics:
                topic = topics[-1].xpath('text()').extract_first()
                topic_href_attr = topics[-1].xpath('a/@href').extract_first()
                if topic_href_attr:
                    topic_url = urljoin(response.url, unicodedata.normalize('NFKD', topic_href_attr))
                else:
                    topic_url = ""

            if s['url']: # and s['url'].startswith('http://www.parlament.hu/naplo35/004/004003'):

                prio = 99 if index == 0 else 0 # there is extra data on the page of the first speech, which should be indexed to all other speeches as well
                request = scrapy.Request(s['url'], callback=self.parse_speech_text, priority=prio)
                request.meta['plenary_sitting'] = response.meta['plenary_sitting']
                request.meta['speech'] = s
                if self.speech_id is None or self.speech_id == speech_id:
                    yield request
                else:
                    continue
            else:
                continue

    def parse_speech_text(self, response):
        self.logger.debug("processing speech: %s" % response.url)
        s = response.meta['speech']
        ps = response.meta['plenary_sitting']

        if not 'header' in ps:
            header = response.xpath('//pre/text()').extract_first()
            if header:
                ps['header'] = header.strip()

        s['text'] = ' '.join(response.xpath('//p/text()').extract())
        prev_speech_url_frag = response.xpath(u"//a[text() = 'El\xf5z\xf5']/@href").extract_first()
        if prev_speech_url_frag:
            s['prev_speech_url'] = "%s/%s" % (response.url.rsplit('/', 1)[0], unicodedata.normalize('NFKD', prev_speech_url_frag).encode('ascii', 'ignore'))

        next_speech_url_frag = response.xpath(u"//a[text() = 'K\xf6vetkez\xf5']/@href").extract_first()
        if next_speech_url_frag:
            s['next_speech_url'] = "%s/%s" % (response.url.rsplit('/', 1)[0], unicodedata.normalize('NFKD', next_speech_url_frag).encode('ascii', 'ignore'))

        s['plenary_sitting_details'] = ps

        if s['bill_url']:
            self.logger.debug("  has bill url, following: %s" % s['id'])
            request = scrapy.Request(s['bill_url'], callback=self.parse_bill, dont_filter=True)
            request.meta['speech'] = s
            yield request
        else:
            self.logger.debug("has not got bill url, returning: %s" % s['id'])
            yield s

    def parse_bill(self, response):
        s = response.meta['speech']
        self.logger.debug("processing bill %s speech: %s" % (response.url, s['id']))
        s['bill_title']=response.xpath('//h2/text()').extract_first()
        s['bill_details']=' '.join(response.xpath('//p/text()').extract())
        self.logger.debug("Fully processed speech: %s" % s['id'])
        yield s
