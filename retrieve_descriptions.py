"""Preprocess the descriptions of the items by:
  1. deleting german texts with langdetect,
  2. removing stop words with NLTK,
  3. removing punctuation signs,
  4. removing numbers and
  5. performing lemmatization on the remaining words. """

import os
import xml.etree.ElementTree as ET
import json
import nltk
from string import punctuation
import langdetect

oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


def retrieve_descriptions(folder):
  """ Extract the descriptions of each publication and store them as a
  list. """
  descriptions = dict()
  for f in os.listdir(folder):
    root = ET.parse(f'{folder}/{f}').getroot()
    records = root.find(f'{oai}ListRecords')
    for record in records:
      header = record.find(f'{oai}header')
      if record.tag == f'{oai}resumptionToken':
        continue
      elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
        continue
      try:
        id = header.find(f'{oai}identifier').text
        descriptions[id] = list()
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        for description in metadata.findall(f'{dc}description'):
          descriptions[id].append(description.text)
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(descriptions, open('data/json/refubium/descriptions.json', 'w'))


def preprocess_file(f, lemmatizer):
  """Preprocess the list of texts contained in file f. Remove 
  german texts. """
  processed = dict()
  texts = json.load(open(f))
  for id in texts:
    processed[id] = list()
    for text in texts[id]:
      if type(text) is not str:
        continue
      try:
        if langdetect.detect(text) == 'en':
          processed[id].append(preprocess(text, lemmatizer))
      except langdetect.lang_detect_exception.LangDetectException:
        print(text)
        continue
  json.dump(processed, open('data/json/processed_descriptions_v2.json', 'w'))


def preprocess(text, lemmatizer):
  """ Tokenize the text; remove stopwords and punctuation. """
  # data = json.load(open(files[0]))
  # for f in files[1:]:
  #   data += json.load(open(f))
  stopwords = nltk.corpus.stopwords.words('english')
  text = "".join([char for char in text.lower() if char not in punctuation])
  return [lemmatizer.lemmatize(w) for w in nltk.word_tokenize(text) 
      if w not in stopwords and not w.isdigit()]


if __name__ == "__main__":
  wnl = nltk.stem.WordNetLemmatizer()
  # retrieve_descriptions('data/xml/refubium')
  preprocess_file('data/json/depositonce/descriptions.json', wnl)
