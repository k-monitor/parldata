BASE_KEYS = {
    'url': (True, (str, )),
    'type': (True, (str, )),
    'text': (True, (str, )),
    'id': (True, (str, int)),
    'started_at': (False, (str, )),
    'next_speech_url': (False, (str, )),
    'prev_speech_url': (False, (str, )),
    'duration': (True, (str, )),
    'speaker_url': (True, (str, )),
    'video_url': (False, (str, )),
    'speaker_party': (True, (str, )),
    'bill_url': (False, (list, str)),
    'bill_title': (False, (list, str)),  #?
    'topic': (True, (list, str)),
    'speaker': (True, (str, )),
    'plenary_sitting_details': (True, (dict, ))
}

PSD_KEYS = {  # plenary_sitting_details
    'date': (True, (str, )),
    'type': (True, (str, )),
    'sitting_id': (False, (str, )),  # Ez az ülés
    'sitting_day': (False, (str, )),
    'sitting_uid': (True, (str, )),  # Ez az term-sitting_nr
    'duration_raw': (False, (str, )),
    'video_time': (False, (str, )),
    'day_of_session': (False, (str, )),
    'video_url': (False, (str, )),
    'day': (True, (str, )),
    'session': (True, (str, )),
    'sitting_nr': (True, (str, int)),
    'toc_url': (True, (str, )),
    'duration': (False, (str, )),
    'term': (True, (str, int)),
    'header': (False, (str, )),
    'note': (False, (str, )),
}
TABLE_COLUMNS = {'speech_id', 'felszolalo', 'type', 'kormany_bizottság', 'felszkezdete', 'videoido'}
REQUIRED_BY_COLUMN_INDEX = {1: 'felszolalo', 2: 'type', 4: 'felszkezdete', 5: 'videoido'}
SPEECH_DETAILS_BASE = {
    "url": "",
    "type": "",
    "text": "",
    "id": "",
    "started_at": "",
    "next_speech_url": "",
    "duration": "",
    "speaker_url": "",
    "video_url": "",
    "speaker_party": "",
    "bill_url": "",
    "topic": "",
    "prev_speech_url": "",
    "bill_title": [""],
    "speaker": ""}
PLENARY_SITTING_DETAILS_BASE = {
    "date": "",
    "type": "",
    "sitting_id": "",
    "sitting_day": "",
    "sitting_uid": "",
    "duration_raw": "",
    "video_time": "",
    "day_of_session": "",
    "video_url": "",
    "day": "",
    "session": "",
    "sitting_nr": "",
    "toc_url": "",
    "duration": "",
    "term": ""}
