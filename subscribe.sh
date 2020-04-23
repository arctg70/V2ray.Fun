#!/bin/bash
#
mv subscribe.list subscribe.list.bak
wget $1
if [ $? -eq 0 ];then
unzip -P $2 subscribe.list.zip
rm subscribe.list.zip
fi
