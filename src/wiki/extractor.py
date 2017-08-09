from __future__ import unicode_literals

import json
import re
import zipfile

import plac
import spacy
from textacy.corpora.wiki_reader import WikiReader, strip_markup
from tqdm import tqdm

SENT_ENDS = [u".", u"!", u"?"]
TABLE_PREFIX = re.compile(u"\s*(\{\))|(\|)|(\|\})")
TAG = re.compile(u"<[^<>]+>")


def tokenize_sentence_split(text, nlp):
    tokenizer = nlp.tokenizer
    for line in text.split("\n"):
        tok_acc = []
        for tok in tokenizer(line):
            tok_acc.append(tok.text)
            if tok.text in SENT_ENDS:
                yield " ".join(tok_acc)
                tok_acc = []
        if tok_acc:
            yield " ".join(tok_acc)


def pre_filter(content):
    return "\n".join([line for line in content.split(u"\n") if not TABLE_PREFIX.match(line)])


def extract_text(content, nlp):
    sentences = []
    # content = strip_markup(pre_filter(content))
    content = strip_markup(content)
    lines = content.split("\n")
    for line in lines:
        for sent in tokenize_sentence_split(line, nlp):
            sentences.append(sent)
    return u"\n".join(sentences)


def main(dump_path, out_path):
    reader = WikiReader(dump_path)
    nlp = spacy.load("hu", parser=None, tagger=None)

    with zipfile.ZipFile(out_path, "w") as zf:
        for id, title, content in tqdm(reader):
            if ":" in title or len(content.strip()) == 0:
                continue
            text_content = extract_text(content, nlp)
            js = json.dumps({"title": title, "content": text_content}, indent=4)
            zf.writestr("{}.json".format(id), js)
        zf.close()

if __name__ == "__main__":
    plac.call(main)
