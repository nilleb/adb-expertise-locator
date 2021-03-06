from . import (adb_crawler, consolidate_authors, extract_metadata_and_content, generate_document_titles,
               extract_named_entities, pdf_downloader, index_documents, regex_authors, uniquify)
from statistics import duplicates_and_matches

# I am preferring the adb website as a source because Google has lots of duplicates
# and eventually returns corrupted documents
kinds_addresses_map = adb_crawler.cached_crawl()

for folder, addresses in kinds_addresses_map.items():
    pdf_downloader.download_and_retry_once(folder, addresses)

folders = kinds_addresses_map.keys()
uniquify.main()
extract_metadata_and_content.main(folders)  # generates .metadata.json
generate_document_titles.main(folders)  # generates documents.json
regex_authors.main(folders)  # generates .regex-authors.json
extract_named_entities.main(folders)  # generates .stanford_ner.json
consolidate_authors.main(folders)  # generates author information (fullname, links to documents, keywords)

duplicates_and_matches.merge_authors()

index_documents.index_authors_documents("regex-authors")

print("OK, now you are ready to launch query.py")
