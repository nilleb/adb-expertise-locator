# README

adb-expertise-locator is an orchestrator that downloads all the public reports from adb.org and enriches them using nltk+Standford NER.

Then it builds a document for every author recognized in these documents, and indexes this to elasticsearch.

It provides a sample CLI interface to query the index.

## indexes

### recommendation

- authors
- title
- content

### linkedin_profile

- first
- last
- current position
- previous positions

### people

- first
- last
- current position
- previous positions
- title of the works she's author
- content of the works she's author
- roles she has played (how many times)

## indexing

### sources - for the PDFs

- [google](https://github.com/MarioVilas/googlesearch)
- [adb](https://www.adb.org/projects/documents)
- [adb pdf documents copy](https://drive.google.com/drive/folders/1IL4YCK8-JqIf63KN4Wk7qb5nPCkDcyGD?usp=sharing)

### workflow

1. crawl the site
2. download the PDFs
3. extract text from the PDFs
   1. author pages
   2. whole document text
4. apply NER to the text
5. extract athors
6. extract people extracted from the authors page with NER
7. extract pepple recognized by NER in the whole document corpus
8. per every person at 5, 6, 7, build
   1. the list of documents where this person appears
   2. the list of keywords associated to the documents
   3. the list of documents where the person appears
   4. the list of all the texts where the person appears
   5. (wannabe) the list of titles of those documents
9. index all the author documents to elasticsearch

the script `index.py` is supposed to complete this workflow.

## search

launch `python query.py "query string"`

## hints for the future

- exclude from the texts the authors section
- should be middle names considered? (edwin e david is the same author than edwin david)?
- consider grouped keywords (eg. recognize "board approved", "terms and conditions")
- \n\n should be considered as a strong line separator and we should not cross it (eg. Sustainable \n\nS. Lee)

## todo

- unicode support (hugh madden keywords seem to include non unicode chars?)
