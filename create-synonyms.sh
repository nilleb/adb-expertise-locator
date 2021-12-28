docker-compose up -d elasticsearch
docker exec -it adb-es mkdir -p /usr/share/elasticsearch/config/analysis
docker cp synonyms.txt adb-es:/usr/share/elasticsearch/config/analysis/default-synonyms.txt
