# setup for elasticsearch
index_settings = {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.max_result_window": 700000,
    "index": {
            "analysis": {
                "analyzer": "simple"
            }
    }
}



doc_mapping = {
    "doc_type": {
        "_all": {
            "enabled": True},
        "properties": {
            "stemmed": {
                "type": "text",
                "index": "analyzed",
                "analyzer": "simple",
                "fielddata": True,
                "term_vector": "yes"
            },
            "raw": {
                "type": "text",
                "index": "analyzed",
                "analyzer": "simple"
            },
            "extractive_summary": {
                "type": "text",
                "index": "analyzed",
                "analyzer": "simple"
            },
            "date": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
            },
            "speechno": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "speaker": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "spekerid": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "category": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "role": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "party": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "url": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "hash": {
                "type": "keyword",
                "index": "not_analyzed"
            },
            "lexical_diversity": {
                "type": "float",
                "index": "not_analyzed"
            },
            "length": {
                "type": "integer",
                "index": "not_analyzed"
            },
            "topic": {
                "type": "keyword",
                "index": "not_analyzed"
            }
        }
    }
}

# json fields
#['topic_number', 'bill_url', 'duration', 'speaker_anon', 'speaker_norm',
# 'id', 'committee', 'topic', 'gender', 'lemmatized', 'prev_speech_url', 'speaker', 'bigram', 'started_at', 'bill_title', 'speaker_party', 'role', 'url', 'text', 'named_entities', 'speaker_url', 'next_speech_url', 'stemmed', 'plenary_sitting_details', 'video_url', 'type', 'speaker_party_norm']