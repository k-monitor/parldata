import re
import math
import time
import logging
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
from bs4 import BeautifulSoup

from configs import BASE_KEYS, REQUIRED_BY_COLUMN_INDEX


def get_last_n_existing_indexes_for_term(
        term_id, url='https://parldata-search-proxy.westeurope.cloudapp.azure.com/parldata/_search?pretty', n=9999):

    if n > 9999:
        raise NotImplementedError(f'Elasticsearch max size is 9999!')

    headers = {"Content-Type": "application/json"}
    data = {
        "query": {"bool": {"filter": {"term": {"term": term_id}}}},
        "sort": [{"date": {"order": "desc"}}],
        "size": 9999,
        "_source": ["id"]
    }
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    sitting_nrs = set([hit["_source"]["id"] for hit in response_json["hits"]["hits"]])
    ids = []
    for s in sitting_nrs:
        a, b, c = s.split('-')
        ids.append((int(a), int(b), int(c)))

    if len(ids) != len(set(ids)):
        raise ValueError(f'ID Duplication in index!')

    return sorted(set(ids))


def delete_last_metadata_xmls(metadata_dir, metadata_htmls, dummy=True):
    # most recent xmls shoudl be deleted so that they are downloaded again and refreshed
    to_unlink = []
    max_term_xml_id = max([int(d.stem.split('_')[-1]) for d in metadata_dir.glob('*.xml')])
    latest_term_xml_path = metadata_dir / f'term_{max_term_xml_id}.xml'
    if latest_term_xml_path.is_file():
        to_unlink.append(latest_term_xml_path)

    existing_term_ids = [int(d.stem) for d in metadata_dir.iterdir() if d.is_dir()]
    if len(existing_term_ids) > 0:
        max_term_dir_int = max(existing_term_ids)
        max_term_dir_path = metadata_dir / str(max_term_dir_int)

        existing_sitting_ids = [int(d.stem.split('_')[-1]) for d in max_term_dir_path.glob('*.xml')]
        if len(existing_sitting_ids) > 0:
            max_sitting_id = max(existing_sitting_ids)
            max_sitting_xml = max_term_dir_path / f'sittings_{max_sitting_id}.xml'
            to_unlink.append(max_sitting_xml)

            existing_html_ids = [(int(f.stem.split('-')[0]), int(f.stem.split('-')[1]))
                                 for f in metadata_htmls.glob('*.html')]
            if len(existing_html_ids) > 0:
                max_html_ids = max(existing_html_ids)
                max_html_file = metadata_htmls / f'{max_html_ids[0]}-{max_html_ids[1]}.html'

                logging.info(f'Deleting last term xml: {max_term_dir_path}\nDeleting last sitting xml: {max_sitting_xml}\n'
                             f'Deleting last sitting html: {max_html_file}')
                to_unlink.append(max_html_file)

    if dummy is False:
        for filepath in to_unlink:
            filepath.unlink()


def get_sitting_data_from_html(term_id, sitting_id, metadata_htmls_dir):
    """
    Get HTML from parlament.hu and extract metadata. Sometimes API is missing certain pages.
    """

    save_filename = metadata_htmls_dir / f'{term_id}-{sitting_id}.html'
    if save_filename.is_file():
        with open(save_filename) as fh:
            html_text = fh.read()
    else:
        url = f'https://www.parlament.hu/web/guest/orszaggyulesi-naplo-elozo-ciklusbeli-adatai?p_p_id=hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_auth=rpKswkfn&_hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8_pairAction=%2Finternet%2Fcplsql%2Fogy_naplo.ulnap_felszo%3Fp_lista%3Df%26p_nap%3D{sitting_id}%26p_ckl%3D{term_id}%26p_stilus%3D'
        html = requests.get(url)
        # TODO if exists
        if html.status_code == 200:
            html_text = html.text
        else:
            return None

    soup = BeautifulSoup(html_text, 'lxml')

    title = soup.find('h1')
    if title is None:
        return None
    else:
        date = title.get_text().split('(')[1].split(')')[0].strip()
        split_date = date.split('.')
        if len(split_date) != 4 and all(elem.isnumeric() for elem in split_date) is False:
            raise ValueError(f'Unable to extract date from html of {term_id}-{sitting_id} !')

    try:
        tables = pd.read_html(StringIO(html_text))
    except ValueError:  # No tables found
        return None

    # Column specific
    all_tables_data = {}

    for table in tables:
        try:
            top_column_text = table.columns[0][0]
        except IndexError:
            continue
        topic, bill_titles = topic_and_bill_titles(top_column_text)

        for column_index in table.index:
            id_or_ids = str(table.iloc[column_index, 0])
            if id_or_ids != 'nincs':
                ids = [int(id) for id in id_or_ids.split('-')]
                for id in ids:
                    column_data = {}
                    for index, name in REQUIRED_BY_COLUMN_INDEX.items():
                        value = table.iloc[column_index, index]
                        if isinstance(value, float) and math.isnan(value):
                            value = ''
                        column_data[name] = value
                    felszolalo = column_data.pop('felszolalo')
                    column_data['party'] = get_speaker_party(felszolalo)
                    column_data['felszolalo'] = felszolalo.split('(')[0].strip()
                    column_data['topic'] = topic
                    column_data['bill_title'] = bill_titles

                    all_tables_data[id] = column_data

    if len(all_tables_data) > 0 and save_filename.is_file() is False:
        with open(save_filename, 'w') as fh:
            fh.write(html_text)

    return all_tables_data, date


