import codecs
import itertools
from os import listdir
from datetime import datetime
from gensim import corpora
from gensim.models import LdaModel
from os.path import join, isfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
# TODO:
# - simplify

print('Starting')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
in_path = 'data/lda_corpus'
in_files = [f for f in listdir(in_path) if isfile(join(in_path, f))]
in_files = sorted(in_files)

print('Files have been read') # 0.2sec
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Run only once, it takes decades to write out everything
# iterates over 322.175 docs
# of = codecs.open('data/corpus/doc_ids.tsv', 'w', 'utf-8')
#
#
# def write_info(f):
#     i = str(in_files.index(f))
#     o = i + '\t' + f + '\n'
#     of.write(o)
#
# with ThreadPoolExecutor(max_workers=40) as executor:
#     executor.map(write_info, in_files)
#
# print('Docids are ready') # 1:34 mins
# print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

f1 = codecs.open('data/corpus/stoplist.txt', 'r', 'utf-8')
stoplist = []
for l in f1:
    stoplist.append(l.strip())

# this part of the code is dirty! 
texts = []
for i in range(0, len(in_files)):
    texts.append([])


def read_text(f):
    t = (codecs.open(join(in_path, f), 'r', 'utf-8').read().split())
    t = [w for w in t if w not in stoplist]
    i = in_files.index(f)
    texts[i] = t

with ThreadPoolExecutor(max_workers=40) as executor:
    # on a laptop, or with older processors with 2 physical cores, use 10-20 workers
    executor.map(read_text, in_files)

print('Raw corpus is ready') # 1:23
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


f2 = codecs.open('data/meta/content_words.csv', 'r', 'utf-8')
frequency = defaultdict(int)
for l in f2:
    wd, freq = l.strip().split('\t')
    frequency[wd] = int(freq)
print('Word frequency is ready')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


merged = set(list(itertools.chain(*texts)))
n = int(round((len(merged) / 2) ** (1/3)))
print('The number of to pics is:', n)
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

dictionary = corpora.Dictionary(texts)
dictionary.save('data/corpus/parla.dict')
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('data/corpus/parla.mm', corpus)

print('Done')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
