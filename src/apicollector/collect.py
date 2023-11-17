import logging
from pathlib import Path
from datetime import datetime

import jsonlines
from bs4 import BeautifulSoup

from utils import get_sitting_data_from_html, check_speech_data, check_dir_and_create
from xml_read import create_sittings_dict, create_speeches_dict, create_plenary_sitting_details, \
    create_speech_dict, get_xml, get_term_sitting_ids, get_sitting_speech_ids
from api_communication import fetch_speech_content, fetch_sitting_speech_listing, \
    fetch_term_sitting_listing

SPEECH_XML_SAVE_DIRECTORY = check_dir_and_create(Path(__file__).resolve().parent / 'data')
TERM_SITTING_XML_SAVE_DIRECTORY = check_dir_and_create(Path(__file__).resolve().parent / 'metadata')
SITTING_HTML_SAVE_DIRECTORY = check_dir_and_create(Path(__file__).resolve().parent / 'metadata_htmls')


def build_collection_of_downloaded_xml_ids(save_directory, start_from) -> set:
    """
    :param save_directory: Directory where API response xmls are saved
        structure should be:
            - term_dir
                - sitting_dir
                    - speech_dir
            - term_dir
            ...
    :param start_from: Limit object with term-sitting-speech IDs
    :return: collections dictionary that contains all saved speeches
    """

    collections_set = set()

    for term_dir_path in save_directory.iterdir():
        if term_dir_path.is_dir() and term_dir_path.stem.isnumeric():  # take only directories
            # take only directories that are titled after their term (e.g.: 42)
            term_num = int(term_dir_path.stem)

            for sitting_dir_path in term_dir_path.iterdir():
                if sitting_dir_path.is_dir() and sitting_dir_path.stem.isnumeric():  # take only directories
                    sitting_num = int(sitting_dir_path.stem)

                    for speech_file_path in sitting_dir_path.glob('*.xml'):
                        speech_num = speech_file_path.stem.split('-')[-1]
                        if speech_num.isnumeric():
                            speech_num = int(speech_num)
                            if start_from.later(term_num, sitting_num, speech_num):
                                collections_set.add((term_num, sitting_num, speech_num))

    return set(sorted(collections_set))


def build_set_of_available_xml_ids(metadata_dir, api_key, start_from, metadata_htmls_dir, end_term=60) -> tuple:

    metadata_list = []
    speech_data_from_html = {}
    sitting_dates_from_html = {}

    for term_id in range(start_from.term_id, end_term + 1):  # Current term is 42
        if start_from.term_later(term_id):
            # check if term xml exists
            term_xml_path = metadata_dir / f'term_{term_id}.xml'
            if term_xml_path.is_file() is False:
                # download term xml
                term_xml_response_text = fetch_term_sitting_listing(term_id, api_key)

                if term_xml_response_text is not None:

                    term_xml = get_xml(term_xml_response_text)

                    with open(term_xml_path, 'w') as fh:
                        fh.write(term_xml.prettify())
                else:
                    logging.info(f'Failed to retrieve TERM SITTINGS XML for {term_id} !')
                    continue

            else:
                with open(term_xml_path) as fh:
                    term_xml = get_xml(fh.read())

            term_sitting_ids = get_term_sitting_ids(term_xml)

            for sitting_id in term_sitting_ids:

                if start_from.term_sitting_later(term_id, sitting_id):

                    # check if sittings direcotry exists
                    term_directory_path = metadata_dir / str(term_id)
                    if term_directory_path.is_dir() is False:
                        term_directory_path.mkdir(exist_ok=True, parents=True)

                    sittings_xml_path = term_directory_path / f'sittings_{sitting_id}.xml'

                    if sittings_xml_path.is_file() is False:

                        sittings_xml_response_text = fetch_sitting_speech_listing(term_id, sitting_id, api_key)

                        success_from_xml = False
                        # If none it means the response had no content - not a valid term-sitting combination
                        if sittings_xml_response_text is not None:
                            success_from_xml = extract_speech_ids_from_sittings_xml_text(metadata_list, sitting_id,
                                                                                         sittings_xml_path,
                                                                                         sittings_xml_response_text,
                                                                                         start_from, term_id)
                    else:
                        with open(sittings_xml_path) as fh:
                            success_from_xml = extract_speech_ids_from_sittings_xml_text(metadata_list, sitting_id,
                                                                                         sittings_xml_path, fh.read(),
                                                                                         start_from, term_id)
                    if success_from_xml is False:
                        logging.error(f'FAILED TO RETRIEVE VALID SITTINGS XML FOR {term_id}-{sitting_id}, '
                                      f'TRYING WITH PANDAS !')
                        sitting_metadata_from_html = get_sitting_data_from_html(term_id, sitting_id, metadata_htmls_dir)

                        if sitting_metadata_from_html is not None:
                            speech_data_from_html[(term_id, sitting_id)] = sitting_metadata_from_html[0]
                            sitting_dates_from_html[(term_id, sitting_id)] = sitting_metadata_from_html[1]

    if len(speech_data_from_html) > 0:
        for term_sitting_ids, speech_dict in speech_data_from_html.items():
            for speech_id in speech_dict:
                metadata_list.append((term_sitting_ids[0], term_sitting_ids[1], speech_id))

    return set(sorted(metadata_list)), speech_data_from_html, sitting_dates_from_html


