""" Retrieve the types of the relevant documents. """


import json
from xml.etree import ElementTree as ET
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'


def get_types(folder, relevant_ids, dump):
  """ Returns a dict with the ids as keys and the types as values. """
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
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'type':
          text = f.text.lower().replace(' ', '').replace('doc-type:', '')
          if 'version' not in text:
            docs[id] = text
            break
  json.dump(docs, open(dump, 'w'))


if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    get_types(
      f'../../data/xml/dim/{repo}',
      json.load(open(f'../../data/json/dim/{repo}/relevant_ids.json')),
      f'../../data/json/dim/{repo}/relevant_types.json'
    )
    