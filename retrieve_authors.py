"""Retrieve the authors of the publications and create a dict with authors
as keys and their publications as a list of values. """

import os
import xml.etree.ElementTree as ET
import json


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


def retrieve_authors(folder):
  """ Extract the creators of each publication and store them as a
  list. """
  creators = dict()
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
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        for creator in metadata.findall(f'{dc}creator'):
          if creator.text not in creators:
            creators[creator.text] = list()
          creators[creator.text].append(id)
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(creators, open('data/json/depositonce/authors.json', 'w'))


def retrieve_authors_reversed(folder):
  """ Same as retrieve_authors(), but now the publications are the keys
  and the authors the values. """
  publications = dict()
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
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        publications[id] = [c.text for c in metadata.findall(f'{dc}creator')]
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(publications, open('data/json/refubium/authors_reversed.json', 'w'))


if __name__ == "__main__":
  retrieve_authors_reversed('data/xml/refubium')
