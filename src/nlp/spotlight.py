import pandas as pd
import plac
import spotlight
from tqdm import tqdm


def extract_concepts(text):
    try:
        return spotlight.annotate("http://127.0.0.1:2229/rest/annotate", text, confidence=0.5, support=100)
    except Exception as e:
        return []


def annotate(texts):
    entities = [extract_concepts(text) if type(text) == str else [] for text in tqdm(texts)]
    return entities


def main(merged_tsv, entities_tsv):
    df = pd.read_csv(merged_tsv, sep="\t").set_index("Hash")
    df["Concepts"] = annotate(df.Text.values)
    df[["Concepts"]].to_csv(entities_tsv)


if __name__ == '__main__':
    plac.call(main)
