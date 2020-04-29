# Download/process data from Wiktionary.

import bz2
import re
import sys
import urllib.request

from collections import defaultdict

TITLE_RE = r'.*<title>(.+)</title>.*'
LANGUAGE_RE = r'.*(?<!=)==([^={}<>]+)==(?!=).*'

def get_script_dir():
  return os.path.dirname(os.path.abspath(__file__))

def download_raw():
  '''Download the latest EN Wiktionary dump, this can take a while, currently 900 MB.'''
  #url = 'https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-meta-current.xml.bz2'
  url = 'https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles-multistream.xml.bz2'
  output = os.path.join(get_script_dir(), 'data/raw-multi.xml.bz2')
  print('Downloading pages-meta-current')
  urllib.request.urlretrieve(url, output)

def process_page(page, langs, errors):
  title = None
  ll = []
  banned_chars = [':', '/', ';']
  for line in page:
    t = re.match(TITLE_RE, line)
    if t:
      if title is not None:
        errors['Multiple titles'] += 1
        return None
      title = t.group(1)
      for c in banned_chars:
        if c in title:
          errors['Contains {}'.format(c)] += 1
          return None
    else:
      l = re.match(LANGUAGE_RE, line)
      if l:
        langs[l.group(1)] += 1
        ll.append(l.group(1))

  if title is None:
    errors['No title'] += 1
    return None
  if len(ll) == 0:
    errors['No corresponding languages'] += 1
    return None
  if len(ll) == 1 and ll[0] == 'Translingual':
    errors['Only translingual'] += 1
    return None
  return title + ':' + '&'.join(ll) + '\n'

def process_raw():
  # Processes the xml.bz2 downloaded into a csv with two fields, separated by ':'
  # word (title of page)
  # list of languages valid for that word, separated by '&'
  raw = os.path.join(get_script_dir(), 'data/raw.xml.bz2')
  output = os.path.join(get_script_dir(), 'data/processed.csv')
  fp = bz2.open(raw, mode='rt')
  fr = open(output, 'w')

  langs = defaultdict(int)
  errors = defaultdict(int)

  cur_page = []
  for line in fp:
    if '<page>' in line:
      p = process_page(cur_page, langs, errors)
      if p is not None:
        fr.write(p)
      cur_page = []
    else:
      cur_page.append(line)

  fp.close()
  fr.close()
  return langs, errors

def get_cached_data():
  cache = os.path.join(get_script_dir(), 'data/processed.csv')
  if os.path.exists(cache):
    cached_words = {}
    for line in cache:
      if len(line.split(':')) != 2:
        print(line)
        return None
      word, langs = line.split(':')
      cached_words[word] = set(langs.split('&'))
    return cached_words
  return None
