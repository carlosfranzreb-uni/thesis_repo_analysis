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


if __name__ == "__main__":
  id = "oai:depositonce.tu-berlin.de:11303/11631"
  formats = ["qdc", "mods", "didl", "ore", "mets", "oai_dc", "marc", "dim"]
  for format in formats:
    harvester = Harvester(
      'https://depositonce.tu-berlin.de/oai/request',
      'data/metadata_formats',
      format
    )
    res = harvester.request('GetRecord', params={'identifier': id})
    with open(f'data/metadata_formats/{format}.xml', 'w', encoding='utf8') as f:
      f.write(res.text)
