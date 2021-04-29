""" Retrieve subjects by language for each doc and store them as a dict
and also the other way around (reversed: subjects -> docs). Also, identify
DDC subjects. """


from xml.etree import ElementTree as ET
import json
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'
langs = {'eng': 'en', 'ger': 'de'}


def retrieve_subjects(folder, dump):
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
      id = header.find(f'{oai}identifier').text
      lang_dict = {'de': [], 'en': [], 'other': [], 'unknown': []}
      publications[id] = {
        'ddc': lang_dict.copy(),
        'dnb': lang_dict.copy(),
        'rvk': lang_dict.copy(),
        'classification': lang_dict.copy(),
        'other': lang_dict.copy(),
        'unknown': lang_dict.copy()
      }
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'subject':
          if 'lang' not in f.attrib:
            f.attrib['lang'] = 'unknown'
          elif f.attrib['lang'] in langs:
            f.attrib['lang'] = langs[f.attrib['lang']]
          if 'lang' not in lang_dict:
            f.attrib['lang'] = 'other'
          if 'qualifier' not in f.attrib:
            f.attrib['qualifier'] = 'unknown'
          publications[id][f.attrib['qualifier']][f.attrib['lang']].append(f.text)
  json.dump(publications, open(dump, 'w'))


def retrieve_subjects_reversed(folder, dump):
  subjects = {'de': {}, 'en': {}, 'other': {}, 'unknown': {}}
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
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'subject':
          if 'lang' not in f.attrib:
            f.attrib['lang'] = 'unknown'
          elif f.attrib['lang'] in langs:
            f.attrib['lang'] = langs[f.attrib['lang']]
          if 'lang' not in subjects:
            f.attrib['lang'] = 'other'
          if f not in subjects[f.attrib['lang']]:
            subjects[f.attrib['lang']][f.text] = list()
          subjects[f.attrib['lang']][f.text].append(id)
          
  json.dump(subjects, open(dump, 'w'))


if __name__ == "__main__":
  repo = 'depositonce'
  retrieve_subjects_reversed(
    f'../../data/xml/dim/{repo}',
    f'../../data/json/dim/{repo}/subjects_reversed.json'
  )