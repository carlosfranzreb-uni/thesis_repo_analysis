""" Process the XML files retrieved with the Harvester class (harvester.py).
- Extract the relevant fields: title, description, date, authors,
contributors, subjects, publication type and language.
- Discard anything written in english.
- If an item has multiple english descriptions, keep only the longest one.
- remove uninformative descriptions.
- process descriptions with the functions of retrieve_descriptions.py """


import os
from retrieve_descriptions import preprocess
import xml.etree.ElementTree as ET
import json
from nltk.stem import WordNetLemmatizer
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
      f'{dc}creator',
      f'{dc}contributor',
      f'{dc}date',
      f'{dc}subject',
      f'{dc}type',
      f'{dc}description',
      f'{dc}subject',
    ]
    self.wnl = WordNetLemmatizer()
  
  def process(self):
    self.retrieve_objects()
    self.dump(dump_file)

  def retrieve_objects(self):
    """ Extract the objects from the XML files that reside
    in the given folder. """
    for f in os.listdir(self.folder):
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
        if len(fi.text) == 0:
          continue
        try:
          if langdetect.detect(fi.text) == 'en' and fi.text not in data:
            data.append(fi.text)
        except langdetect.lang_detect_exception.LangDetectException:
          if fi.text not in data:
            data.append(fi.text)
      if len(data) == 0:
        data = None
      elif 'description' in field:
        data = preprocess(max(data, key=len), self.wnl)
      elif len(data) == 1:
        data = data[0]
      object[field.replace(dc, '')] = data
    self.data.append(object)

  def dump(self, dump_file):
    json.dump(self.data, open(dump_file, 'w'))


if __name__ == "__main__":
  folder = 'data/xml/depositonce'
  dump_file = 'data/processed/depositonce.json'
  processor = Processor(folder, dump_file)
  processor.process()
        