import json
from os import listdir
from os.path import isfile, join

fid_topic = {}
with open('data/corpus/docs_topic.tsv') as infile:
    for l in infile:
        fid, topics = l.strip().split('\t')
        topic = topics.split('|')[0]
        fid_topic[fid] = topic

in_path = 'data/raw'
out_path = 'data/final'
jsons = [f for f in listdir(in_path) if isfile(join(in_path, f))]
for j in jsons:
    with open(join(in_path, j)) as data:
        d = json.load(data)
        for e in d:
            e['topic_number'] = fid_topic[e['id']]
        with open(join(out_path, j), 'w') as outfile:
            json.dump(d, outfile)
