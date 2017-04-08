#!/usr/bin/sh
for pid in $(ps -ef | awk '/persistent-learning.py/ {print $2}'); do sudo kill -9 $pid; done
sudo ./persistent-learning.py  &


