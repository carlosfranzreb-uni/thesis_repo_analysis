""" Retrieve the IDs of theses or publications written in english. These are
the document types that are relevant for my work. Which types are included
in the groups 'thesis' and 'publication' can be seen in 
analysis/oai_dc/types/clustered_types.json """


from xml.etree import ElementTree as ET
import json
import os


oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'
dim = '{http://www.dspace.org/xmlns/dspace/dim}'
types = json.load(open('../../analysis/oai_dc/types/clustered_types.json'))
for t in types:
  for i in range(len(types[t])):
    types[t][i] = types[t][i].lower().replace(' ', '').replace('doc-type:', '')


def retrieve_relevant(folder, dump):
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


if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    retrieve_relevant(
      f'../../data/xml/dim/{repo}',
      f'../../data/json/dim/{repo}/relevant.json'
    )
