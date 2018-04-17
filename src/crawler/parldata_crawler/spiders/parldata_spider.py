# -*- coding: utf-8 -*-
import scrapy
import unicodedata
import re
from ..items import PlenarySitting
from ..items import Speech
from urllib.parse import urljoin



class ParldataSpider(scrapy.Spider):

    name = "parldata"

    allowed_domains = [
        'www.parlament.hu'
    ]
    start_urls = [
        'http://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'
    ]

    def __init__(self, term_id=None, sitting_id=None, speech_id=None, *args, **kwargs):
        super(ParldataSpider, self).__init__(*args, **kwargs)
        self.sitting_id = sitting_id
        self.speech_id = speech_id
        if term_id is None:
            raise ValueError("Missing term id param! Value range: [34,40] (34: 1990-1994, ... 40: 2014-2018)")
        else:
            self.term_id = int(term_id)

    def parse(self, response):
        d = (self.term_id - 34) * 4
        term_url = response.xpath("//a[text()='%s-%s']/@href" % (1990 + d, (1994 + d) if self.term_id < 40 else '')).extract_first()
        self.logger.debug("Intermediate page URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_intermediate_page)

    def parse_intermediate_page(self, response):
        term_url = response.xpath("//a[text()='Ülésnap felszólalásai']/@href").extract_first()
        self.logger.debug("Term URL: %s" % term_url)
        yield scrapy.Request(term_url, callback=self.parse_list_of_sittings)

    def parse_list_of_sittings(self, response):
        self.logger.debug("processing page: %s" % response.url)
        rows = response.xpath('//table/tbody/tr')
        for index, row in enumerate(rows):

            # first row has only headers
            if index > 0:
                sitting_date = row.xpath('td[1]/a/text()').extract_first()
                if sitting_date is None:
                    self.logger.warn("Skipping row: %s", ''.join(row.xpath('.//text()').extract()))
                    continue
                sitting_nr = sitting_date.partition("(")[2].partition(")")[0]
                sitting_nr_padded = sitting_nr.rjust(3, '0')
                # do not follow the link to the sitting toc, continue crawling on a simplier page instead
                # the following link was broken in term 40
                # toc_url = "http://www.parlament.hu/naplo%s/%s/%s.htm" % (self.term_id, sitting_nr_padded,
                #                                                         sitting_nr_padded)
                toc_url = "http://www.parlament.hu/internet/plsql/ogy_naplo.ulnap_felszo?p_lista=f&p_nap=%s&p_ckl=%s" \
                          % (sitting_nr, self.term_id)
                video_column_offset = 1 if self.term_id > 36 else 0
                ps = PlenarySitting(
                    term=self.term_id,
                    date=sitting_date.partition("(")[0],
                    toc_url=toc_url,
                    day=row.xpath("td[%d]/text()" % 2).extract_first().strip(),
                    session=row.xpath("td[%d]/text()" % (3 + video_column_offset)).extract_first(),
                    type=row.xpath("td[%d]/text()" % (4 + video_column_offset)).extract_first(),
                    day_of_session=row.xpath("td[%d]/text()" % (5 + video_column_offset)).extract_first(),
                    duration_raw=row.xpath("td[%d]/a/text()" % (6 + video_column_offset)).extract_first(),
                    duration=row.xpath("td[%d]/text()" % (7 + video_column_offset)).extract_first(),
                    sitting_id=row.xpath("td[%d]/text()" % (8 + video_column_offset)).extract_first(),
                    sitting_day=row.xpath("td[%d]/text()" % (9 + video_column_offset)).extract_first(),
                    note=row.xpath("td[%d]/text()" % (10 + video_column_offset)).extract_first(),
                    sitting_uid="%s-%s" % (self.term_id, sitting_nr),
                    sitting_nr=sitting_nr
                )
                # video column is useless in term 36
                if self.term_id > 37:
                    ps['video_time'] = row.xpath("td[3]/a/text()").extract_first()
                    ps['video_url'] = row.xpath("td[3]/a/@href").extract_first()

                request = scrapy.Request(toc_url, callback=self.parse_sitting_toc)
                request.meta['plenary_sitting'] = ps
                if self.sitting_id is None or self.sitting_id == sitting_nr:
                    self.logger.debug("  crawling sitting: %s", sitting_nr)
                    yield request
            else:
                continue

    def parse_sitting_toc(self, response):
        # self.logger.debug("processing toc url: %s" % response.url)
        ps = response.meta['plenary_sitting']

        blocks = response.xpath('/html/body/div[@class="pair-content"]/table')
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
                        bill_titles.append("%s %s" % (bill_ref.xpath('text()').extract_first(),
                                                      bill_ref.xpath('following-sibling::text()').extract_first()))

                elif index == 1:
                    # headers
                    continue
                else:
                    # speeches
                    speech_ref = row.xpath('td[1]/a')
                    speech_id = unicodedata.normalize('NFKD', speech_ref.xpath('text()').extract_first()).strip()
                    # self.logger.debug("  ###  speech ID : %s", speech_id)
                    # some of the speeches are published in batch, these should be processed separately
                    range_id_match = re.fullmatch('([0-9]+)\-([0-9]+)', speech_id)
                    if range_id_match:
                        # self.logger.debug("######### RANGE ID MATCH")
                        speech_id_range_start = int(range_id_match.group(1))
                        speech_id_range_end = int(range_id_match.group(2)) + 1
                    else:
                        speech_id_range_start = int(speech_id)
                        speech_id_range_end = int(speech_id) + 1
                    for i in range(speech_id_range_start, speech_id_range_end):
                        # self.logger.debug("  ###  speech ID from range: %s", i)
                        s = Speech(
                            id="%s-%s" % (ps['sitting_uid'], i),
                            # url=urljoin(response.url, unicodedata.normalize('NFKD', speech_ref.xpath('@href').extract_first())),
                            # using a more parseable url
                            url="http://www.parlament.hu/internet/plsql/ogy_naplo.naplo_fadat?p_ckl=%d&p_uln=%s&p_felsz=%s&p_szoveg=&p_felszig=%s"
                                % (self.term_id, ps['sitting_nr'], i, i),
                            type=row.xpath('td[3]/text()').extract_first(),
                            committee=row.xpath('td[4]/text()').extract_first(),
                            started_at=row.xpath('td[5]/text()').extract_first(),
                            topic=topic,
                            bill_title=bill_titles,
                            bill_url=bill_urls


                        )
                        if self.speech_id is None or self.speech_id == str(i):
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

        data_table = response.xpath('//div[@id="egy_felszolalas"]/table')
        speaker_fulltext = data_table.xpath('tr[2]/td[2]/a/text()').extract_first()
        s['speaker'] = speaker_fulltext.partition("(")[0].strip()
        s['speaker_party'] = speaker_fulltext.partition("(")[2].partition(")")[0]
        s['speaker_url'] = urljoin(response.url, unicodedata.normalize('NFKD', data_table.xpath('tr[2]/td[2]/a/@href').extract_first()))
        if self.term_id > 36:
            s['duration'] = data_table.xpath("tr[6]/td[2]/a/text()").extract_first()
            s['video_url'] = data_table.xpath("tr[6]/td[2]/a/@href").extract_first()
        else:
            s['duration'] = data_table.xpath("tr[6]/td[2]/text()").extract_first()

        s['text'] = ''.join(response.xpath('//div[@id="felsz_szovege"]//text()').extract())
        prev_speech_url_frag = response.xpath("//a[text()='Előző']/@href").extract_first()
        if prev_speech_url_frag:
            s['prev_speech_url'] = urljoin(response.url, unicodedata.normalize('NFKD', prev_speech_url_frag))

        next_speech_url_frag = response.xpath("//a[text()='Következő']/@href").extract_first()
        if next_speech_url_frag:
            s['next_speech_url'] = urljoin(response.url, unicodedata.normalize('NFKD', next_speech_url_frag))

        s['plenary_sitting_details'] = ps

        yield s