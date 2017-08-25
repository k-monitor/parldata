import gensim
import codecs
from shutil import copy2
from os import listdir, mkdir
from os.path import join, isfile

in_path = 'data/all_raw_text'
out_path = 'data/docs_by_topic'

for i in range(0, 27):
    mkdir(join(out_path, str(i)))

dictionary = gensim.corpora.Dictionary.load('data/corpus/parla.dict')
corpus = gensim.corpora.MmCorpus('data/corpus/parla.mm')
lda = gensim.models.ldamodel.LdaModel.load('data/corpus/parla2.model')
all_topics = lda.get_document_topics(corpus, per_word_topics=True)


docid_docname = {}
f1 = codecs.open('data/corpus/doc_ids.tsv', 'r', 'utf-8')

for l in f1:
    docid, docname = l.strip().split('\t')
    docname = docname.replace('.txt', '')
    docid_docname[docid] = docname
f1.close()
i = 0
for doc_topics, word_topics, phi_values in all_topics:
    docid = str(i)
    if docid in docid_docname.keys():
        dname = docid_docname[docid] + '.txt'
        doc_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)
        top_topics = [e for e in doc_topics if e[1] > 0.81]
        if len(top_topics) > 0:
            top_topic = str(top_topics[0][0])
            try:
                copy2(join(in_path, dname), join(out_path, top_topic, dname))
            except Exception as e:
                print(e)
                continue
    i += 1