""" Given the already extracted relevant data, improve it by replacing the
titles and abstracts chosen by langdetect (stored in the files best_titles.json
and best_abstracts.json) by their original ones. """


import json
import logging
from time import time



def improve():
  data = json.load(open('data/json/dim/all/relevant_data.json'))
  titles = json.load(open('data/json/dim/all/best_titles.json'))
  abstracts = json.load(open('data/json/dim/all/best_abstracts.json'))
  for id in data:
    best = {'title': titles[id], 'abstract': abstracts[id]}
    for key in best:
      if best[key] is not None:
        if data[id][key] != best[key]:
          logging.info(f'Change {key} of id from {data[id][key]} to {best[key]}.')
          data[id][key] = best[key]
  json.dump(data, open('data/json/dim/all/improved_data.json', 'w'))


if __name__ == '__main__':
  logging.basicConfig(
    filename=f"logs/changelang_{str(int(time()))}.log",
    format='%(asctime)s %(message)s',
    level=logging.INFO
  )
  improve()
