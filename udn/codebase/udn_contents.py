from bs4 import BeautifulSoup
import requests
import re
import urllib3
urllib3.disable_warnings()


def crawl_page(link):
    # 取得頁面的原始碼
    resp = requests.get(
        url=link,
        verify=False
    )
    # 確認有爬到東西
    if resp.status_code == requests.codes.ok:
        # 取得網頁的原始碼
        soup = BeautifulSoup(resp.text, "lxml")
    else:
        return None
    # 去除圖片內容
    try:
        figure_soup = soup.figure.extract()
    except:
        pass

    # title
    try:
        artTitle = soup.find('h1').text
    except:
        return None

    # time
    try:
        artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
    except:
        return None

    # class
    try:
        clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
        artCatagory = clas[1].text
        try:
            artSecondCategory = clas[2].text
        except:
            artSecondCategory = "Can't find it."
    except:
        return None

    # URL
    artUrl = link

    # All content
    # artAllContent = soup

    # Article content
    artContent = ""
    try:
        sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')
        for s in sc:
            regex = re.compile("[\"\n\r\n]")
            ss = regex.sub("", s.text)
            artContent = artContent + ss
        # 如果是要導去別的頁面的新聞，便不爬此則
        # if "window.location.href" in artContent:
        #     return None
    except:
        return None

    d = {"artTitle": artTitle, "artDate": artDate, "artCatagory": artCatagory,
         "artSecondCategory": artSecondCategory, "artUrl": artUrl, "artContent": artContent}
    return d


if __name__ == "__main__":
    url = "https://udn.com/news/story/6810/4358643?from=udn-ch1_breaknews-1-0-news"
    content = crawl_page(url)
    print(content)
