#!/bin/sh

mkdir run
mkdir logs
mkdir tmp

m2sh load -config ./conf.py
m2sh servers -db ./config.sqlite
m2sh start -db ./config.sqlite -host localhost

tail -f ./logs/*.log
