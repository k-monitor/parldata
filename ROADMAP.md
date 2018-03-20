This is the Parliamentary Debates Open's roadmap. The aim of the project is to make parliamentary speeches open and accessible covering Hungarian parliamentary debates since 1990. For further details see the [README of the project.](https://github.com/k-monitor/parldata/blob/master/README.md)

**Tasks**

- New crawler to download data from parlament.hu – done
- Freshen the corpus – done
- Process the text, handle old characters
- Do the topicmodelling
- Prepare corpus to upload to Elasticsearch
- Prepare frontend
  - search for keyword
  - faceted search to filter data (speaker, date, party)
  - histogram of the distribution of the results of search
  - show result texts for the search (few words before, search term, few words after to reveal the context), using pagination or scroll.