def check_dir_and_create(dir_path):

    if isinstance(dir_path, Path) is False:
        dir_path = Path(dir_path)
    if dir_path.is_dir() is False:
        dir_path.mkdir(parents=True, exist_ok=True)

    time.sleep(1)

    return dir_path


class Limit:

    def __init__(self, term_id, sitting_id, speech_id):
        self.term_id = term_id
        self.sitting_id = sitting_id
        self.speech_id = speech_id

    def later(self, compare_term, compare_sitting, compare_speech):
        if self.term_id < compare_term:
            return True
        elif self.term_id == compare_term:
            if self.sitting_id == compare_sitting and self.speech_id <= compare_speech:
                return True
            elif self.sitting_id < compare_sitting:
                return True

        return False

    def term_later(self, compare_term):
        if self.term_id <= compare_term:
            return True
        return False

    def term_sitting_later(self, compare_term, compare_sitting):
        if self.term_id < compare_term:
            return True
        elif self.term_id == compare_term:
            if self.sitting_id <= compare_sitting:
                return True

        return False

    def earlier(self, compare_term, compare_sitting, compare_speech):

        if self.term_id > compare_term:  # if limit term is higher
            return True

        if self.term_id == compare_term:  # if limit term is the same
            if self.sitting_id > compare_sitting:  # if sitting limit is higher
                return True
            elif self.sitting_id == compare_sitting:  # if sitting limit is the same
                if self.speech_id > compare_speech:  # if limit speech is higher
                    return True

        return False


def topic_and_bill_titles(es_tit):

    bill_code_pattern = r'\b[A-Z]/\d+'

    bill_codes = re.findall(bill_code_pattern, es_tit)
    if len(bill_codes) == 0:
        return es_tit.strip(), []
    else:
        es_title = es_tit[:es_tit.find(bill_codes[0])].strip()

        bill_titles_full = es_tit.replace(es_title, '').strip()
        if len(bill_codes) == 1:
            return es_title, [bill_titles_full]
        else:
            bill_code_iter = iter(bill_codes)
            next(bill_code_iter)  # skip first
            bill_titles = []
            for bill_code in bill_code_iter:
                bill_title = bill_titles_full[bill_titles_full.find(bill_code):]
                bill_titles.append(bill_title)
                bill_titles_full = bill_titles_full.replace(bill_title, '').strip()

            return es_title, bill_titles


def id_tuples_to_dict(id_tuples):

    result_dict = {}

    for a, b, c in id_tuples:
        if a in result_dict:
            if b in result_dict[a]:
                result_dict[a][b].append(c)
            else:
                result_dict[a][b] = [c]
        else:
            result_dict[a] = {b: [c]}

    return result_dict


def check_speech_data(speech_data_dict):
    required_keys = {key for key in BASE_KEYS if key[0] is True}
    if len(set(speech_data_dict).intersection(required_keys)) != len(required_keys):
        raise ValueError(f'The following keys are missing from speech dict {speech_data_dict["id"]}:'
                         f'{required_keys.difference(speech_data_dict)}')

    for key in required_keys:
        if len(speech_data_dict[key]) == 0 or isinstance(key, BASE_KEYS[key][1]) is False:
            raise ValueError(f'The following keys has an empty or incorrect value from speech dict '
                             f'{speech_data_dict["id"]}: {key}')

    if speech_data_dict['text'].strip() == '':
        logging.error(f'FAILED TO RETRIEVE TEXT FOR SPEECH {speech_data_dict["id"]} !')
        raise ValueError(f'FAILED TO RETRIEVE TEXT FOR SPEECH {speech_data_dict["id"]} !')


def get_speaker_party(tag_text):
    if tag_text.endswith(')'):
        return tag_text.split('(')[-1].replace(')', '').strip()
    else:
        return ''
