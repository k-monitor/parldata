import hunlp
import pandas as pd
import plac
from tqdm import tqdm


def extract_entities(texts):
    nlp = hunlp.HuNlp()
    entities = [list(nlp(text).entities) if type(text) == str else [] for text in tqdm(texts)]
    return entities


def main(merged_tsv, entities_tsv):
    df = pd.read_csv(merged_tsv, sep="\t").set_index("Hash")
    df["Entities"] = extract_entities(df.Text.values)
    df[["Entities"]].to_csv(entities_tsv)


if __name__ == '__main__':
    plac.call(main)
