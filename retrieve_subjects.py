""" retrieve_subjects() creates a dict that maps subjects (keys) to
publications (values). retrieve_subjects_reversed() does the same but
reversing the mapping order (publications are keys, subjects are values). """


import os
import xml.etree.ElementTree as ET
import json


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


def retrieve_subjects(folder):
  """ Extract the subjects of each publication and store them as a
  dictionary with the subjects as keys and the publications is is
  present in as values. """
  subjects = dict()
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
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        id = header.find(f'{oai}identifier').text
        for subject in metadata.findall(f'{dc}subject'):
          if subject.text not in subjects:
            subjects[subject.text] = list()
          subjects[subject.text].append(id)
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(subjects, open('data/json/subjects.json', 'w'))


def retrieve_subjects_reversed(folder):
  """ Extract the subjects of each publication and store them as a
  dictionary with the subjects as keys and the publications is is
  present in as values. """
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
        metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
        id = header.find(f'{oai}identifier').text
        publications[id] = list()
        for subject in metadata.findall(f'{dc}subject'):
          publications[id].append(subject.text)
      except AttributeError:
        print(f, id)
        import sys; sys.exit(0)
  json.dump(publications, open('data/json/publications.json', 'w'))


if __name__ == "__main__":
  retrieve_subjects_reversed('data/xml/depositonce')