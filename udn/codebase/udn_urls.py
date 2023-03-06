from bs4 import BeautifulSoup
import datetime
import requests
import time

category_list = {
    'all': "https://udn.com/rank/ajax_newest/2/0",  # 全站總排行
    'important': "https://udn.com/rank/ajax_newest/2/6638",  # 要聞
    'sport': "https://udn.com/rank/ajax_newest/2/7227",  # 運動
    'global': "https://udn.com/rank/ajax_newest/2/7225",  # 全球
    'social': "https://udn.com/rank/ajax_newest/2/6639",  # 社會
    'produce': "https://udn.com/rank/ajax_newest/2/6644",  # 產經
    'stock': "https://udn.com/rank/ajax_newest/2/6645",  # 股市
    'life': "https://udn.com/rank/ajax_newest/2/6649",  # 生活
    'education': "https://udn.com/rank/ajax_newest/2/11195",  # 文教
    'comment': "https://udn.com/rank/ajax_newest/2/6643",  # 評論
    'local': "https://udn.com/rank/ajax_newest/2/6641",  # 地方
    'cn-tw': "https://udn.com/rank/ajax_newest/2/6640",  # 兩岸
    'digit': "https://udn.com/rank/ajax_newest/2/7226",  # 數位
    'read': "https://udn.com/rank/ajax_newest/2/12659"  # 閱讀
    }

year = datetime.datetime.now().strftime("%Y") + "/"


def get_urls(range_start, range_end, category):
    all_links = []
    # 因為頁面中的時間並無年份，以搜尋當下的年份視為第一篇文章的年份
    year = datetime.datetime.now().strftime("%Y") + "/"

    # 轉換時間格式
    s_time = datetime.datetime.strptime(range_start, "%Y-%m-%d %H:%M:%S")
    e_time = datetime.datetime.strptime(range_end, "%Y-%m-%d %H:%M:%S")

    for count in range(1, 300):
        href_resp = requests.get(category_list[category] + "/%s" % count)
        crawl_href = BeautifulSoup(href_resp.text, "html.parser")

        if crawl_href.text == "":
            break

        # 若該頁面時間已超出設定範圍即結束，遇到錯誤則將該頁面時間設為當下時間
        try:
            lim_time = crawl_href.find('dt', class_="").find('dt', class_='dt').text
            lim_time = datetime.datetime.strptime(year + lim_time, "%Y/%m/%d %H:%M")
        except AttributeError:
            lim_time = datetime.datetime.now()

        print("搜尋新聞連結中...，目前搜尋時間進度:", lim_time)
        if s_time > lim_time:
            break

        last_date = "12/31"

        for link in crawl_href.find_all('dt', class_=""):
            date_time = link.find('dt', class_='dt').text

            # 若上一篇文的時間為01/01，且這一篇篇為12/31，表示這是前一年的新聞，故將年份減一
            if last_date[0:5] == "01/01" and date_time[0:5] == "12/31":
                year = str(int(datetime.datetime.now().strftime("%Y")) - 1) + "/"
            last_date = date_time

            date_time = datetime.datetime.strptime(year + date_time, "%Y/%m/%d %H:%M")
            if e_time < date_time:
                continue
            if s_time > date_time:
                break
            all_links.append(link.find('h2').find('a').get('href'))
        time.sleep(1)

    all_links = sorted(set(all_links), key=all_links.index)
    print("搜尋連結完成，總連結數:", len(all_links))
    print("------------------------------------")
    return all_links


if __name__ == "__main__":
    start_time = "2019-06-25 18:01:00"
    end_time = "2019-06-25 19:00:00"
    category = 'all'
    links = get_urls(start_time, end_time, category)
    print("列出第一個結果:", links[0])

