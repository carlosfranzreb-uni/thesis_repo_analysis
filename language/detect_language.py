""" How many titles and abstracts are actually not in english? Which ones? """


import json
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException


def detect_foreign(data_file, dump_file):
  """ Iterate through the documents in 'data_file' and store the IDs
  of the docs that either their title or abstract is not in english. """
  data = json.load(open(data_file))
  foreign = {'title': [], 'abstract': []}
  for id, texts in data.items():
    for text_type in ('title', 'abstract'):
      if texts[text_type] is not None:
        out = detect_language(texts[text_type])
        if out is not None:
          foreign[text_type].append((id, out[0], out[1]))
  json.dump(foreign, open(dump_file, 'w'))


def detect_language(text, prob=.99, n=10):
  """ To detect if a text is not in english, run the 'detect_langs' function
  on the text 'n' times. If the probability that the language is not english
  exceeds 'prob' in all 'n' runs, return the language and the avg. prob. If
  the condition is not met in any of the attempts or the language changes,
  return None. """
  probs = []
  foreign_language = None
  for _ in range(n):
    try:
      langs = detect_langs(text)
    except LangDetectException:
      print(text)
      return None
    if langs[0].lang != 'en' and langs[0].prob > .99:
      probs.append(langs[0].prob)
      if foreign_language is None:
        foreign_language = langs[0].lang
      else:
        if foreign_language != langs[0].lang:
          return None
    else:
      return None
  return (foreign_language, sum(probs)/len(probs))


if __name__ == "__main__":
  data_file = 'data/json/dim/all/improved_data.json'
  dump_file = 'data/json/dim/all/language/foreign_languages_improved.json'
  detect_foreign(data_file, dump_file)