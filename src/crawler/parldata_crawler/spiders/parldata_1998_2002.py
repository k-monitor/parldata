# -*- coding: utf-8 -*-
import scrapy
import unicodedata
from ..items import PlenarySitting
from ..items import Speech
from urllib.parse import urljoin


class Parldata_1998_2002_Spider(scrapy.Spider):

    name = 'parldata_1998-2002'

    allowed_domains = [
        'www.parlament.hu'
    ]
    start_urls = [
        'http://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'
    ]

    def __init__(self, sitting_id=None, speech_id=None, *args, **kwargs):
        super(Parldata_1998_2002_Spider, self).__init__(*args, **kwargs)
        self.sitting_id = sitting_id
        self.speech_id = speech_id

    def parse(self, response):
        term_url = response.xpath("//a[text()='1998-2002']/@href").extract_first()
        self.logger.debug("Intermediate page URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_intermediate_page)

    def parse_intermediate_page(self, response):
        term_url = response.xpath("//a[text()='Ülésnap felszólalásai']/@href").extract_first()
        self.logger.debug("Term URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_36)

    def parse_36(self, response):
        self.logger.debug("processing page: %s" % response.url)
        rows = response.xpath('//table/tbody/tr')
        for index, row in enumerate(rows):

            # first row has only headers
            if index > 0:
                sitting_date = row.xpath('td[1]/a/text()').extract_first()
                sitting_id = sitting_date.partition("(")[2].partition(")")[0]
                sitting_id_padded = sitting_id.rjust(3, '0')
                # do not follow the link to the sitting toc, continue crawling on a simplier page instead
                toc_url = "http://www.parlament.hu/naplo36/%s/%s.htm" % (sitting_id_padded, sitting_id_padded)
                ps = PlenarySitting(
                    term='36',
                    date=sitting_date.partition("(")[0],
                    toc_url=toc_url,
                    day=row.xpath('td[2]/text()').extract_first().strip(),
                    session=row.xpath('td[3]/text()').extract_first(),
                    type=row.xpath('td[4]/text()').extract_first(),
                    day_of_session=row.xpath('td[5]/text()').extract_first(),
                    duration_raw=row.xpath('td[6]/a/text()').extract_first(),
                    duration=row.xpath('td[7]/text()').extract_first(),
                    sitting_id=row.xpath('td[8]/text()').extract_first(),
                    sitting_day=row.xpath('td[9]/text()').extract_first(),
                    sitting_uid="36-%s" % (sitting_id)
                )
                request = scrapy.Request(toc_url, callback=self.parse_sitting_toc)
                request.meta['plenary_sitting'] = ps
                #self.logger.debug("  parsed obj: %s" % ps)
                if self.sitting_id is None or self.sitting_id == sitting_id:
                    self.logger.debug("  crawling sitting: %s", sitting_id)
                    yield request
            else:
                continue

    def parse_sitting_toc(self, response):
        self.logger.debug("processing toc url: %s" % response.url)
        ps = response.meta['plenary_sitting']

        blocks = response.xpath('//table')
        for block_index, block in enumerate(blocks):
            rows = block.xpath('tr')
            topic = ""
            bill_titles = []
            bill_urls = []
            for index, row in enumerate(rows):
                if index == 0:
                    # topic
                    topic = row.xpath("th/font/text()").extract_first().strip()
                    bills = row.xpath("th/font/a")
                    for bill_index, bill_ref in enumerate(bills):
                        bill_urls.append(urljoin(response.url,
                                    unicodedata.normalize('NFKD', bill_ref.xpath('@href').extract_first())))
                        bill_titles.append("%s %s" % (bill_ref.xpath('text()').extract_first(),  bill_ref.xpath('following-sibling::text()').extract_first()))

                elif index == 1:
                    # headers
                    continue
                else:
                    # speeches
                    speech_ref = row.xpath('td[1]/a')
                    speaker_fulltext = row.xpath('td[2]/a/text()').extract_first()
                    speech_id = unicodedata.normalize('NFKD', speech_ref.xpath('text()').extract_first()).strip()
                    self.logger.debug("  ###  speech ID : %s", speech_id)
                    s = Speech(
                        id="%s-%s" % (ps['sitting_uid'], speech_id),
                        url=urljoin(response.url,
                                    unicodedata.normalize('NFKD', speech_ref.xpath('@href').extract_first())),
                        speaker = speaker_fulltext.partition("(")[0].strip(),
                        speaker_party=speaker_fulltext.partition("(")[2].partition(")")[0],
                        speaker_url = urljoin(response.url,
                                    unicodedata.normalize('NFKD', row.xpath('td[2]/a/@href').extract_first())),
                        type = row.xpath('td[3]/text()').extract_first(),
                        committee=row.xpath('td[4]/text()').extract_first(),
                        started_at=row.xpath('td[5]/text()').extract_first(),
                        duration=row.xpath('td[6]/text()').extract_first(),
                        topic=topic,
                        bill_title=bill_titles,
                        bill_url=bill_urls


                    )
                    #self.logger.debug("  ###  speech: %s", s)
                    if self.speech_id is None or self.speech_id == speech_id:
                        request = scrapy.Request(s['url'], callback=self.parse_speech_text)
                        request.meta['plenary_sitting'] = response.meta['plenary_sitting']
                        request.meta['speech'] = s
                        yield request
                    else:
                        continue

    def parse_speech_text(self, response):
        self.logger.debug("processing speech: %s" % response.url)
        s = response.meta['speech']
        ps = response.meta['plenary_sitting']

        s['text'] = ' '.join(response.xpath('//p[@align="JUSTIFY"]/text()').extract())
        prev_speech_url_frag = response.xpath(u"//a[text() = 'Előző']/@href").extract_first()
        if prev_speech_url_frag:
            s['prev_speech_url'] = urljoin(response.url, unicodedata.normalize('NFKD', prev_speech_url_frag))

        next_speech_url_frag = response.xpath(u"//a[text() = 'Következő']/@href").extract_first()
        if next_speech_url_frag:
            s['prev_speech_url'] = urljoin(response.url, unicodedata.normalize('NFKD', next_speech_url_frag))

        s['plenary_sitting_details'] = ps

        yield s

