""" Given the list of filenames retrieved with os.listdir(), check which
relevant documents are missing. """


import json

repo = 'depositonce'
files = json.load(open(f'../data/texts/txt/{repo}_files.json'))
items = json.load(open(f'../data/json/dim/{repo}/relevant_ids.json'))
ids = set([item.split('/')[1] for item in items])
file_ids = set([f[:-4].split('_')[1] for f in files])
assert len(ids) == len(items)
assert len(file_ids) == len(files)
missing = ids - file_ids
print(len(missing))
print(len(file_ids - ids))
print(len(ids) - len(file_ids))