def extract_speech_ids_from_sittings_xml_text(metadata_list, sitting_id, sittings_xml_path, sittings_xml_text,
                                              start_from, term_id) -> bool:
    """
    Fill metadata_list from XML text of speech API response.
    """
    sittings_xml = get_xml(sittings_xml_text)
    sitting_speech_ids = get_sitting_speech_ids(sittings_xml)
    if len(sitting_speech_ids) == 0:
        success_from_xml = False
        logging.error(f'No speech IDs could be extracted from xml: {sittings_xml_path}')
    else:
        success_from_xml = True
        for speech_id in sitting_speech_ids:
            if start_from.later(term_id, sitting_id, speech_id):
                metadata_list.append((term_id, sitting_id, speech_id))

        with open(sittings_xml_path, 'w') as fh:
            fh.write(sittings_xml.prettify())
            logging.info(f'SAVED XML {sittings_xml_path.stem}')

    return success_from_xml


def term_sitting_speeches_metadata(ids_to_download_dict, sittings_metadata_from_html,
                                   sitting_dates_from_html, metadata_directory) -> dict:
    """
    Create dictionary with term-sitting keys and tuple of following values:
        - sitting_speeches_data: dict of metadata specific to certain speech
        - plenary_sitting_details: Metadata specific to sitting
    """
    term_sittings_dicts, sitting_speeches_dict = {}, {}

    for term_id in ids_to_download_dict:
        sittings_of_term_dict = term_sittings_dicts.get(term_id)
        if sittings_of_term_dict is None:
            sittings_of_term_dict = create_sittings_dict(metadata_directory / f'term_{term_id}.xml')
            term_sittings_dicts[term_id] = sittings_of_term_dict

        for sitting_id in ids_to_download_dict[term_id]:
            sitting_speeches_data, plenary_sitting_details = None, None

            # 1. Try from xml
            from_xml = False
            sitting_xml = metadata_directory / str(term_id) / f'sittings_{sitting_id}.xml'

            if sitting_xml.is_file():
                with open(sitting_xml) as fh:
                    sitting_soup = BeautifulSoup(fh.read(), 'lxml-xml')
                sitting_speeches_data = create_speeches_dict(sitting_soup)

                if len(sitting_speeches_data) > 1:
                    from_xml = True
                    plenary_sitting_details = create_plenary_sitting_details(sittings_of_term_dict[sitting_id],
                                                                             sitting_soup, term_id, sitting_id)
            if from_xml is False:  # 2. Try from html
                sitting_speeches_data = sittings_metadata_from_html.get((term_id, sitting_id))
                sitting_date = sitting_dates_from_html.get((term_id, sitting_id))
                if sitting_speeches_data is None:
                    raise NotImplementedError(f'Neither xml or html could provide sitting_speeches_data from '
                                              f'{term_id}-{sitting_id}')

                plenary_sitting_details = create_plenary_sitting_details(sittings_of_term_dict[sitting_id],
                                                                         None, term_id, sitting_id, from_xml=False,
                                                                         sitting_date=sitting_date)

            sitting_speeches_dict[(term_id, sitting_id)] = (sitting_speeches_data, plenary_sitting_details)

    return sitting_speeches_dict


