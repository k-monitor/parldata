import codecs
import gensim
import pickle

dictionary = gensim.corpora.Dictionary.load('data/corpus/parla.dict')
corpus = gensim.corpora.MmCorpus('data/corpus/parla.mm')
lda = gensim.models.ldamodel.LdaModel.load('data/corpus/parla.model')

#topic -> words
of1 = codecs.open('data/corpus/topic_words.tsv', 'w', 'utf-8')

for i in range(0, 24):
    rep = lda.show_topic(i, 40) # get the first 40 words
    wds = [e[0] for e in rep]
    wds = ' '.join(wds)
    o = str(i).zfill(2) + '\t' + wds + '\n'
    of1.write(o)
of1.close()

fids = pickle.load( open('data/corpus/fids.pkl', 'rb'))

# doc -> topics
of2 = codecs.open('data/corpus/docs_topic.tsv', 'w', 'utf-8')
all_topics = lda.get_document_topics(corpus, per_word_topics=True)
i = 0
for doc_topics, word_topics, phi_values in all_topics:
    dname = fids[i]
    doc_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)
    doc_topics = [e[0] for e in doc_topics][:3]
    doc_topics = [str(e) for e in doc_topics]
    doc_topics = '|'.join(doc_topics)
    o = dname + '\t' + str(doc_topics) + '\n'
    of2.write(o)
    i += 1
of2.close()
