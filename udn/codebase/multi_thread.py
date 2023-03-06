import threading
import time
from codebase.udn_contents import crawl_page


# Multi-threading
def thread_crawl_page(link, q):
    result = crawl_page(link)
    if result is not None:
        q.append(result)


def multi_crawling(all_links):
    count = 0
    threads = []
    list_results = []
    for l in all_links:
        t = threading.Thread(target=thread_crawl_page, args=[l, list_results])
        threads.append(t)
        t.start()
        count += 1
        if count % 60 == 0 or count == len(all_links):
            print("爬文進度:", count, "/", len(all_links))
            time.sleep(1)

    # 等待所有的子執行緒結束
    for t in threads:
        t.join()

    print("爬文完成，總爬文篇數:", count)
    print("------------------------------------")
    return list_results


if __name__ == '__main__':
    result = multi_crawling([
        'https://udn.com/news/story/7001/3880920',
        'https://udn.com/news/story/12639/3880918',
        'https://udn.com/news/story/120565/3880919',
        'https://udn.com/news/story/7268/3878809',
        'https://udn.com/news/story/7238/3880909',
        'https://udn.com/news/story/7321/3880910',
        'https://udn.com/news/story/6904/3875453',
        'https://udn.com/news/story/120570/3880906',
        'https://udn.com/news/story/120570/3880904'])
    print(result)
