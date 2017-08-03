import pandas as pd
import plac
import spotlight
from tqdm import tqdm
import logging

def extract_concepts(text):
    try:
        return spotlight.annotate("http://127.0.0.1:2229/rest/annotate", text, confidence=0.5, support=100)
    except Exception as e:
        #logging.warn(e)
        #logging.warn("Could not annotate '{}'".format(text[:50]))
        return []


def annotate(texts):
    entities = [extract_concepts(text) if type(text) == str else [] for text in tqdm(texts)]
    return entities


def main(merged_tsv, entities_pkl):
    df = pd.read_csv(merged_tsv, sep="\t").set_index("Hash")
    df["Concepts"] = annotate(df.Text.values)
    df[["Concepts"]].to_pickle(entities_pkl)


if __name__ == '__main__':
    plac.call(main)
