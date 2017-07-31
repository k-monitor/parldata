#!/usr/bin/env bash

pip install https://github.com/oroszgy/hunlp/releases/download/0.2/hunlp-0.2.0.tar.gz

docker pull oroszgy/hunlp
docker pull dbpedia/spotlight-hungarian
