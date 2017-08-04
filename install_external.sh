#!/usr/bin/env bash

pip install https://github.com/oroszgy/hunlp/releases/download/0.2/hunlp-0.2.0.tar.gz

conda install -c conda-forge/label/broken icu
easy_install pyicu

pip install pycld2 morfessor
pip install https://github.com/aboSamoor/polyglot/archive/master.zip

polyglot download ner2.hu
polyglot download embeddings2.hu

docker pull oroszgy/hunlp
docker pull dbpedia/spotlight-hungarian
