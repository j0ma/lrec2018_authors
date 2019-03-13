from collections import Counter
import lxml.html as html
import itertools as it
import pandas as pd
import requests
import cssselect
import time
import json

LREC_2018_URL = "http://www.lrec-conf.org/proceedings/lrec2018/papers.html"
AUTHOR_CSS_SELECTOR = "td.authors_papers"

def flatten_list(nested_list):
    t_start = time.time()
    out = list(it.chain.from_iterable(nested_list))
    t_end = time.time()
    elapsed = t_end - t_start
    print('Time elapsed: {}'.format(elapsed))
    return out

def tree_from_url(url):
    page = requests.get(url).content
    tree = html.fromstring(page)
    return tree

def grab_text_content(tree, css_selector):
    return [e.text_content() for e in
            tree.cssselect(css_selector)]

def pretty_print(d, indent=2):
    payload = json.dumps(d, indent=indent)
    print(payload)

print('Grab LREC 2018 publication tree...')
lrec_tree = tree_from_url(LREC_2018_URL)
print('Done... Grabbing all authors...')
authors = [a.strip().replace(' and', ',')
           for a in grab_text_content(lrec_tree,
                                      AUTHOR_CSS_SELECTOR)]
print('Done... Splitting each author list to get a nested list')
nested_authors = [a.split(', ') for a in authors]

print('Done... Flattening the list...')
flat_authors = flatten_list(nested_authors)

print('Done... Counting occurrences of each author')
lowercase_author_counts = Counter([a.lower() for a in flat_authors])

author_counts = pd.DataFrame()
author_counts['author'] = list(set(flat_authors))
author_counts['count'] = author_counts.author.apply(lambda a: lowercase_author_counts[a.lower()])
author_counts.sort_values('count', ascending=False, inplace=True)
author_counts.reset_index(inplace=True)
author_counts.drop('index', 1, inplace=True)

print('Done! here are top 50 most prolific authors')
top_authors = author_counts.head(50)

print('Done. Now saving to README')
table = top_authors.to_html(index=False)
with open('README.md', 'w') as f:
    f.write(table)
