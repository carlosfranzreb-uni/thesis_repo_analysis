""" Given the already extracted relevant data, improve it by replacing the
titles and abstracts chosen by langdetect (stored in the files best_titles.json
and best_abstracts.json) by their original ones. """


import json
import logging
from time import time


def improve():
  data = json.load(open('data/json/dim/all/relevant_data.json'))
  titles = json.load(open('data/json/dim/all/language/best_titles.json'))
  abstracts = json.load(open('data/json/dim/all/language/best_abstracts.json'))
  for id in data:
    if id not in titles:
      titles[id] = None
    if id not in abstracts:
      abstracts[id] = None
    best = {'title': titles[id], 'abstract': abstracts[id]}
    for key in best:
      if best[key] is not None:
        if data[id][key] != best[key]:
          old_short = data[id][key][:10] + '...' if len(data[id][key]) > 10 \
            else data[id][key]
          new_short = best[key][:10] + '...' if len(best[key]) > 10 else best[key]
          logger.info(
            f'Change {key} of {id} from "{old_short}" to "{new_short}".'
          )
          data[id][key] = best[key]
  json.dump(data, open('data/json/dim/all/improved_data.json', 'w'))


if __name__ == '__main__':
  logger= logging.getLogger()
  logger.setLevel(logging.INFO)
  handler = logging.FileHandler(
    f"logs/changelang_{str(int(time()))}.log", 'w', 'utf-8'
  )
  handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
  logger.addHandler(handler)
  improve()
