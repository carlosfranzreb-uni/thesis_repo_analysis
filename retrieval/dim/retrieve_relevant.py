""" Retrieve the IDs of theses or publications written in english. These are
the document types that are relevant for my work. Which types are included
in the groups 'thesis' and 'publication' can be seen in 
analysis/oai_dc/types/clustered_types.json """


from xml.etree import ElementTree as ET
import json
import os
import langdetect


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'
types = json.load(open('../../analysis/oai_dc/types/clustered_types.json'))
for t in types:
  for i in range(len(types[t])):
    types[t][i] = types[t][i].lower().replace(' ', '').replace('doc-type:', '')


def retrieve_relevant_ids(folder, dump):
  """ Retrieve the IDs of the relevant documents. """
  docs = list()
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
      correct_lang, correct_type = False, False
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'language':
          correct_lang = f.text == 'en' or f.text == 'eng'
        elif f.attrib['element'] == 'type':
          text = f.text.lower().replace(' ', '').replace('doc-type:', '')
          if text not in sum(types.values(), []) and 'version' not in text:
            print(text)
            import sys; sys.exit(0)
          correct_type = text in types['thesis'] + types['publication']
        if correct_lang and correct_type:
          docs.append(id)
          break
  json.dump(docs, open(dump, 'w'))


def retrieve_relevant(relevant_ids, folder, dump):
  """ Given the IDs of the relevant documents, retrieve their respective
  metadata. Keep only the english metadata and store them in JSON format. 
  Interesting metadata: title, authors, date, subjects, abstract, type, 
  access rights, publisher, b"""
  data = list()
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
      if id in relevant_ids:
        metadata = record.find(f'{oai}metadata').find(f'{dim}dim')
        data.append({
          'id': id,
          'title': get_title(metadata),
          'date': get_date(metadata),
          # 'authors': get_authors(metadata),
          # 'subjects': get_subjects(metadata),
          # 'abstract': get_abstract(metadata),
          # 'rights': get_rights(metadata),
          # 'publisher': get_publisher(metadata),
          # 'collection': get_collection(metadata)
        })
  json.dump(data, open(dump, 'w'))  


def get_title(metadata):
  """ If you find an english title (not a subtitle), return it. If not,
  try to detect the english title out of the options. If not possible, 
  return the shortest title. """
  titles = []
  for f in metadata.findall(f'{dim}field'):
    if f.attrib['element'] == 'title':
      if 'qualifier' in f.attrib and f.attrib['qualifier'] == 'subtitle':
        continue
      if 'lang' in f.attrib:
        if f.attrib['lang'] in ('en', 'eng'):
          return f.text
      else:
        titles.append(f.text)
  if len(titles) == 0:
    return None
  elif len(titles) == 1:
    return titles[0]
  else:
    for title in titles:
      try:
        if langdetect.detect(title) == 'en':
          return title
      except langdetect.lang_detect_exception.LangDetectException:
        continue
  return min(titles, key=len)


def get_date(metadata):
  """ Look for the issue date. I have checked that there is such a date
  in every document. """
  for f in metadata.findall(f'{dim}field'):
    if f.attrib['element'] == 'date':
      if 'qualifier' in f.attrib and f.attrib['qualifier'] == 'issued':
        return f.text
  print("No issue date")
  import sys; sys.exit(0)

if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    retrieve_relevant(
      json.load(open(f'../../data/json/dim/{repo}/relevant_ids.json')),
      f'../../data/xml/dim/{repo}',
      f'dump_{repo}.json'
    )
