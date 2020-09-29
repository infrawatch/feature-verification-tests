curl -XPOST 'localhost:9200/_search?pretty' -d '{"query": {"bool": {"must": [{ "match": { "host": "overcloud-controller-0" } },{ "match": { "message":  "vm1" } }]}}}' > /tmp/output_instance_query.txt
