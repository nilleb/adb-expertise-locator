from collections import defaultdict
import re

from charset_normalizer import logging

from common.folder_processor import FolderProcessor
from common.io import read_object, write_object
from statistics.describe_authors import sort_dictionary_values


def get_tokens(name):
    return re.split("[\s\.]", name)


def compute_mutations(name):
    tokens = sorted([string.strip() for string in get_tokens(name) if string.strip()])
    key = " ".join(tokens)
    yield key, name

    for idx, word in enumerate(tokens):
        variant = [*tokens[:idx], word[0], *tokens[idx + 1 :]]
        key = " ".join(variant)
        if len(key) > 3:
            yield key, name
    return


def check_whether_could_be_the_same_person(fullnames):
    """
    The risk of catalogating two individuals as the same person,
    this function tries to highlight where this risk is evident.
    """
    fullname = fullnames[0]
    is_short_name = "." in fullname
    short_names = [fn for fn in fullnames[1:] if "." in fn]
    complete_names = [fn for fn in fullnames[1:] if "." not in fn]
    risk = False
    if not is_short_name and not short_names:
        tokens = get_tokens(fullname)
        for fn in complete_names:
            tn = get_tokens(fn)
            if sorted(tn) != sorted(tokens):
                logging.info(f"there is a risk that {tn} != {tokens}.")
                risk = True
    return risk


def compute_all_mutations(set_of_names):
    mutations = defaultdict(set)
    for name in set_of_names:
        for key, value in compute_mutations(name):
            if mutations[key]:
                fullnames = set(value) if isinstance(value, set) else set([value])
                fullnames.union(mutations[key])
                check_whether_could_be_the_same_person(list(fullnames))
            mutations[key].add(value)
    return mutations


def duplicates_analysis(mutations):
    sorted_mutations = sort_dictionary_values(mutations)
    for a, b in sorted_mutations[-50:]:
        print(f"{a}, {len(b)}: {' = '.join([val for val in b])}")

    duplicates_count = len(
        [len(value) for value in mutations.values() if len(value) == 2]
    )
    print(f"=> we found {duplicates_count} duplicates")

    # the algorithm works well on duplicates
    # on the triplets, the history is different: the algorithm shows its limits
    # A Morel, 3: Antoine Morel = Alain Morel = A. Morel
    # Ahmed S, 3: Salman Ahmed = Ahmed Saeed = S. Ahmed
    # David E, 3: E. David = David Elzinga = Edwin David
    # George L, 3: George Luarsabishvili = L. George = Len George
    # Xu Y, 3: Ye Xu = Yi Xu = Y. Xu
    # {'Meenakshi Aggarwal', 'Meenakshi Ajmera'}


def analyze_matches(primary_db_mutations, secondary_db_mutations):
    common_mutations = set(secondary_db_mutations.keys()).intersection(
        set(primary_db_mutations.keys())
    )
    if common_mutations:
        print(f"in the secondary database we found some matching mutations.")
    # there is high probablity that a matching mutation identifies the same person
    # but the probability of error is not null
    visited_fullnames = set()
    count = 0
    for mutation in common_mutations:
        for fullname in secondary_db_mutations[mutation]:
            if fullname not in visited_fullnames:
                visited_fullnames.add(fullname)
                print(
                    f"{secondary_db_mutations[mutation]} = {primary_db_mutations[mutation]}"
                )
                count += 1

    print(f"{count} distinct matching fullnames across the two databases.")


CONCAT_KEYS = set(["role", "documentRole", "organization"])
DICT_KEYS = set(["keywords"])
EXCLUDED_KEYS = CONCAT_KEYS.union(DICT_KEYS)


def to_list(document, key):
    val = document.get(key, []) or []
    val = val if isinstance(val, list) else [val]
    return val


def merge_authors():
    authors = dict(read_object("data/output/regex-authors.json"))
    authors_keys = set(authors.keys())
    authors_count_before = len(authors_keys)
    primary_db_mutations = compute_all_mutations(authors_keys)
    for _, author_names in primary_db_mutations.items():
        document = {}
        complete_name = None
        for name in author_names:
            if not complete_name and "." not in name:
                complete_name = name
            if authors.get(name):
                author = dict(authors.pop(name))
                for key in CONCAT_KEYS:
                    val = to_list(document, key)
                    aval = to_list(author, key)
                    val.extend(aval)
                    document[key] = list(set(val))
                for key in DICT_KEYS:
                    for k, v in author.get(key, {}).items():
                        tou = document.get(key, {}) or {}
                        tou[k] = tou.get(k, 0) + v
                        document[key] = tou
                for key in author.keys() - EXCLUDED_KEYS:
                    document[key] = author[key]
        if document:
            authors[complete_name or name] = document
    authors_count_after = len(authors.keys())
    print(f"tree shaking the authors: {authors_count_before} -> {authors_count_after}")
    write_object(authors, "data/output/regex-authors-merged.json")


def main():
    authors = read_object("data/output/regex-authors.json")
    author_names = authors.keys()
    primary_db_mutations = compute_all_mutations(author_names)
    duplicates_analysis(primary_db_mutations)

    other_db_fullnames = set()

    def process_single_file(filepath):
        wd = read_object(filepath)
        if isinstance(wd, dict):
            fullname = f"{wd.get('firstName')} {wd.get('lastName')}"
            other_db_fullnames.add(fullname)

    FolderProcessor(["data/linkedin"], "*.json", process_single_file).process_folders()

    secondary_db_mutations = compute_all_mutations(other_db_fullnames)
    duplicates_analysis(secondary_db_mutations)

    analyze_matches(primary_db_mutations, secondary_db_mutations)
    print(
        f"cardinality of the two sets: {len(author_names)}, {len(other_db_fullnames)}."
    )


if __name__ == "__main__":
    merge_authors()
    main()
