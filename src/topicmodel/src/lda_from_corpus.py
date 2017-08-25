import codecs
import logging
from datetime import datetime
from gensim import corpora
from gensim.models import LdaModel

# uncomment logging, if you don't like it
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
print('Start')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# open corpus
id2word = corpora.Dictionary.load('data/corpus/parla.dict')
corpus = corpora.MmCorpus('data/corpus/parla.mm')

stopwords = []
# stoplist.txt
f = codecs.open('data/corpus/stoplist.txt', 'r', 'utf-8')
for l in f:
    stopwords.append(l.strip())

# train model
n = 27
lda = LdaModel(corpus, id2word=id2word, num_topics=n, alpha='auto',
               eta='auto', iterations=300, passes=1, update_every=1,
               chunksize=10000)
lda.save('data/corpus/parla.model')
print('Done')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
