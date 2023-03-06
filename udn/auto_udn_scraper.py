# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import pymysql
import datetime
import json
from codebase.output import output_mysql
from codebase.multi_thread import multi_crawling


db_list = [
    'important',
    'sport',
    'global',
    'social',
    'produce',
    'stock',
    'life',
    'education',
    'comment',
    'local',
    'cntw',
    'digit',
    'read',
    'other'
]


def check_last_time():
    # 連線資料庫之資訊
    host = "140.117.69.136"
    user = "crawler"
    password = "lab_30241#"
    last_time = datetime.datetime(2021, 1, 1)
    connection = pymysql.connect(host, user, password)
    with connection.cursor() as cursor:
        for db_name in db_list:
            cursor.execute("use crawler_udn_" + db_name)
            for year in range(2021, datetime.datetime.now().year+1):
                try:
                    cursor.execute("select MAX(artDate) from %s_%i" % (db_name, year))
                except pymysql.err.ProgrammingError:
                    continue
                result = cursor.fetchone()[0]
                if result is None or isinstance(result, str):
                    continue
                if result > last_time:
                    last_time = result
    print("當前資料庫中最後一篇的時間:", last_time)
    return last_time


if __name__ == '__main__':
    # 設定時間
    s_time = check_last_time()
    # 可設定從特定時間開始
    # s_time = datetime.datetime.strptime("2020-03-01 11:56:00", "%Y-%m-%d %H:%M:%S")
    print(s_time)
    e_time = datetime.datetime.now()

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    all_links = []
    keep = 0

    for count in range(1, 300):
        href_resp = requests.get("https://udn.com/api/more?page=" + str(count) + "&id=&channelId=1&cate_id=0&type=breaknews", headers=headers)
        crawl_href = json.loads(href_resp.content.decode('utf-8'))
        
        # 已經無內容
        if 'lists' not in crawl_href:
            break
        
        # 頁面第一篇的時間
        lim_time = datetime.datetime.strptime(crawl_href['lists'][0]['time']['date'], "%Y-%m-%d %H:%M")
        if s_time > lim_time:
            break
        for link in crawl_href['lists']:
            if s_time > datetime.datetime.strptime(link['time']['date'], "%Y-%m-%d %H:%M"):
                break
            all_links.append("https://udn.com" + link['titleLink'].split("?")[0])

        print("搜尋新聞連結中...，目前搜尋時間進度:", lim_time)

    # 爬文內容
    results = multi_crawling(all_links[keep:keep+len(all_links)])
    keep = len(all_links)
    # 匯入mysql
    count_saved = output_mysql(results)

    with open("udn.txt", "w", encoding='utf-8') as result_file:
        result_file.write(f"-聯合- 更新筆數: {count_saved}, 完成時間: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")

    print("更新資料庫新聞完成，總更新筆數:", count_saved)

