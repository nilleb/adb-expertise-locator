from . import (adb_crawler, build_expertise_db, extract_metadata_and_content,
               extract_named_entities, pdf_downloader, es_index_documents)

# I am preferring the adb website as a source because Google has lots of duplicates
# and eventually returns corrupted documents
kinds_addresses_map = adb_crawler.crawl()

for folder, addresses in kinds_addresses_map.items():
    pdf_downloader.download_and_retry_once(folder, addresses)

folders = kinds_addresses_map.keys()

extract_metadata_and_content.process_folders(folders)  # generates .metadata.json
extract_named_entities.process_folders(folders)  # generates .classified.json

build_expertise_db.build_people_indexes(folders)  # generates author_documents and person_documents

index_name = es_index_documents.setup_index(1)
es_index_documents.index_authors_documents(index_name)

print("OK, now you are ready to launch es_query.py")
