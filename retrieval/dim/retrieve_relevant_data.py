""" Retrieve the abstracts of the relevant documents. """


import json
from xml.etree import ElementTree as ET
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'


def get_data(folder, relevant_ids, dump):
  """ Returns a dict with the ids as keys and the title and abstract as values. """
  docs = dict()    
  for f in os.listdir(folder):
    root = ET.parse(f'{folder}/{f}').getroot()
    records = root.find(f'{oai}ListRecords')
    for record in records:
      header = record.find(f'{oai}header')
      if record.tag == f'{oai}resumptionToken':
        continue
      elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
        continue
      id = header.find(f'{oai}identifier').text
      if id not in relevant_ids:
        continue
      docs[id] = {'title': None, 'abstract': None}
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if 'qualifier' in f.attrib and f.attrib['qualifier'] == 'abstract':
          if 'lang' in f.attrib and f.attrib['lang'] in ('en', 'eng'):
            docs[id]['abstract'] = f.text
            break
        if 'element' in f.attrib and f.attrib['element'] == 'title':
          if 'lang' in f.attrib:
            if f.attrib['lang'] in ('en', 'eng'):
              docs[id]['title'] = f.text
              break
          else:
            docs[id]['title'] = f.text
            break
  json.dump(docs, open(dump, 'w'))


def merge_data():
  """ Merge the data extracted for each repository. """
  res = {}
  for repo in ('depositonce', 'edoc', 'refubium'):
    data = json.load(open(f'../../data/json/dim/{repo}/relevant_data.json'))
    res.update(data)
  json.dump(res, open('../../data/json/dim/all/relevant_data.json', 'w'))


if __name__ == "__main__":
  # for repo in ('depositonce', 'edoc', 'refubium'):
  #   get_data(
  #     f'../../data/xml/dim/{repo}',
  #     json.load(open(f'../../data/json/dim/{repo}/relevant_ids.json')),
  #     f'../../data/json/dim/{repo}/relevant_data.json'
  #   )
  merge_data()
    