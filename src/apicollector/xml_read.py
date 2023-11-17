from copy import copy
from pathlib import Path

from bs4 import BeautifulSoup

from utils import topic_and_bill_titles, get_speaker_party
from configs import SPEECH_DETAILS_BASE, PLENARY_SITTING_DETAILS_BASE
from api_communication import get_kepv_url, speech_url_gen, toc_url_gen

BASE_DIR = Path(__file__).resolve().parent


def create_plenary_sitting_details(sitting_of_term_dict, soup, term_id, sitting_id, from_xml=True, sitting_date=None):

    psd = copy(PLENARY_SITTING_DETAILS_BASE)

    # from xml
    if from_xml:
        sitting_nr = soup.find('felszolalasok')['ulesnap'].strip()
        psd['date'] = soup.find('felszolalasok')['datum'].strip()

        sitting_nr = int(sitting_nr)
        if sitting_nr != sitting_id:
            raise ValueError(f'Inconsistency in sitting XML {term_id}-{sitting_id} !')

    else:
        sitting_nr = sitting_id
        if sitting_date is None:
            raise ValueError(f'sitting_date cant be None if using html!')

        psd['date'] = sitting_date

    psd['type'] = sitting_of_term_dict['ulesjelleg']
    # sitting_day
    psd['sitting_uid'] = f'{term_id}-{sitting_nr}'
    # duration_raw
    # video_time
    # day_of_session
    # video_url
    psd['day'] = sitting_of_term_dict['nap']
    psd['session'] = sitting_of_term_dict['ulszak']
    psd['sitting_nr'] = sitting_nr
    psd['toc_url'] = toc_url_gen(term_id, sitting_nr)
    # duration
    psd['term'] = str(term_id)

    return psd


def create_sittings_dict(file_path):
    with open(file_path) as fh:
        soup = BeautifulSoup(fh.read(), 'lxml-xml')

    s_d = {}
    for sitting in soup.find_all('ulesnap'):
        s_d[int(sitting.find('ulnap').get_text(strip=True))] = {
            'datum': sitting.find('datum').get_text(strip=True),
            'nap': sitting.find('nap').get_text(strip=True),
            'ulszak': sitting.find('ulszak').get_text(strip=True),
            'ulesjelleg': sitting.find('ulesjelleg').get_text(strip=True)
        }
    return s_d


def create_speeches_dict(soup):

    s_d = {}
    esemeny_list = soup.find_all('esemeny')
    for esemeny in esemeny_list:
        if len(esemeny.find_all()) > 0:
            esemeny_title = esemeny.contents[0]
            topic, bill_titles = topic_and_bill_titles(esemeny_title)

            for speech in esemeny.find_all('felszolalas'):
                speech_id = speech.find('sorszam').get_text(strip=True)
                if speech_id != 'nincs' and len(speech_id) > 0:
                    speech_id = int(speech_id)
                    if speech_id not in s_d:
                        s_d[speech_id] = {
                            'felszolalo': speech.find('felszolalo').get_text().split('(')[0].strip(),
                            'felszkezdete': speech.find('felszkezdete').get_text(strip=True),
                            'videoido': speech.find('videoido').get_text(strip=True),
                            'party': get_speaker_party(speech.find('felszolalo').get_text(strip=True)),
                            'topic': topic,
                            'bill_title': bill_titles,
                            'type': speech.find('felsztip').get_text(strip=True)
                        }

    return s_d


def create_speech_dict(speech_soup, speeches_dict, plenary_sitting_details, term_id, sitting_id, last_speech_id,
                       next_speech_id, mp_urls):
    """
    Extract speech specific data from speech XML and insert into dict
    """
    speech_id = speech_soup.find('felszolalas')['sorsz']
    speech_id = int(speech_id)

    sd = copy(SPEECH_DETAILS_BASE)

    sd['url'] = speech_url_gen(term_id, sitting_id, speech_id)
    sd['type'] = speech_soup.find('felsz_oka').get_text(strip=True)

    text = speech_soup.find('felsz_szovege').get_text(strip=True)
    if len(text) > 0:
        sd['text'] = text
    else:
        raise ValueError(f'Empty text in {term_id}-{sitting_id}-{speech_id}. Stopping.')

    sd['id'] = f'{term_id}-{sitting_id}-{speech_id}'

    if speech_id not in speeches_dict:
        raise KeyError(f'Speech ID {speech_id} not found in speech_dict for {term_id}-{sitting_id} !')
    sd['started_at'] = speeches_dict[speech_id]['felszkezdete']

    if last_speech_id is not None:
        sd['prev_speech_url'] = speech_url_gen(last_speech_id[0], last_speech_id[1], last_speech_id[2])
        # sd['prev_speech_url'] = adj_speech_url_gen('prev', last_speech_id, term_id, sitting_id, speech_id)
    else:
        sd['prev_speech_url'] = ''

    if next_speech_id is not None:
        sd['next_speech_url'] = speech_url_gen(next_speech_id[0], next_speech_id[1], next_speech_id[2])
    else:
        sd['next_speech_url'] = ''

    sd['duration'] = speech_soup.find('felsz_ideje').get_text(strip=True)
    speaker_tag = speech_soup.find('felszolalo')
    if speaker_tag is None:
        raise ValueError(f'Speaker not found in {term_id}-{sitting_id}-{speech_id}')
    sd['speaker_url'] = get_kepv_url(speaker_tag, mp_urls)
    sd['speaker_party'] = get_speaker_party(speaker_tag.get_text(strip=True))
    sd['bill_title'] = speeches_dict[speech_id]['bill_title']
    sd['topic'] = speeches_dict[speech_id]['topic'],
    sd['speaker'] = speech_soup.find('felszolalo').get_text(strip=True).split('(')[0].strip()
    sd['plenary_sitting_details'] = plenary_sitting_details

    return sd


def get_xml(text):
    soup = BeautifulSoup(text, 'xml')
    return soup


def get_term_sitting_ids(soup):

    sitting_ids = set()
    for sitting in soup.find_all('ulnap'):
        sitting_id = int(sitting.get_text(strip=True))
        sitting_ids.add(sitting_id)

    return sorted(sitting_ids)


def get_sitting_speech_ids(sitting_speech_list_soup):

    sitting_speech_id_strs = [tag.get_text(strip=True) for tag in sitting_speech_list_soup.find_all('sorszam')]
    sitting_speech_ids = set()
    for speech_id in sitting_speech_id_strs:
        if speech_id != 'nincs':
            sitting_speech_ids.add(int(speech_id))

    return sorted(sitting_speech_ids)


