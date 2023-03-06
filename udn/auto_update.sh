#!/bin/bash
source /home/crawler/NEWS_crawler/news_crawler/bin/activate
cd /home/crawler/NEWS_crawler/udn
rm udn.out
python auto_udn_scraper.py > udn.out &
deactivate