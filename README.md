parldata_analysis
==============================

Scripts for analyzing the Hungarian parlament speech corpus.

Welcome to the Parliamentary Debates Open's github repo. We are a bunch of people working on making Hungarian parliamentary speeches open. We are happy to see you here.

"Do you recall when Viktor Orbán said this and that? How was that exactly?" – This is the typical use case this project wants to address. The tool we are developing aims to make parliamentary speeches open and accessible covering Hungarian parliamentary debates since 1990. The scraped speeches (using Scrapy) are processed using Natural Language Processing (using Spacy), Elasticsearch is used for search backend. The minimal viable product is a filterable dashboard for name, party, and date, returning the relevant speeches. Additional features will include topics (using Gensim), top lists, histograms and comparisons.

If you are interested in an analysis we have made earlier, check out [this blog post in English](http://k.blog.hu/2017/12/05/the_language_of_the_hungarian_parliament_1990) or [this site in Hungarian.](http://k-monitor.github.io/) If you want to have a look at the raw data we downloaded for the sake of this project from parlament.hu click [here.](http://opendata.hu/dataset/parldata)

Would you like to contribute? Please see the [CONTRIBUTING.md](https://github.com/k-monitor/parldata/blob/master/CONTRIBUTING.md) for more information.

The test version of the project is available [here.](https://k-monitor.github.io/parliamentary_debates_open/)
