""" Given the list of filenames retrieved with os.listdir(), check which
relevant documents are missing. """


import json
import os


def prinf_facts():
  """ Print some facts about the missing files. """
  for repo in ('depositonce', 'edoc', 'refubium'):
    files = json.load(open(f'../data/texts/txt/{repo}_files.json'))
    items = json.load(open(f'../data/json/dim/{repo}/relevant_ids.json'))
    ids = set([item.split('/')[1] for item in items])
    file_ids = set([f[:-4].split('_')[1] for f in files])
    assert len(ids) == len(items)
    assert len(file_ids) == len(files)
    missing = ids - file_ids
    print(f'{repo} has {len(files)} files.')
    print(len(missing))
    print(len(file_ids - ids))
    print(len(ids) - len(file_ids))


def search_logs():
  """ Search the logs for the missing files. """
  missing_logs = {}
  for repo in ('depositonce', 'edoc', 'refubium'):
    files = json.load(open(f'../data/texts/txt/{repo}_files.json'))
    items = json.load(open(f'../data/json/dim/{repo}/relevant_ids.json'))
    ids = set([item.split('/')[1] for item in items])
    file_ids = set([f[:-4].split('_')[1] for f in files])
    missing = ids - file_ids
    missing_files = [f'{repo}_{id}' for id in missing]
    for missing_file in missing_files:
      for filename in os.listdir('../logs'):
        with open(f'../logs/{filename}') as f:
          if repo not in f.readline():
            continue
          for line in f:
            if missing_file + " " in line:
              missing_logs[missing_file] = line
  json.dump(missing_logs, open('missing_files.json', 'w'))


def get_missing_ids(repo):
  files = json.load(open(f'../data/texts/txt/{repo}_files.json'))
  items = json.load(open(f'../data/json/dim/{repo}/relevant_ids.json'))
  ids = set([item.split('/')[1] for item in items])
  file_ids = set([f[:-4].split('_')[1] for f in files])
  return ids - file_ids 


if __name__ == "__main__":
  for repo in ('depositonce', 'edoc', 'refubium'):
    missing = get_missing_ids(repo)
    json.dump(list(missing), open(f'{repo}_missing.json', 'w'))

