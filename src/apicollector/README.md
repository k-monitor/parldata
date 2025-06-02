# API Collector

Collect data published on the official parlament.hu API with an authenticated API KEY into a JSONL file.

Requires `Python 3.8 >=`

**To install:**
<br>(create virtualenv if needed)
<br>`pip install -r requirements.txt`

**To run:**<br>
`python3 main.py MODE SAVE_DIR API_KEY MP-URLS-JSON-PATH start_term start_sitting start_speech end_term end_sitting end_speech` 

- `MODE`:
  - `index`: Only download and convert XMLs of speeches that are not already indexed on elasticsearch 
    (must add index_url optional argument: `-i https://...`)
  - `download`: Download and convert XMLs of speeches that are not already downloaded.
  - `all`: Download and convert all available XMLs.
- `SAVE_DIR`: Directory to save output JSONL file to
- `API_KEY`: Access token for parlament.hu
- `MP-URLS-JSON-PATH`: Json file with key-value pairs of MP name and URL from parlament.hu
- `start_term`: Term to start from
- `start_sitting`: Sitting ID to start from
- `start_speech`: Speech ID to start from
- `end_term`: Term ID to go until
- `end_sitting`: Sitting ID to go until
- `end_speech`: Speech ID to go until

_Optional arg:_
- `INDEX_URL`: Url of elasticsearch server with index query ending (required for `index` mode)
