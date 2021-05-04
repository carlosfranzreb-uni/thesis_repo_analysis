""" Retrieve subjects by language for each doc and store them as a dict
and also the other way around (reversed: subjects -> docs). Also, identify
DDC subjects. 

The subjects also have a type, so each subject in the dicts is really a
tuple (subject, type). """


from xml.etree import ElementTree as ET
import json
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'
langs = {'eng': 'en', 'ger': 'de'}


def retrieve_subjects(folder, relevant, dump):
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
      if id not in relevant:
        continue
      publications[id] = []
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'subject':
          if 'qualifier' not in f.attrib:
            f.attrib['qualifier'] = 'unknown'
          elif f.attrib['qualifier'] == 'ddc':
            number = extract_number(f.text)
            if number is not None:
              f.text = number
          if 'lang' not in f.attrib:
            f.attrib['lang'] = 'unknown'
          if f.attrib['lang'] in ('en', 'eng'):
            publications[id].append((f.text, f.attrib['qualifier']))
  json.dump(publications, open(dump, 'w'))


def retrieve_subjects_reversed(folder, relevant, dump):
  subjects = []
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
      if id not in relevant:
        continue
      metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'subject':
          if 'qualifier' not in f.attrib:
            f.attrib['qualifier'] = 'unknown'
          elif f.attrib['qualifier'] == 'ddc':
            number = extract_number(f.text)
            if number is not None:
              f.text = number
          if 'lang' not in f.attrib:
            f.attrib['lang'] = 'unknown'
          if f.attrib['lang'] in ('en', 'eng', 'unknown'):
            added = False
            for s in subjects:
              if s['type'] == f.attrib['qualifier'] and s['subject'] == f.text:
                s['values'].append(id)
                added = True
                break
            if not added:
              subjects.append({
                'type': f.attrib['qualifier'],
                'subject': f.text,
                'values': [id]
              })
  json.dump(subjects, open(dump, 'w'))


def is_ddc(n):
  """ True if the given number (string) complies with the DDC format. """
  return '.' in n and len(n.split('.')[0]) == 3 or \
      '.' not in n and len(n) == 3


def extract_number(text):
  """ Extract the number from the text, including the decimal numbers.
  If there are more than one number, retrieve the ones that follow
  the DDC format ddd.d*. """
  n = ''
  for char in text:
    if char.isdigit() or char == '.':
      n += char
    elif len(n) > 0:
      if is_ddc(n):
        return n
      n = ''
  if len(n) > 0 and is_ddc(n):
    return n
  return None


if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    relevant_ids = json.load(open(f'../../data/json/dim/{repo}/relevant_ids.json'))
    retrieve_subjects(
      f'../../data/xml/dim/{repo}',
      relevant_ids,
      f'../../data/json/dim/{repo}/relevant_subjects.json'
    )
    retrieve_subjects_reversed(
      f'../../data/xml/dim/{repo}',
      relevant_ids,
      f'../../data/json/dim/{repo}/relevant_subjects_reversed.json'
    )