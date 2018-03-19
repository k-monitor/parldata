import codecs
import logging
from datetime import datetime
from gensim import corpora
from gensim.models import LdaModel

# logger, timer
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
print('Start')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# load corpus
id2word = corpora.Dictionary.load('data/corpus/parla.dict')
corpus = corpora.MmCorpus('data/corpus/parla.mm')

# train model
n = 24
lda = LdaModel(corpus, id2word=id2word, num_topics=n, alpha='auto',
               eta='auto', iterations=100, passes=1, update_every=1,
               chunksize=50000)
lda.save('data/corpus/parla.model')
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
