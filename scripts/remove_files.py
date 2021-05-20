""" Remove duplicates from the txt folders. """


import os
import re


repo = 'refubium'
regexp = re.compile(f'{repo}_[0-9.]+_[0-9]+')
folder = f'../data/texts/txt/{repo}'
for f in os.listdir(folder):
  if regexp.match(f):
    os.remove(f'{folder}/{f}')