# -*- coding: utf-8 -*-
import scrapy
import unicodedata
import re
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
            toc_url = row.xpath('td[1]/a/@href').extract_first()
            if toc_url:
                sitting_date = row.xpath('td[1]/a/text()').extract_first().strip()
                sitting_id = sitting_date.partition("(")[2].partition(")")[0]
                ps = PlenarySitting(
                    term='35',
                    date=sitting_date.partition("(")[0],
                    toc_url=toc_url,
                    day=row.xpath('td[2]/text()').extract_first().strip(),
                    session=row.xpath('td[3]/text()').extract_first().strip(),
                    type=row.xpath('td[4]/text()').extract_first().strip(),
                    day_of_session=row.xpath('td[5]/text()').extract_first().strip(),
                    duration_raw=row.xpath('td[6]/a/text()').extract_first().strip(),
                    duration=row.xpath('td[7]/text()').extract_first().strip(),
                    sitting_id=row.xpath('td[8]/text()').extract_first().strip(),
                    sitting_day=row.xpath('td[9]/text()').extract_first().strip(),
                    sitting_uid="35-%s" % (sitting_id)
                )
                request = scrapy.Request(toc_url, callback=self.parse_sitting_toc)
                request.meta['plenary_sitting'] = ps
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
            if len(speech_refs) == 0:
                self.logger.warn("Missing speech link at %s: %s" % (response.url, speech_id))
                continue
            s = Speech(
                id = "%s-%s" % (ps['sitting_uid'], speech_id),
                url = urljoin(response.url, unicodedata.normalize('NFKD', speech_refs[0].xpath('@href').extract_first())),
                topic=topic,
                bill_url=topic_url

            )

            # find speaker
            if len(speech_refs) == 1:
                speaker = ' '.join(speech.xpath('text()').extract()).strip(' :\r\n')
                if speaker.find('[') == -1:
                    s['speaker'] = speaker
                else:
                    s['speaker'] = speaker.partition("[")[0].strip(' :\r\n')
                    s['duration'] = speaker.partition("[")[2].partition(" ")[0]

            elif len(speech_refs) == 2:
                s['speaker'] = speech_refs[1].xpath('text()').extract_first().strip()
                s['speaker_url'] = urljoin(response.url, unicodedata.normalize('NFKD', speech_refs[1].xpath('@href').extract_first()))
                duration = speech_refs[1].xpath('following-sibling::text()').extract_first()
                if duration != '\n':
                    s['duration'] = duration.strip(' \n')[1:6]

            # find topic of next speech
            topics = speech.xpath('h4')
            if topics:
                topic = topics[-1].xpath('text()').extract_first().strip(' (')
                topic_href_attr = topics[-1].xpath('a/@href').extract_first()
                if topic_href_attr:
                    topic_url = urljoin(response.url, unicodedata.normalize('NFKD', topic_href_attr))
                else:
                    topic_url = ""

            if s['url']:

                prio = 99 if index == 0 else 0  # there is extra data on the page of the first speech, which should be indexed to all other speeches as well
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
            s['prev_speech_url'] = urljoin(response.url, prev_speech_url_frag)

        next_speech_url_frag = response.xpath(u"//a[text() = 'K\xf6vetkez\xf5']/@href").extract_first()
        if next_speech_url_frag:
            s['next_speech_url'] = urljoin(response.url, next_speech_url_frag)

        # 216/43
        if not 'speaker' in s or len(s['speaker'].strip()) == 0:
            idx = s['text'].find(':')
            if idx > -1:
                speaker = s['text'][0:idx]
                speaker_with_title_match = re.search("([^\,]+)\,\s*(.+)", speaker)
                if speaker_with_title_match:
                    g1 = speaker_with_title_match.group(1).strip()
                    g2 = speaker_with_title_match.group(2).strip()
                    s['speaker'] = g1.title()
                    s['speaker_title'] = g2
                else:
                    s['speaker'] = speaker

        s['plenary_sitting_details'] = ps

        if s['bill_url']:
            request = scrapy.Request(s['bill_url'], callback=self.parse_bill, dont_filter=True)
            request.meta['speech'] = s
            yield request
        else:
            yield s

    def parse_bill(self, response):
        s = response.meta['speech']
        self.logger.debug("processing bill %s speech: %s" % (response.url, s['id']))
        s['bill_title']=response.xpath('//h2/text()').extract_first().strip()
        s['bill_details']=' '.join(response.xpath('//p/text()').extract()).strip()
        yield s
