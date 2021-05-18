""" Remove duplicates from the txt folders. """


import os
import re


regexp = re.compile('depositonce_[0-9]+_[0-9]+')
folder = '../data/texts/txt/depositonce'
for f in os.listdir(folder):
  if regexp.match(f):
    os.remove(f'{folder}/{f}')