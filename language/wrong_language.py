""" For the documents present in the file created by 'detect_language.py', look if
they have two titles. I have seen that a couple of them have the language tags
swapped: it says 'en' where it should be 'de' and the other way around. """


import json
from xml.etree import ElementTree as ET
import os

from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'


def get_record(id):
  """ Return the record of the document with the given ID. """
  folder = f'data/xml/dim/{get_repo(id)}'
  for f in os.listdir(folder):
    root = ET.parse(f'{folder}/{f}').getroot()
    records = root.find(f'{oai}ListRecords')
    for record in records:
      header = record.find(f'{oai}header')
      if record.tag == f'{oai}resumptionToken':
        continue
      elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
        continue
      if header.find(f'{oai}identifier').text == id:
        return record


def get_fields(id, tag, value):
  """ Get the field with the given element and qualifier. """
  fields = []
  record = get_record(id)
  metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
  for f in metadata.findall(f'{dim}field'):
    if tag in f.attrib and f.attrib[tag] == value:
      fields.append(f)
  return fields


def get_repo(doc_id):
  """ Return the repository to which the given identifier belongs. """
  if 'depositonce' in doc_id:
    return 'depositonce'
  elif 'edoc' in doc_id:
    return 'edoc'
  else:
    return 'refubium'


def get_texts(tag, value):
  """ Looking at the docs in 'foreign_languages.json', how many of them
  have more than one value? Value can be either title or abstract. """
  res = {}
  foreign = json.load(open('data/json/dim/all/foreign_languages.json'))
  for doc, _, _ in foreign[value]:
    fields = get_fields(doc, tag, value)
    if len(fields) > 0:
      res[doc] = [{'text': f.text, 'attribs': f.attrib} for f in fields]
  json.dump(res, open(f'data/json/dim/all/foreign_{value}s.json', 'w'))


def get_english_texts(value):
  """ Using the texts retrieved by get_texts(), return those that are in
  English by using langdetect."""
  data = json.load(open(f'data/json/dim/all/foreign_{value}s.json'))
  res = {}
  for id, titles in data.items():
    best_prob = -1  # probability that a text is in English
    best_text = None
    for obj in titles:
      text, _ = obj.values()
      out = detect_language(text)
      if out is not None and out[0] == 'en' and out[1] > best_prob:
        best_prob = out[1]
        best_text = text
      res[id] = best_text
  json.dump(res, open(f'data/json/dim/all/best_{value}s.json', 'w'))


def detect_language(text, n=10):
  """ Detect the language of a text by running the 'detect_langs' function
  on the text 'n' times. Return the language and the avg. prob. If the language
  changes from one iteration to another, return None. """
  probs = []
  language = None
  for _ in range(n):
    try:
      langs = detect_langs(text)
    except LangDetectException:
      print(text)
      return None
    probs.append(langs[0].prob)
    if language is None:
      language = langs[0].lang
    elif language != langs[0].lang:
        return None
  return (language, sum(probs)/len(probs))


if __name__ == '__main__':
  get_texts('qualifier', 'abstract')
  get_english_texts('abstract')
