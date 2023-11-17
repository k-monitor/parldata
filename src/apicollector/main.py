import json
import logging
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

from collect import build_collection_of_downloaded_xml_ids, TERM_SITTING_XML_SAVE_DIRECTORY, \
    SITTING_HTML_SAVE_DIRECTORY, build_set_of_available_xml_ids, SPEECH_XML_SAVE_DIRECTORY, write_json_data, \
    term_sitting_speeches_metadata, gen_create_json_data_from_ids
from utils import Limit, delete_last_metadata_xmls, get_last_n_existing_indexes_for_term, id_tuples_to_dict

log_dir = Path(__file__).resolve() / 'logs'
if log_dir.is_dir() is False:
    log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / datetime.now().strftime("%Y-%m-%dT%H:%M")
logging.basicConfig(filename=f'{str(log_file)}.log', encoding='utf-8', level=logging.DEBUG)


def get_speeches_and_convert_to_jsonl(api_key, index_url, save_dir_path, mp_urls, start, end=Limit(43, 1, 1),
                                      mode='index', index_len=9999):

    min_indexed = (0, 0, 0)  # Only for working with indexed files e.g.: elasticsearch server

    # Make sure directory set as save_dir exists
    save_dir_path = Path(save_dir_path)
    if save_dir_path.is_dir() is False:
        raise ValueError(f'save_dir_path received a non-valid directory path {str(save_dir_path)}')

    # Delete last metadata files so they are downloaded again and refreshed if new data is available
    delete_last_metadata_xmls(TERM_SITTING_XML_SAVE_DIRECTORY, SITTING_HTML_SAVE_DIRECTORY, dummy=False)

    # Get ID tuples from XML metadata files, metadata taken from HTMLs (unavailable as xml),
    # dates of sittings form HTMLs
    set_of_available_xml_ids, sittings_metadata_from_html, sitting_dates_from_html = \
        build_set_of_available_xml_ids(TERM_SITTING_XML_SAVE_DIRECTORY, api_key, start, SITTING_HTML_SAVE_DIRECTORY,
                                       end_term=end.term_id)

    # Get IDs according to mode
    # Only those that are not indexed
    if mode == 'index':
        # Get the last n (9999) indexed term-sitting-speech id tuples from the index
        if index_url is None:
            raise ValueError('No index_url provided!')
        # !!! Change this function if elasticsearch layout changes, or documents are indexed on different platform !!!
        last_n_indexed_ids = get_last_n_existing_indexes_for_term(start.term_id, url=index_url, n=index_len)

        min_indexed = min(last_n_indexed_ids) # For error handling
        ids_to_not_process = last_n_indexed_ids

    # Those that are not downloaded
    elif mode == 'download':
        ids_to_not_process = build_collection_of_downloaded_xml_ids(SPEECH_XML_SAVE_DIRECTORY, start)
    # All IDs
    elif mode == 'all':
        ids_to_not_process = ()
    else:
        raise ValueError(f'Bad parameter for mode!')

    ids_to_process = {i for i in set_of_available_xml_ids if i not in ids_to_not_process
                      and start.later(i[0], i[1], i[2]) and end.earlier(i[0], i[1], i[2])}

    ids_to_process_as_string = "\n".join([" ".join([f"{i_[0]}-{i_[1]}-{i_[2]}" for i_ in list(ids_to_process)[i:i + 10]])
                                          for i in range(0, len(ids_to_process), 10)])
    logging.info(f'Processing the following IDs: {ids_to_process_as_string}')

    if min(ids_to_process) < min_indexed:
        raise ValueError(f'Earliest ID to process is earlier then earliest retrieved index! Cannot be sure that '
                         f'indexing will be contiguous!')
    else:
        ids_to_process = sorted(ids_to_process)  # for consistency

    # Convert ID tuples to dict --> [term][sitting] = [speech1, speech2, ...]
    ids_to_process_dict = id_tuples_to_dict(ids_to_process)

    # Create a dictionary that holds: the sitting specific metadata, the plenary_sitting_details for each sitting
    speeches_data = term_sitting_speeches_metadata(ids_to_process_dict,
                                                   sittings_metadata_from_html,
                                                   sitting_dates_from_html,
                                                   TERM_SITTING_XML_SAVE_DIRECTORY)

    # There are new IDs to process (download and convert XMLs or just convert existing XMLs)
    if len(ids_to_process_dict) > 0:
        json_data_it = gen_create_json_data_from_ids(ids_to_process_dict, speeches_data, set_of_available_xml_ids,
                                                     api_key, mp_urls)
        write_json_data(ids_to_process_dict, json_data_it, save_dir_path)


def main():
    parser = ArgumentParser()

    parser.add_argument('mode', type=str, choices=['index', 'download', 'all'],
                        help='index: Download and convert only those speech XMLs that are not indexed (e.g.: on '
                             'elasticsearch)\ndownload: Download and convert those speech XMLs that are not downloaded'
                             '\nall: Download and convert all speech XMLs within range. (between start and end)')
    parser.add_argument('save_dir', type=str, help='Directory path to save jsonl files to.')
    parser.add_argument('api_key', type=str, help='API key for parlament.hu')
    parser.add_argument('mp_urls_json', type=str, default='kepviselo_urls.json',
                        help='json file with key-value pairs of MP name: parlament.hu url')

    # ID to start from
    parser.add_argument('start_term', type=int)
    parser.add_argument('start_sitting', type=int)
    parser.add_argument('start_speech', type=int)

    # ID to goo until
    parser.add_argument('end_term', type=int)
    parser.add_argument('end_sitting', type=int)
    parser.add_argument('end_speech', type=int)

    parser.add_argument('-i', '--index_url', type=str, default=None, help='Index URL of elasticsearch server.')
    args = parser.parse_args()

    # Create save_dir if it does not yet exist
    save_dir = Path(args.save_dir)
    if save_dir.is_dir() is False:
        save_dir.mkdir(parents=True, exist_ok=True)

    with open(args.mp_urls_json) as fh:
        mp_urls = json.load(fh)

    get_speeches_and_convert_to_jsonl(args.api_key, args.index_url, save_dir, mp_urls,
                                      Limit(args.start_term, args.start_sitting, args.start_speech),
                                      end=Limit(args.end_term, args.end_sitting, args.end_speech), mode='index')


if __name__ == '__main__':
    main()
