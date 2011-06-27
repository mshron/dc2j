#!/bin/sh

curl -T fake_newspapers.csv http://localhost:8081/data/newspapers
curl -d nid=1 -d email-0=max.shron@gmail.com -d "name-0=Max Shron" -d isperson=on http://localhost:8081/input/journalists
curl -d nid=1 -d lat=40.6936488 -d lng=-89.5889864 -d offsetLat=0.9975025 -d offsetLng=0.3686301 http://localhost:8081/data/newspapers
curl -d dcid=567364 http://localhost:8081/data/task/querydc
