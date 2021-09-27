import os
from time import sleep
from timeit import default_timer as timer
from urllib.error import HTTPError

from googlesearch import search

queries = {
    'pdf-generic': 'filetype:pdf site:adb.org',
    'reports': "filetype:pdf site:adb.org report and recommandation of the president",
    'technical': 'filetype:pdf site:adb.org technical and vocational education and training'
}

def my_search(query):
    last_sleep = 10
    start = 0
    num = 10

    while True:
        try:
            links = search(query, num=10, start=start, stop=start + num)
            if not links:
                return
            for link in links:
                print(link)
                yield link
            start += 10
        except HTTPError as err:
            print(err)
            last_sleep *= 2
            print(f"increasing sleep to {last_sleep}")
            sleep(last_sleep)


for name, query in queries.items():
    print(f"processing {name}")
    if not os.path.exists(f"{name}.txt"):
        start = timer()
        pdfs = [url for url in my_search(query)]            
        with open(f'{name}.txt', 'w') as fd:
            fd.write("\n".join(pdfs))
        end = timer()
        elapsed = end - start
        print(f"{name}.txt constituted in {elapsed}")
