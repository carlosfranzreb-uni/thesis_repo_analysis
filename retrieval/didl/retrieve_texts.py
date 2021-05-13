""" Retrieve the full texts of the publications that are either of type
'thesis' or of type 'publication' and are written in english. 

The links to the resources can be found in the 'didl' metadata format for
edoc and depositonce and in 'xoai' for refubium. """


import requests as req
import xml.etree.ElementTree as ET
import os
from pathlib import Path
import json
import logging
from tika import parser
from time import sleep, time


oai = '{http://www.openarchives.org/OAI/2.0/}'


class Harvester:
  def __init__(self, base_url, format, repo):
    self.base_url = base_url
    self.repo = repo
    self.pdf_folder = f'../../data/texts/pdf/{repo}'
    self.txt_folder = f'../../data/texts/txt/{repo}'
    self.existing_txt = os.listdir(self.txt_folder)
    self.existing_pdf = os.listdir(self.pdf_folder)
    self.metadata_prefix = format
    self.oai = '{http://www.openarchives.org/OAI/2.0/}'
    self.oai_dc = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
    self.dc = '{http://purl.org/dc/elements/1.1/}'
    self.didl = '{urn:mpeg:mpeg21:2002:02-DIDL-NS}'
    self.rejected_langs = set()
    self.data = json.load(open(f'../../data/processed/oai_dc/{repo}.json'))

  def request(self, verb, params=dict()):
    """ Executes a request with the given verbs and parameters. The parameters
    are given as a dict. """
    request = f'{self.base_url}?verb={verb}'
    for key, value in params.items():
      request += f'&{key}={value}'
    if 'resumptionToken' not in params:
      request += f'&metadataPrefix={self.metadata_prefix}'
    return req.get(request)

  def retrieve_all(self, token=None):
    """ Retrieve all publications. If a resumption token is given,
    start there. """
    done = False
    cnt = 1
    if token is None:
      res = self.request('ListRecords')
    else:
      res = self.request('ListRecords', {'resumptionToken': token})
    while not done:
      self.retrieve_pdfs(res.text)
      token = self.get_resumption_token(res.text)
      logging.info(f'Resumption token: {token}')
      if token is None or len(token) == 0:
        done = True
      else:
        res = self.request('ListRecords', {'resumptionToken': token})
  
  def get_resumption_token(self, text):
    return ET.fromstring(text) \
      .find(f'{self.oai}ListRecords') \
      .find(f'{self.oai}resumptionToken') \
      .text
  
  def retrieve_pdfs(self, res):
    """ Retrieve the PDFs of the items in the page 'res'. """
    root = ET.fromstring(res)
    records = root.find(f'{self.oai}ListRecords')
    for record in records:
      header = record.find(f'{self.oai}header')
      if record.tag == f'{oai}resumptionToken':
        continue
      elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
        continue
      id = header.find(f'{self.oai}identifier').text
      metadata = record.find(f'{self.oai}metadata').find(f'{self.didl}DIDL') \
        .find(f'{self.didl}Item')
      lang = metadata.findall(f'{self.didl}Descriptor')[1] \
        .find(f'{self.didl}Statement').find(f'{self.oai_dc}dc') \
        .find(f'{self.dc}language').text
      if lang in ('en', 'eng') and self.correct_type(id):
        link = metadata.find(f'{self.didl}Component') \
          .find(f'{self.didl}Resource').attrib['ref']
        try:
          res = req.get(link)
        except UnicodeDecodeError:
          logging.error(f'{filename} couldn\'t be decoded')
          continue
        filename = self.pdf_folder.split('/')[-1] + '_' + id.split('/')[-1]
        if f'{filename}.txt' in self.existing_txt:
          logging.info(f'File {filename} has already been retrieved.')
          continue
        elif f'{filename}.txt' in os.listdir(self.txt_folder):
          logging.info(f'File name {filename} already exists.')
          filename += f"_{int(time())}"
        f = Path(f'{self.pdf_folder}/{filename}.pdf')
        f.write_bytes(res.content)
        self.parse_pdf(filename)
        sleep(5)
      else:
        self.rejected_langs.add(lang)

  def correct_type(self, id):
    """ Returns True if the item is of type thesis or publication. """
    for obj in self.data:
      if obj['id'] == id:
        if obj['type'] is None:
          return True
        return obj['type'] in ('thesis', 'publication')

  def parse_pdf(self, filename):
    """ Extract the text of the PDF and store it in a TXT file.
    Delete the PDF file afterwards. Don't remove the PDF files
    whose content is None. """
    try:
      pdf_file = f'{self.pdf_folder}/{filename}.pdf'
      pdf = parser.from_file(pdf_file)
      if pdf["content"] is not None:
        with open(f'{self.txt_folder}/{filename}.txt', 'w', encoding='utf8') as f:
          f.write(pdf["content"])
        os.remove(pdf_file)
    except req.exceptions.ReadTimeout:
      logging.error(f"Parsing of {filename} failed.")
      self.parse_pdf(filename)


if __name__ == "__main__":
  logging.basicConfig(
    filename=f"../../logs/{str(int(time()))}.log",
    format='%(asctime)s %(message)s',
    level=logging.INFO
  )
  url = 'https://depositonce.tu-berlin.de/oai/request'
  format = 'didl'
  # repo = 'depositonce'
  # logging.info(f'START OF {repo}')
  # harvester = Harvester(url, format, repo)
  # token = 'didl////5200'
  # harvester.retrieve_all(token)
  # logging.info(f'Rejected languages in {repo}: {harvester.rejected_langs}')
  # logging.info(f'END OF {repo}')
  url = 'https://edoc.hu-berlin.de/oai/request'
  repo = 'edoc'
  logging.info(f'START OF {repo}')
  harvester = Harvester(url, format, repo)
  harvester.retrieve_all()
  logging.info(f'Rejected languages in {repo}: {harvester.rejected_langs}')
  logging.info(f'END OF {repo}')

  