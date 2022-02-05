from collections import defaultdict
import re

from common.folder_processor import FolderProcessor
from common.io import read_object
from statistics.describe_authors import sort_dictionary_values

authors = read_object("data/output/stanford_ner.json")
author_names = authors.keys()


def compute_mutations(name):
    tokens = sorted([string for string in re.split("[\s\.]", name) if string])
    key = " ".join(tokens)
    yield key, name

    for idx, word in enumerate(tokens):
        variant = [*tokens[:idx], word[0], *tokens[idx + 1 :]]
        key = " ".join(variant)
        if len(key) > 3:
            yield key, name
    return mutations


mutations = defaultdict(set)
for name in author_names:
    for key, value in compute_mutations(name):
        mutations[key].add(value)

sorted_mutations = sort_dictionary_values(mutations)
for a, b in sorted_mutations[-50:]:
    print(f"{a}, {len(b)}: {' = '.join([val for val in b])}")

duplicates_count = len([len(value) for value in mutations.values() if len(value) == 2])
print(f"=> we found {duplicates_count} duplicates")

# the algorithm works well on duplicates
# on the triplets, the history is different: the algorithm shows its limits
# A Morel, 3: Antoine Morel = Alain Morel = A. Morel
# Ahmed S, 3: Salman Ahmed = Ahmed Saeed = S. Ahmed
# David E, 3: E. David = David Elzinga = Edwin David
# George L, 3: George Luarsabishvili = L. George = Len George
# Xu Y, 3: Ye Xu = Yi Xu = Y. Xu
# {'Meenakshi Aggarwal', 'Meenakshi Ajmera'}


other_db_fullnames = set()


def process_single_file(filepath):
    wd = read_object(filepath)
    if isinstance(wd, dict):
        fullname = f"{wd.get('firstName')} {wd.get('lastName')}"
        other_db_fullnames.add(fullname)


FolderProcessor(["data/linkedin"], "*.json", process_single_file).process_folders()

other_db_mutations = defaultdict(set)

for name in other_db_fullnames:
    for key, value in compute_mutations(name):
        other_db_mutations[key].add(value)

common_mutations = set(other_db_mutations.keys()).intersection(set(mutations.keys()))
if common_mutations:
    print(f"in the secondary database we found some matching mutations.")
# there is high probablity that a matching mutation identifies the same person
# but the probability of error is not null
visited_fullnames = set()
count = 0
for mutation in common_mutations:
    for fullname in other_db_mutations[mutation]:
        if fullname not in visited_fullnames:
            visited_fullnames.add(fullname)
            print(f"{other_db_mutations[mutation]} = {mutations[mutation]}")
            count += 1

print(f"{count} distinct matching fullnames")
