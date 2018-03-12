parldata_analysis
==============================

Scripts for analyzing the Hungarian parlament speech corpus.

Welcome to the Parliamentary Debates Open's github repo. We are a bunch of people working on making Hungarian parliamentary speeches open. We are happy to see you here.

"Do you recall when Viktor Orbán said this and that? How was that exactly?" – This is the typical use case this project wants to address. The tool we are developing aims to make parliamentary speeches open and accessible covering Hungarian parliamentary debates since 1990. The scraped speeches (using Scrapy) are processed using Natural Language Processing (using Spacy), Elasticsearch is used for search backend. The minimal viable product is a filterable dashboard for name, party, and date, returning the relevant speeches. Additional features will include topics (using Gensim), top lists, histograms and comparisons.

If you are interested in an analysis we have made earlier, check out this blog post in English: http://k.blog.hu/2017/12/05/the_language_of_the_hungarian_parliament_1990 or this site in Hungarian: http://k-monitor.github.io/. If you want to have a look at the raw data we downloaded for the sake of this project from parlament.hu click here: http://opendata.hu/dataset/parldata.

Would you like to contribute? We are seeking for a developer, who helps us build a nice, easy-to-use frontend. Contact us here on github if you are interested.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
