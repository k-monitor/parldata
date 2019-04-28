# Elasticsearch configs of Hungarian parlamentary debate search engine


## 1. Requirements

Elasticsearch 7.0 with hunspell and hungarian hunspell dictionaries installed


## 2. Contents of this directory

- `mapping.json`: defines the structure of the Elasticsearch index
- `search-template.mst`: Query template for facated search
- `suggestion-template.mst`: Query template for suggestions
- `docker-compose.yml`: docker-compose file describing a test environment


## 3. Running the test environment and proposed workflow

### 3.1. Start the test environment if it is not running yet

    docker-compose up -d


You might need to set `vm.max_map_count` for Elasticsearch to start

    sudo sysctl -w vm.max_map_count=262144

### 3.2. Create the index with the mapping

    curl -XPUT -H "Content-Type: application/json" http://127.0.0.1:9200/parldata_v2 -d @./mapping.json

The index name is versioned, and the search uses aliases, so it can be recreated while the old version is still serviing the requests

### 3.3. Store the query templates

    curl -XPOST http://127.0.0.1:9200/_scripts/filtered_query_v3?pretty -H "Content-Type: application/json" --data @search-template.mst

    curl -XPOST http://127.0.0.1:9200/_scripts/suggest_v1?pretty -H "Content-Type: application/json" --data @suggestion-template.mst

### 3.4. Index data with the [indexer](https://github.com/k-monitor/parldata/tree/master/src/indexer)


### 3.5. Setup the aliases for the search

If it not exist yet:

    curl -XPOST http://127.0.0.1:9200/_aliases -H "Content-Type: application/json"-d '
    { "actions" : [
        { "add"    : { "index" : "parldata_v2", "alias" : "parldata" } }
    ]}'

Or if  you need to move it to the new index:

    curl -XPOST http://127.0.0.1:9200/_aliases -H "Content-Type: application/json" -d '
    { "actions" : [
        { "remove" : { "index" : "pardata_v1", "alias" : "parldata" } },
        { "add"    : { "index" : "parldata_v2", "alias" : "parldata" } }
    ]}'

### 3.6. Execute test searches and check the results

Suggestion:

    curl http://127.0.0.1:9200/parldata/_search/template?pretty -H "Content-Type: application/json" -d '
    {
      "id": "suggest_v1",
      "params": {
        "q": "had"
      }
    }'


Query:

    curl http://127.0.0.1:9200/parldata/_search/template?pretty -H "Content-Type: application/json" -d '
    {
      "id": "filtered_query_v3",
      "params": {
        "q": "atomerőmű",
        "size": 10
      }
    }'


### 3.7. Delete old index if it is not needed anymore

    curl -XDELETE http://127.0.0.1:9200/parldata_v1



## 4. Available search template params

- `q`: the query
- `size`: number of records to return, default: 20
- `from`: the offset of records for paging, default: 0
- `filter.date`: filter for the date of the speech, optional
- `filter.date.from`: date of the speech filtering as interval, starting value, optional
- `filter.date.to`: date of the speech filtering as interval, ending value, optional. Requires `filter.date.from` to be specified.
- `filter.speakers`: filter for the speakers, optional. Expects an array of values.
- `filter.speaker_parties`: filter for the speaker parties, optional. Expects an array of values


Example:

    curl http://127.0.0.1:9200/parldata/_search/template?pretty -H "Content-Type: application/json" -d '
    {
      "id": "filtered_query_v3",
      "params": {
        "q": "atomerőmű",
        "size": 10,
        "filter.date.from": "2017.01.01.",
        "filter.date.to":"2017.12.31.",
        "filter.speaker_parties":["Fidesz", "KDNP", "LMP", "Jobbik"],
        "filter.speakers":["Lázár János", "Dr. Szél Bernadett", "Sneider Tamás"]
      }
    }'
