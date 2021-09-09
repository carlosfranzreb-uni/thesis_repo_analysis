""" For the documents present in the file created by 'detect_language.py', look if
they have two titles. I have seen that a couple of them have the language tags
swapped: it says 'en' where it should be 'de' and the other way around. """


import json
from xml.etree import ElementTree as ET
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'


def get_record(id):
  """ Return the record of the document with the given ID. """
  folder = f'../data/xml/dim/{get_repo(id)}'
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


def get_fields(id, element=None, qualifier=None):
  """ Get the field with the given element and qualifier. """
  fields = []
  record = get_record(id)
  metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
  for f in metadata.findall(f'{dim}field'):
    if element is not None:
      if 'element' in f.attrib and f.attrib['element'] == element:
        if qualifier is not None:
          if 'qualifier' in f.attrib and f.attrib['qualifier'] == qualifier:
            fields.append(f)
        else:
          fields.append(f)
    elif qualifier is not None:
      if 'qualifier' in f.attrib and f.attrib['qualifier'] == qualifier:
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


def get_titles():
  """ Looking at the docs in 'foreign_languages.json', how many of them
  have more than one title? """
  cnt, total = 0, 0
  foreign = json.load(open('../data/json/dim/all/foreign_languages.json'))
  for doc, _, _ in foreign['title']:
    total += 1
    fields = get_fields(doc, element='title')
    if len(fields) > 0:
      print(f'{doc} has two titles: {[(f.text, f.attrib) for f in fields]}')
      cnt += 1
  print(cnt, total)


if __name__ == '__main__':
  get_titles()
