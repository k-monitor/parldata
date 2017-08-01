import io
import logging
from zipfile import ZipFile

import pandas as pd
import plac
import regex as re
from tqdm import tqdm

PARTY_PATT = re.compile(r"[\p{L}\s\.\-]+\(([\p{L}\s]+)\)", re.UNICODE)

logging.basicConfig(level=logging.INFO)


def read_zipped_contents(fpath):
    data = {}
    with ZipFile(fpath) as zf:
        for name in tqdm(zf.namelist()):
            if name.endswith(".txt"):
                try:
                    with zf.open(name) as f:
                        full_text = "".join(io.TextIOWrapper(f).readlines()[2:])
                        speech = full_text[full_text.find(":") + 1:]
                        hash = name.split("/")[1].split(".")[0]
                        data[hash] = speech
                except Exception as e:
                    logging.error("Could not read {}".format(name))
    return pd.Series(data)


def extract_name_and_party(text):
    match = PARTY_PATT.match(text)
    if match is None:
        logging.warning("Could not match {}".format(repr(text)))
        return text, None
    else:
        party = match.group(1).strip()
        name = text[:match.start(1) - 1].strip()
        return name, party


def extract_speaker_id(text):
    if text.startswith("p_azon="):
        return text[7:].strip()
    else:
        logging.warning("Could not parse {}".format(repr(text)))
        return None


def read_metadata(tabular_metadata):
    meta_df = pd.read_csv(tabular_metadata, sep="\t")
    # FIXME: What the hell is the second row?
    meta_df.columns = ["Date", "Unk1", "NameAndParty", "RawSpeakerId", "SpeechType", "SpeakerType", "URL", "Hash"]
    meta_df["Name"], meta_df["Party"] = zip(*map(extract_name_and_party, meta_df.NameAndParty.values))
    meta_df["SpeakerId"] = meta_df.RawSpeakerId.apply(extract_speaker_id)
    meta_df.drop(["Unk1", "RawSpeakerId", "NameAndParty"], axis=1, inplace=True)
    meta_df.set_index(["Hash"], inplace=True)
    return meta_df


def main(tabular_metadata, zipped_content, out_file):
    data = read_metadata(tabular_metadata)
    texts = read_zipped_contents(zipped_content)
    data["Text"] = texts
    data.to_csv(out_file, sep="\t")


if __name__ == '__main__':
    plac.call(main)
