import json

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

def read_content(path):
    with open(path) as fd:
        return json.load(fd)


author_documents = read_content("author_documents.json")

choices = set()
for author, document in author_documents.items():
    choices.add(author)
    for keyword in document["keywords"]:
        choices.add(keyword)

print(f"Dictionary: {len(set(choices))} words")

completer = FuzzyWordCompleter(choices)

text = prompt("> ", completer=completer, complete_while_typing=True, complete_in_thread=True)
print(text)
