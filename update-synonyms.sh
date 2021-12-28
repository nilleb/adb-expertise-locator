docker-compose up -d elasticsearch
docker exec -it adb-es mkdir -p /usr/share/elasticsearch/config/analysis
docker cp synonyms.txt adb-es:/usr/share/elasticsearch/config/analysis/default-synonyms.txt
# curl -X DELETE http://elastic:3WnQtogV2Tf9h4kjQ5hPAAKeg6jwypVFPSJNm6iaTE5QMTcYavg4tKph8eb6@127.0.0.1:9200/s_adb_people_v1
curl -X PUT http://elastic:3WnQtogV2Tf9h4kjQ5hPAAKeg6jwypVFPSJNm6iaTE5QMTcYavg4tKph8eb6@127.0.0.1:9200/s_adb_people_v1 --data-binary "@configuration/index_settings.json"
curl -X POST http://elastic:3WnQtogV2Tf9h4kjQ5hPAAKeg6jwypVFPSJNm6iaTE5QMTcYavg4tKph8eb6@127.0.0.1:9200/s_adb_people_v1/_reload_search_analyzers
