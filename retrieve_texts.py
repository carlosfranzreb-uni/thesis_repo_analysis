""" Retrieve the full texts of the publications that are either of type
'thesis' or of type 'publication'. 

The links to the resources can be found in the 'didl' metadata format for
edoc and depositonce and in 'xoai' for refubium. """


import requests as req
import xml.etree.ElementTree as ET
import os
from pathlib import Path
import json


class Harvester:
  def __init__(self, base_url, format, repo):
    self.base_url = base_url
    self.repo = repo
    self.folder = f'data/texts/{repo}'
    if not os.path.isdir(self.folder):
      raise OSError('Folder does not exist.')
    self.metadata_prefix = format
    self.oai = '{http://www.openarchives.org/OAI/2.0/}'
    self.oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
    self.dc = '{http://purl.org/dc/elements/1.1/}'
    self.didl = '{urn:mpeg:mpeg21:2002:02-DIDL-NS}'
    self.rejected_langs = set()
    self.data = json.load(open(f'data/processed/{repo}.json'))

  def request(self, verb, params=dict()):
    """ Executes a request with the given verbs and parameters. The parameters
    are given as a dict. """
    request = f'{self.base_url}?verb={verb}'
    for key, value in params.items():
      request += f'&{key}={value}'
    if 'resumptionToken' not in params:
      request += f'&metadataPrefix={self.metadata_prefix}'
    return req.get(request)

  def retrieve_all(self):
    """ Retrieve all publications. """
    done = False
    cnt = 1
    res = self.request('ListRecords')
    while not done:
      self.retrieve_texts(res.text)
      token = self.get_resumption_token(res.text)
      if token is None or len(token) == 0:
        done = True
      else:
        res = self.request('ListRecords', {'resumptionToken': token})
  
  def get_resumption_token(self, text):
    return ET.fromstring(text) \
      .find(f'{self.oai}ListRecords') \
      .find(f'{self.oai}resumptionToken') \
      .text
  
  def retrieve_texts(self, res):
    """ Retrieve the texts of the items in the page 'res'. """
    root = ET.fromstring(res)
    records = root.find(f'{self.oai}ListRecords')
    for record in records:
      try:
        id = record.find(f'{self.oai}header').find(f'{self.oai}identifier').text
        metadata = record.find(f'{self.oai}metadata').find(f'{self.didl}DIDL') \
          .find(f'{self.didl}Item')
        lang = metadata.findall(f'{self.didl}Descriptor')[1] \
          .find(f'{self.didl}Statement').find(f'{self.oai_dc}dc') \
          .find(f'{self.dc}language').text
        if lang == 'en' and self.correct_type(id):
          link = metadata.find(f'{self.didl}Component') \
            .find(f'{self.didl}Resource').attrib['ref']
          res = req.get(link)
          filename = self.folder.split('/')[-1] + '_' + id.split('/')[-1]
          f = Path(f'{self.folder}/{filename}.pdf')
          f.write_bytes(res.content)
        else:
          self.rejected_langs.add(lang)
      except AttributeError:
        continue
  
  def correct_type(self, id):
    """ Returns True if the item is of type thesis or publication. """
    for obj in self.data:
      if obj['id'] == id:
        if obj['type'] is None:
          return True
        return obj['type'] in ('thesis', 'publication')


if __name__ == "__main__":
  url = 'https://depositonce.tu-berlin.de/oai/request'
  format = 'didl'
  repo = 'depositonce'
  harvester = Harvester(url, format, repo)
  harvester.retrieve_all()
  print(harvester.rejected_langs)
  print('HU')
  url = 'https://edoc.hu-berlin.de/oai/request'
  repo = 'edoc'
  harvester = Harvester(url, format, repo)
  harvester.retrieve_all()
  print(harvester.rejected_langs)

  