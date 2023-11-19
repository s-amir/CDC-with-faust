#!/bin/bash

mkdir -p data config_kafka data_kafka zookeeper/conf zookeeper/data zookeeper/logs kafka_logs kafka_zookeeper

chown -R 1001:1001 ./zookeeper config_kafka/ data_kafka/ kafka_logs/ data kafka_zookeeper
