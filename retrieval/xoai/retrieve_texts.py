""" Retrieve the full texts of the refubium publications that are either of
type 'thesis' or of type 'publication' and are written in english. 

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
xoai = '{http://www.lyncode.com/xoai}'


class Harvester:
  def __init__(self, base_url, format, repo):
    self.base_url = base_url
    self.repo = repo
    self.pdf_folder = f'../../data/texts/pdf/{repo}'
    self.txt_folder = f'../../data/texts/txt/{repo}'
    self.existing_txt = os.listdir(self.txt_folder)
    self.existing_pdf = os.listdir(self.pdf_folder)
    self.metadata_prefix = format
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
      .find(f'{oai}ListRecords') \
      .find(f'{oai}resumptionToken') \
      .text
  
  def retrieve_pdfs(self, res):
    """ Retrieve the PDFs of the items in the page 'res'. """
    root = ET.fromstring(res)
    records = root.find(f'{oai}ListRecords')
    for record in records:
      header = record.find(f'{oai}header')
      if record.tag == f'{oai}resumptionToken':
        continue
      elif 'status' in header.attrib and header.attrib['status'] == 'deleted':
        continue
      id = header.find(f'{oai}identifier').text
      metadata = record.find(f'{oai}metadata').find(f'{xoai}metadata')
      lang = self.find_lang(metadata)
      if lang in ('en', 'eng') and self.correct_type(id):
        try:
          bundle = self.get_bundle(metadata)
          if bundle is None:
            logging.info(f"No original bundle was found for {id}.")
            continue
          link = self.get_link(bundle)
          if link is None:
            logging.info(f"No link was found in the original bundle for {id}.")
            continue
          elif 'pdf' not in link.lower():
            logging.info(f"Link of {id} is not of pdf format: {link}.")
            continue
          filename = self.pdf_folder.split('/')[-1] + '_' + id.split('/')[-1]
        except AttributeError:
          logging.error(f"An error occured when looking for the link of {id}.")
          continue
        try:
          res = req.get(link)
        except UnicodeDecodeError:
          logging.error(f'{filename} couldn\'t be decoded')
          continue
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

  def find_lang(self, metadata):
    """ Return the language of the item. """
    for elem in metadata.findall(f'{xoai}element'):
      if elem.attrib['name'] == 'dc':
        for e in list(elem):
          if 'language' in e.attrib.values():
            for field in list(e):
              if 'value' in list(field)[0].attrib.values():
                return list(field)[0].text

  def correct_type(self, id):
    """ Returns True if the item is of type thesis or publication. """
    for obj in self.data:
      if obj['id'] == id:
        if obj['type'] is None:
          return True
        return obj['type'] in ('thesis', 'publication')

  def get_bundle(self, metadata):
    """ Return the bundle where the link to the PDF file resides. """
    for elem in metadata.findall(f'{xoai}element'):
      if elem.attrib['name'] == 'bundles':
        for bundle in list(elem):
          for f in list(bundle):
            if f.attrib['name'] == 'name':
              if 'original' in f.text.lower():
                return bundle
    return None
  
  def get_link(self, bundle):
    """ Return the link to the PDF file. """
    for element in list(bundle):
      if 'bitstreams' in element.attrib.values():
        for bitstream in list(element):
          for field in list(bitstream):
            if 'url' in field.attrib.values():
              return field.text
    return None

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


if __name__ == "__main__":
  logging.basicConfig(
    filename=f"../../logs/{str(int(time()))}.log",
    format='%(asctime)s %(message)s',
    level=logging.INFO
  )
  url = 'https://refubium.fu-berlin.de/oai/request'
  format = 'xoai'
  repo = 'refubium'
  logging.info(f'START OF {repo}')
  harvester = Harvester(url, format, repo)
  token = None
  harvester.retrieve_all(token)
  logging.info(f'Rejected languages in {repo}: {harvester.rejected_langs}')
  logging.info(f'END OF {repo}')
  