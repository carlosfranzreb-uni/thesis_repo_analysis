"""Retrieve any field of the publications and create a dict with them
as keys and their publications as a list of values. 

extract_info() is relevant for contributors, where there are contact e-mails
and single letters. """

import os
import xml.etree.ElementTree as ET
import json


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


def retrieve_fields(dump):
  """ Extract the fields of each publication and store them as a
  list. """
  types = dict()
  data_folder = '../../data/xml'
  for folder in os.listdir(data_folder):
    types[folder] = list()
    for f in os.listdir(f'{data_folder}/{folder}'):
      root = ET.parse(f'{data_folder}/{folder}/{f}').getroot()
      records = root.find(f'{oai}ListRecords')
      for record in records:
        header = record.find(f'{oai}header')
        if record.tag == f'{oai}resumptionToken':
          continue
        elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
          continue
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        for fi in metadata.findall(f'{dc}type'):
          if fi.text not in types[folder]:
            types[folder].append(fi.text)
    json.dump(types, open(dump, 'w'))


if __name__ == "__main__":
  dump = 'types.json'
  retrieve_fields(dump)
