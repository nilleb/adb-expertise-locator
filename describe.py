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
