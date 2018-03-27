import pickle
import operator
import itertools
import ijson.backends.yajl2 as ijson
from os import listdir
from os.path import isfile, join
from collections import Counter
from gensim import corpora


in_path = 'data/raw'
jsons = [f for f in listdir(in_path) if isfile(join(in_path, f))]
jsons = sorted(jsons)

good_pos = ['noun', 'adj', 'propn']

fids = []
texts = []
for f in jsons:
    with open(join(in_path, f), 'rb') as infile:
        parser = ijson.parse(infile)
        for prefix, type, value in parser:
            if prefix == 'item.id':
                fid = value.strip()
                fids.append(fid)
            if prefix == 'item.lemmatized':
                wds = value.strip().lower().split()
                filtered = []
                for w in wds:
                    w, pos = w.rsplit('_', 1)
                    if pos in good_pos:
                        filtered.append(w)
                texts.append(filtered)

with open('src/topicmodel/data/corpus/stoplist.txt', 'r') as infile:
    stoplist = []
    for l in infile:
        stoplist.append(l.strip())

merged = list(itertools.chain(*texts))
wfreq = Counter(merged)
sorted_wf = sorted(wfreq.items(), key=operator.itemgetter(1), reverse=True)
sorted_wf = [e[0] for e in sorted_wf if e[1] > 50 and e[0] not in stoplist]
sorted_wf = sorted_wf[25:]

n = int(round((len(sorted_wf) / 2) ** (1/3)))
print('The number of topics is:', n)


def filter_text(lst):
    return [wd for wd in lst if wd in sorted_wf]


filtered_txts = [filter_text(t) for t in texts]

with open('data/corpus/fids.pkl', 'wb') as pf:
    pickle.dump(fids, pf)

dictionary = corpora.Dictionary(filtered_txts)
dictionary.save('data/corpus/parla.dict')
corpus = [dictionary.doc2bow(text) for text in filtered_txts]
corpora.MmCorpus.serialize('data/corpus/parla.mm', corpus)
