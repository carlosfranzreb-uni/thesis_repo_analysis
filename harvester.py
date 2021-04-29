""" Harvests publications from a OAI-PMH repository. """

import xml.etree.ElementTree as ET
import os
import requests as req


class Harvester:
  def __init__(self, base_url, folder, format):
    self.base_url = base_url
    self.folder = folder
    if not os.path.isdir(folder):
      raise OSError('Folder does not exist.')
    self.metadata_prefix = format
    self.oai = '{http://www.openarchives.org/OAI/2.0/}'

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
      with open(f'{self.folder}/publications_{cnt}.xml', 'w', encoding='utf8') as f:
        f.write(res.text)
      cnt += 1
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


if __name__ == "__main__":
  format = 'dim'
  harvester = Harvester(
    'https://refubium.fu-berlin.de/oai/request',
    'data/xml/dim/refubium',
    format
  )
  harvester.retrieve_all()
