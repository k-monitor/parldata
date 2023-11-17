import time
import logging

import requests


BASE_URL = 'https://parlament.hu'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0'
                         '.0.0 Safari/537.36'}


def fetch_speech_content(p_ckl, p_uln, p_felsz, access_token, time_sleep: (None, int) = None):
    logging.info(f'FETCHING SPEECH CONTENT {p_ckl}-{p_uln}-{p_felsz}')
    url = f'{BASE_URL}/cgi-bin/web-api-pub/felszolalas.cgi?access_token={access_token}&p_ckl={p_ckl}&p_uln={p_uln}' \
          f'&p_felsz={p_felsz}'

    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        logging.debug(f'Requesting {p_ckl}-{p_uln}-{p_felsz} failed with {e} ! Retrying in 15 seconds...')
        time.sleep(15)
        response = requests.get(url)

    response.encoding = 'utf-8'

    response_text = response.text

    if response_text == '<?xml version="1.0" encoding="utf-8"?>\n<felszolalas/>\n':
        return None

    if time_sleep is not None:
        time.sleep(time_sleep)

    return response_text


def fetch_sitting_speech_listing(p_ckl, p_nap, access_token):
    logging.info(f'FETCHING SITTING SPEECH LISTING - {p_ckl}-{p_nap}')
    url = f'{BASE_URL}/cgi-bin/web-api-pub/felszolalasok.cgi?access_token={access_token}&p_ckl={p_ckl}&p_nap={p_nap}'
    response = requests.get(url)
    response.encoding = 'utf-8'

    response_text = response.text

    if response_text == '<?xml version="1.0" encoding="utf-8"?>\n<felszolalasok/>\n':
        return None

    return response_text


def fetch_term_sitting_listing(p_ckl, access_token):
    """
    Fetch xml of term sittings - the first layer of xmls.
    :param p_ckl: term_number
    :param access_token: API ACCESS TOKEN
    :return:
    """
    logging.info(f'FETCHING TERM SITTING LISTING {p_ckl}')
    p_ckl = str(p_ckl)

    url = f'{BASE_URL}/cgi-bin/web-api-pub/ulesnap.cgi?access_token={access_token}&p_ckl={p_ckl}'
    response = requests.get(url)
    response.encoding = 'utf-8'

    response_text = response.text

    if response_text == '<?xml version="1.0" encoding="utf-8"?>\n<ulesnapok/>\n' or response_text == 'Nincs adat\n':
        return None

    return response_text


def get_kepv_url(speaker_tag, mp_urls):
    url = mp_urls.get(speaker_tag.get_text(strip=True))
    if url is None:
        return f"https://www.parlament.hu/web/guest/orszaggyulesi-naplo-elozo-ciklusbeli-adatai?p_p_id=hu_parlament_c" \
               f"ms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_aut" \
               f"h=l1cdCEL9&_hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8_pairAction=%2Finternet%2Fc" \
               f"plsql%2F{speaker_tag['href']}"
    else:
        return url


def speech_url_gen(t_id, sit_id, sp_id):
    t_id, sit_id, sp_id = str(t_id), str(sit_id), str(sp_id)

    return f'https://www.parlament.hu/web/guest/orszaggyulesi-naplo-elozo-ciklusbeli-adatai?p_p_id=hu_parlament_cms_p' \
           f'air_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_auth=3ze1nt' \
           f'cj&_hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8_pairAction=%2Finternet%2Fcplsql%2Fogy_' \
           f'naplo.naplo_fadat%3Fp_ckl%3D{t_id}%26p_uln%3D{sit_id}%26p_felsz%3D{sp_id}%26p_szoveg%3D%26p_felszig%3' \
           f'D{sp_id}'


def toc_url_gen(t_id, s_id):
    t_id, s_id = str(t_id), str(s_id)

    return f"https://www.parlament.hu:443/web/guest/orszaggyulesi-naplo-elozo-ciklusbeli-adatai?p_p_id=hu_parlament_c" \
           f"ms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_auth=j3" \
           f"e1NXrC&_hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8_pairAction=%2Finternet%2Fcplsql%2F" \
           f"ogy_naplo.ulnap_felszo%3Fp_lista%3DA%26p_nap%3D{s_id}%26p_ckl%3D{t_id}"
