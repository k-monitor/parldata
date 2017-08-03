from polyglot import text as nlp
import pandas as pd
import plac
from tqdm import tqdm

def parse_entity(entity):
    return entity.tag, " ".join(list(entity))


def extract_entities(texts):
    entities = [[parse_entity(entity) for entity in nlp.Text(text, "hu").entities] \
                if type(text) == str else [] for text in tqdm(texts)]
    return entities


def main(merged_tsv, entities_pkl):
    df = pd.read_csv(merged_tsv, sep="\t").set_index("Hash")
    df["Entities"] = extract_entities(df.Text.values)
    df[["Entities"]].to_pickle(entities_pkl)


if __name__ == '__main__':
    plac.call(main)
