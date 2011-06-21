#!/usr/bin/env bash
mkdir $1
cd $1
/opt/local/bin/wget -r -l 2 -k -R jpeg,jpg,gif,png,mov,js,css,swf,pdf,bmp,svg -Q 5m $1
