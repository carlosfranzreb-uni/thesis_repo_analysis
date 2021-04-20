"""Retrieve any field of the publications and create a dict with them
as keys and their publications as a list of values. """

import os
import xml.etree.ElementTree as ET
import json


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


def retrieve_fields(folder, dump, field):
  """ Extract the fields of each publication and store them as a
  list. """
  fields = dict()
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
        for fi in metadata.findall(field):
          if fi.text not in fields:
            fields[fi.text] = list()
          fields[fi.text].append(id)
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(fields, open(dump, 'w'))


def retrieve_fields_reversed(folder, dump, field):
  """ Same as retrieve_fields(), but now the publications are the keys
  and the fields the values. """
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
        publications[id] = [c.text for c in metadata.findall(field)]
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(publications, open(dump, 'w'))


if __name__ == "__main__":
  dump = 'data/json/refubium/contributors.json'
  dump_r = 'data/json/refubium/contributors_reversed.json'
  field = f'{dc}contributor'
  retrieve_fields('data/xml/refubium', dump, field)
  retrieve_fields_reversed('data/xml/refubium', dump_r, field)