def _download_or_open_speech_xml(term_id, sitting_id, speech_id, save_directory, api_key, time_sleep):

    sitting_directory = save_directory / str(term_id) / str(sitting_id)
    speech_xml_path = sitting_directory / f'{term_id}-{sitting_id}-{speech_id}.xml'

    save = False
    if speech_xml_path.is_file() is False:
        # make sure directory is created if missing
        if sitting_directory.is_dir() is False:
            sitting_directory.mkdir(exist_ok=True, parents=True)

        # get API response
        speech_xml_text = fetch_speech_content(term_id, sitting_id, speech_id, api_key, time_sleep=time_sleep)

        # convert to XML
        speech_xml = get_xml(speech_xml_text)

        # Save XML (if it has text)
        save = True

    else:
        with open(speech_xml_path) as fh:
            speech_xml = get_xml(fh.read())

    felsz_szovege_tag = speech_xml.find('felsz_szovege')
    if felsz_szovege_tag is not None and len(felsz_szovege_tag.get_text(strip=True)) > 0:
        if save:
            with open(sitting_directory / f'{term_id}-{sitting_id}-{speech_id}.xml', 'w') as fh:
                fh.write(speech_xml.prettify())
    else:
        logging.error(f'Speech XML {term_id}-{sitting_id}-{speech_id} contains no text!')

    return speech_xml


def gen_create_json_data_from_ids(ids_to_download_dict, speeches_data, set_of_available_xml_ids, api_key, mp_urls,
                                  time_sleep=2):

    for term, sittings in ids_to_download_dict.items():

        all_c = len(sittings)

        for c, (sitting, speeches) in enumerate(sittings.items(), start=1):
            print(f'Processing {term}-{sitting} speeches! Term: {term} {c}/{all_c}')

            sitting_speeches_data, psd = speeches_data[(term, sitting)]

            for speech_id in speeches:
                prev_id = (term, sitting, speech_id - 1)
                if prev_id not in set_of_available_xml_ids:
                    prev_id = None

                next_id = (term, sitting, speech_id + 1)
                if next_id not in set_of_available_xml_ids:
                    next_id = None

                speech_soup = _download_or_open_speech_xml(term, sitting, speech_id, SPEECH_XML_SAVE_DIRECTORY, api_key,
                                                           time_sleep=time_sleep)
                speech_data_as_dict = create_speech_dict(speech_soup, sitting_speeches_data, psd, term, sitting,
                                                         prev_id, next_id, mp_urls)

                check_speech_data(speech_data_as_dict)

                yield speech_data_as_dict


def write_json_data(ids_to_download_dict, json_data_it, save_dir_path):
    min_term = min(ids_to_download_dict.keys())
    min_sitting = min(ids_to_download_dict[min_term].keys())
    min_speech = min(ids_to_download_dict[min_term][min_sitting])
    max_term = max(ids_to_download_dict.keys())
    max_sitting = max(ids_to_download_dict[max_term].keys())
    max_speech = max(ids_to_download_dict[max_term][max_sitting])
    first, last = f'{min_term}-{min_sitting}-{min_speech}', f'{max_term}-{max_sitting}-{max_speech}'

    filepath = save_dir_path / f'{first}_to_{last}.jsonl'

    with jsonlines.open(filepath, 'w') as writer:
        for data in json_data_it:
            logging.info(f'WRITING {data["id"]} TO {filepath}')
            writer.write(data)
