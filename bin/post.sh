#!/bin/sh

scp $1 myles@bear.mylesbraithwaite.com:/srv/www/mylesb.ca/twtxt/html/twtxt.txt

cd ~/Documents/twtxt
git add twtxt.txt
git commit -m "Updated 'twtxt.txt' file on `date`."
