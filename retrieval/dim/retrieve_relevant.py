""" Retrieve the IDs of theses or publications written in english. These are
the document types that are relevant for my work. Which types are included
in the groups 'thesis' and 'publication' can be seen in 
analysis/oai_dc/types/clustered_types.json """


from xml.etree import ElementTree as ET
import json
import os
import langdetect

from retrieve_relevant_subjects import extract_number


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
        doc_type = get_type(metadata)
        data.append({
          'id': id,
          'type': doc_type,
          'title': get_title(metadata),
          'date': get_date(metadata),
          'authors': get_contributors(metadata),
          'subjects': get_subjects(metadata),
          'rights': get_rights(metadata),
          'publisher': get_publisher(id, doc_type, metadata)
        })
  json.dump(data, open(dump, 'w'))


def get_type(metadata):
  """ Return the type of the publication and the corresponding 
  cluster as a tuple. """
  for f in metadata.findall(f'{dim}field'):
    if f.attrib['element'] == 'type':
      text = f.text.lower().replace(' ', '').replace('doc-type:', '')
      if text in types['thesis']:
        return (text, 'thesis')
      elif text in types['publication']:
        return (text, 'publication')


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


def get_contributors(metadata):
  """ Return contributors as a list of tuples with their names and their 
  qualifier. In refubium they put gender or an email as a contributor: 
  ignore that.
  Also, they order referees as 'firstReferee' and 'furtherReferee', while
  in edoc and depositonce it is just 'referee'. It should be like that
  for refubium documents as well. """
  contributors = []
  for f in metadata.findall(f'{dim}field'):
    if f.attrib['element'] == 'contributor':
      if 'qualifier' in f.attrib:
        if f.attrib['qualifier'] in ('gender', 'contact'):
          continue
        elif f.attrib['qualifier'] in ('firstReferee', 'furtherReferee'):
          f.attrib['qualifier'] = 'referee'
        contributors.append((f.text, f.attrib['qualifier']))
      else:
        contributors.append((f.text, 'unknown'))
  return contributors


def get_subjects(metadata):
  """ Return english subjects (or those without a language) and their
  qualifiers as a list of tuples. If subject is of type DDC, extract
  the number. """
  subjects = []
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
        subjects.append((f.text, f.attrib['qualifier']))
  return subjects


def get_rights(metadata):
  """ Get the URI to the rights statement of the document. """
  for f in metadata.findall(f'{dim}field'):
    if f.attrib['element'] == 'rights':
      if 'qualifier' in f.attrib and f.attrib['qualifier'] == 'uri':
        return f.text
  return None


def get_publisher(id, doc_type, metadata):
  """ Get the publisher of the document. If the document is a thesis, the publisher
  is the university. In some documents, the faculty is mentioned, which could
  be useful. Refubium doesn't have publisher fields for theses.
  For publications, return (journal title, publisher name).
  In depositonce and refubium the title (journal, book, proceedings, etc.) is in 
  bibliographicCitation -> journaltitle and the publisher name in
  bibliographicCitation -> originalpublishername.
  In edoc the journal title is in edoc -> container-title and the publisher
  name in edoc -> container-publisher-name. """
  if doc_type[1] == 'thesis':
    if 'refubium' in id:
      return None
    else:
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'publisher':
          return f.text
  elif doc_type[1] == 'publication':
    title, name = None, None
    if 'edoc' in id:
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'edoc' and 'qualifier' in f.attrib:
          if f.attrib['element'] == 'container-title':
            title = f.text
          elif f.attrib['qualifier'] == 'container-publisher-name':
            name = f.text
        if name is not None and title is not None:
          return (title, name)
    else:
      for f in metadata.findall(f'{dim}field'):
        if f.attrib['element'] == 'bibliographicCitation' and \
            'qualifier' in f.attrib:
          if 'title' in f.attrib['qualifier']:
            title = f.text
          elif f.attrib['qualifier'] == 'originalpublishername':
            name = f.text
          if name is not None and title is not None:
            return (title, name)
    return (title, name)


if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    retrieve_relevant(
      json.load(open(f'../../data/json/dim/{repo}/relevant_ids.json')),
      f'../../data/xml/dim/{repo}',
      f'../../data/processed/dim/{repo}.json'
    )
