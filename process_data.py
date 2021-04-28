""" Process the XML files retrieved with the Harvester class (harvester.py).
- Extract the relevant fields: title, date, authors, contributors, subjects,
publication type and language.
- If an item has two titles, keep only the english one. """


import os
import xml.etree.ElementTree as ET
import json
import langdetect

oai = '{http://www.openarchives.org/OAI/2.0/}'
oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
dc = '{http://purl.org/dc/elements/1.1/}'


class Processor:
  def __init__(self, folder, dump_file):
    """ Folder contains the XML files. """
    self.folder = folder
    self.data = list()
    self.fields = [
      f'{dc}title',
      f'{dc}creator',
      f'{dc}contributor',
      f'{dc}date',
      f'{dc}subject',
      f'{dc}type',
      f'{dc}language',
    ]
    self.types = json.load(open('analysis/types/clustered_types.json'))
    self.dump_file = dump_file
  
  def process(self):
    self.retrieve_objects()
    self.dump()

  def retrieve_objects(self):
    """ Extract the objects from the XML files that reside
    in the given folder. """
    for f in os.listdir(self.folder):
      print(f)
      root = ET.parse(f'{self.folder}/{f}').getroot()
      records = root.find(f'{oai}ListRecords')
      for record in records:
        header = record.find(f'{oai}header')
        if record.tag == f'{oai}resumptionToken':
          continue
        elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
          continue
        else:
          id = header.find(f'{oai}identifier').text
          metadata = record.find(f'{oai}metadata').find(f'{oai_dc}dc')
          self.extract_fields(id, metadata)
    
  def extract_fields(self, id, metadata):
    """ Given metadata, extract the relevant fields written in english,
    avoid duplicates. If an item has multiple english descriptions,
    keep only the longest one. """
    object = {"id": id}
    for field in self.fields:
      data = []
      for fi in metadata.findall(field):
        if fi.text is None or len(fi.text) == 0:
          continue
        elif fi.text not in data:
          data.append(fi.text) 
      if len(data) == 0:
        data = None
      elif 'type' in field:
        data = self.prune_types(data)
      elif 'language' in field and len(data) > 1:
        data = min(data, key=len)
      elif 'title' in field:
        if len(data) > 1:
          english_data = []
          for t in data:
            try:
              if langdetect.detect(t) == 'en':
                english_data.append(t)
            except langdetect.lang_detect_exception.LangDetectException:
              english_data.append(t)
          if len(english_data) == 0:
            data = data[0]
          else:
            data = max(english_data, key=len)
        else:
          data = data[0]
      elif len(data) == 1:
        data = data[0]
      object[field.replace(dc, '')] = data
    self.data.append(object)

  def dump(self):
    json.dump(self.data, open(self.dump_file, 'w'))

  def prune_types(self, data):
    """Extract the correct types. """
    for d in data:
      d = d.lower().replace('doc-type:', '').replace(' ', '')
      if 'version' in data:
        continue
      for category in self.types:
        for t in self.types[category]:
          if d == t.lower().replace(' ', ''):
            return category


if __name__ == "__main__":
  folders = ['depositonce', 'edoc', 'refubium']
  for folder in folders:
    processor = Processor(f'data/xml/{folder}', f'data/processed/{folder}.json')
    processor.process()
        