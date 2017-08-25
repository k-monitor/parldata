import gensim
import pyLDAvis.gensim

dictionary = gensim.corpora.Dictionary.load('data/corpus/parla.dict')
corpus = gensim.corpora.MmCorpus('data/corpus/parla.mm')
lda = gensim.models.ldamodel.LdaModel.load('data/corpus/parla2.model')

t = pyLDAvis.gensim.prepare(lda, corpus, dictionary)
#pyLDAvis.show(t)
pyLDAvis.save_html(t, 'viz/parla_topics.html')
