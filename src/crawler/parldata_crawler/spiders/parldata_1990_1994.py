# -*- coding: utf-8 -*-
import scrapy
import unicodedata
from ..items import PlenarySitting
from ..items import Speech
from urllib.parse import urljoin


class Parldata_1990_1994_Spider(scrapy.Spider):

    name = 'parldata_1990-1994'

    allowed_domains = [
        'www.parlament.hu'
    ]
    start_urls = [
        'http://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'
    ]

    def __init__(self, sitting_id=None, speech_id=None, *args, **kwargs):
        super(Parldata_1990_1994_Spider, self).__init__(*args, **kwargs)
        self.sitting_id = sitting_id
        self.speech_id = speech_id


    def parse(self, response):
        term_url = response.xpath("//a[text()='1990-94']/@href").extract_first()
        self.logger.debug("Intermediate page URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_intermediate_page)

    def parse_intermediate_page(self, response):
        term_url = response.xpath("//a[text()='Ülésnap felszólalásai']/@href").extract_first()
        self.logger.debug("Term URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_34)

    def parse_34(self, response):
        self.logger.debug("processing page: %s" % response.url)
        rows = response.xpath('//table/tbody/tr')
        for index, row in enumerate(rows):
            #self.logger.debug("  processing row: %s" % index)
            toc_url = row.xpath('td[1]/a/@href').extract_first()
            if toc_url: # and toc_url.startswith('http://www.parlament.hu/naplo34/001/'):
                sitting_date = row.xpath('td[1]/a/text()').extract_first()
                sitting_id = sitting_date.partition("(")[2].partition(")")[0]
                ps = PlenarySitting(
                    term='34',
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
                    sitting_uid="34-%s" % (sitting_id)
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
        for index, speech in enumerate(speeches):
            speech_id = str(index + 1)
            s = Speech(
                id="%s-%s" % (ps['sitting_uid'], speech_id),
                url =  urljoin(response.url, unicodedata.normalize('NFKD', speech.xpath('a/@href').extract_first())),
                speaker = speech.xpath('a/following-sibling::text()').extract()
            )
            self.logger.debug("Found speech: %s" % s)

            if s['url']:# and s['url'].startswith('http://www.parlament.hu/naplo34/001/001001'):

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

        if not 'title' in ps:
            title = response.xpath('//pre/text()').extract_first()
            if title:
                ps['title'] = title

        s['text'] = ' '.join(response.xpath('//p/text()').extract())
        prev_speech_url_frag = response.xpath(u"//a[text() = 'El\xf5z\xf5']/@href").extract_first()
        if prev_speech_url_frag:
            s['prev_speech_url'] = "%s/%s" % (response.url.rsplit('/', 1)[0], unicodedata.normalize('NFKD', prev_speech_url_frag).encode('ascii', 'ignore'))

        next_speech_url_frag = response.xpath(u"//a[text() = 'K\xf6vetkez\xf5']/@href").extract_first()
        if next_speech_url_frag:
            s['next_speech_url'] = "%s/%s" % (response.url.rsplit('/', 1)[0], unicodedata.normalize('NFKD', next_speech_url_frag).encode('ascii', 'ignore'))

        self.logger.debug("Fully processed speech: %s" % s)

        s['plenary_sitting_details'] = ps
        yield s
