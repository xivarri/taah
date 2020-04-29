import iso639  # pip install iso369
import json
import random
import requests  # pip install requests
import taah.data

from bs4 import BeautifulSoup  # pip install bs4
from collections import defaultdict

URL = 'https://en.wiktionary.org/w/api.php?action=query&generator=random&prop=extracts&format=json&exlimit=1'
# If the first language (lexicographically) for a word is in this dict, potentially skip the word.
DEFAULT_SKIP_PROB = {'english' : 1,
                     'latin' : 0.8,
                     'spanish' : 0.75,
                     'italian' : 0.75,
                     'french' : 0.75,
                     'german' : 0.75,
                     'russian' : 1,
                     'translingual' : 1}

def get_word_online(skip_prob):
  r = requests.get(URL)
  d = json.loads(r.text)['query']['pages']
  d = d[list(d.keys())[0]]
  bs = BeautifulSoup(d['extract'], 'html.parser')
  langs = {h.text.lower() for h in bs.find_all('h2')}

  if len(langs) < 1 or ':' in d['title']:
    return None, None
  lang_list = sorted(langs)
  if lang_list[0] in skip_prob and random.random() < skip_prob[lang_list[0]]:
    return None, None

  return d['title'], langs

def get_word_offline(words_to_langs, skip_prob):
  while True:
    word = random.choice(tuple(words_to_langs))
    langs = words_to_langs[word]
    if len(langs) == 1 and random.random() < skip_prob[list(langs[0])]:
      continue
    return word, langs

def play(skip_prob=DEFAULT_SKIP_PROB,
         max_rounds=float('inf'),
         dist_test=False,
         online=False):
  if dist_test and max_rounds == float('inf'):
    print('Must provide max_rounds when testing distributions, no infinite loops please.')
    return

  words_to_langs = None if online else taah.data.get_cached_data()
  if not online and not words_to_langs:
    print('You need to download data from Wiktionary first')
    return

  win = 0
  rounds = 0

  part1 = iso639.languages.part1
  part3 = iso639.languages.part3

  seen_langs = defaultdict(int)

  while rounds < max_rounds:
    word, langs = get_word_online(skip_prob) if online else get_word_offline(words_to_langs, skip_prob)
    if not word:
      continue
    print(word)
    rounds += 1
    if dist_test:
      for lang in langs:
        seen_langs[lang] += 1
      continue

    guess = input()

    if guess.lower() in langs or ((guess in part3 and part3[guess].name.lower() in langs)
                                  or (guess in part1 and part1[guess].name.lower() in langs)):
      print('Зөв!')
      win += 1
    else:
      print('Алдаатай :(')
    print('All valid languages: ', sorted(langs))

    print('Session score: {}/{} = {}\n'.format(win,
                                               rounds,
                                               win/rounds))
  if dist_test:
    return seen_langs

def set_language_skip_prob(language, probability):
  DEFAULT_SKIP_PROB[language] = probability
