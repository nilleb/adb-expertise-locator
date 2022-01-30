from collections import defaultdict
from email.policy import default
import json
from operator import countOf

authors = "data/intermediate/person_documents.json"
try:
    with open(authors) as fd:
        loaded_results = json.load(fd)
        print(f"loaded successfully {len(loaded_results.keys())} profiles")
except:
    loaded_results = []


def is_anomaly(key):
    return len(key) > 100 or " " not in key


def is_mild_anomaly(key):
    final = ' '.join(set(key.split(' ')))
    return (
        (len(key) > 50 and len(key) < 100)
        or countOf(key, " ") > 4
        or countOf(key, ".") > 4
        or final != key
    )


legit, mild_anomalies, anomalies = [], [], []
for key in loaded_results.keys():
    if is_anomaly(key):
        anomalies.append(key)
        continue
    if is_mild_anomaly(key):
        mild_anomalies.append(key)
        continue
    legit.append(key)

print(
    f"{len(legit)} legit, {len(anomalies)} anomalies, {len(mild_anomalies)} mild anomalies"
)
longest_legit = sorted(legit, key=len, reverse=True)
for item in longest_legit[:1000]:
    print(item)

# FIXME analyze the keywords we have in the 'classified.json' files
# 2788 pdf
# 5285 classified.json
all_metadata = 'data/intermediate/all_metadata.json'
with open(all_metadata) as fd:
    loaded_results = json.load(fd)
    print(f"loaded successfully {len(loaded_results.keys())} texts")

# loaded successfully 536 texts

all_keys = {}
keys_counts = defaultdict(int)
for title, metadata in loaded_results.items():
    for key, item in metadata.items():
        new_type = str(type(item))
        existing_type = all_keys.get(key)
        if new_type != existing_type and existing_type:
            print(f"warning: {key} (was: {existing_type}) is now {new_type}")
        all_keys[key] = new_type
        keys_counts[key] += 1
for key, item in all_keys.items():
    print(f"{key} {item} {keys_counts[key]}")

all_keywords_count = defaultdict(int)
all_keywords_documents = defaultdict(set)
for title, metadata in loaded_results.items():
    keywords = metadata.get('Keywords', "").split(',')
    for keyword in keywords:
        all_keywords_count[keyword] += 1
        all_keywords_documents[keyword].add(title)

# sort by number of occurrences
# tell how many keywords we have
# tell most common occurrences across texts
# Title <class 'str'> 502
# content <class 'str'> 536
# Author <class 'str'> 515
# CreationDate <class 'str'> 535
# Creator <class 'str'> 519
# Keywords <class 'str'> 442
# ModDate <class 'str'> 533
# Producer <class 'str'> 530

# ❯ find . -type f -iname "*.pdf" | wc
#     2788    2788  111878
# ❯ find . -type f -iname "*.classified.json" | wc
#     5285    5285  368422

# FIXME how many documents are being referenced by the people in the elasticsearch?
all_metadata = 'data/intermediate/person_documents.json'
documents = set()
with open(all_metadata) as fd:
    loaded_results = json.load(fd)
    print(f"loaded successfully {len(loaded_results.keys())} people")
    for author, data in loaded_results.items():
        for document in data.get('documents', []):
            documents.add(document)
print(f"the persons mention {len(documents)} distinct documents")
# loaded successfully 14488 people
# the persons mention 2137 distinct documents
