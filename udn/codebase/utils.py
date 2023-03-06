from calendar import c
import calendar
from bs4 import BeautifulSoup
from bs4.element import NavigableString 
from datetime import datetime
import re
import time
import bs4
import requests
import glob
import urllib3
import configparser
import pandas as pd
import sys
import os
#sys.path.append(os.getcwd())
from NEWS_crawler.system_exception import *
import itertools
import json
#from requests_html import HTMLSession
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import TimeoutException
# import chromedriver_autoinstaller as chromedriver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


headers = {
    'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}

# =============================================================================
# config = configparser.ConfigParser()
# config.read("./config.ini", encoding="utf-8")
# 
# #取得config.ini["category"]["category_chi_list"]的values()
# category = eval(config["category_url"]["category_url_list"])
# =============================================================================
category_url_list = {
    'important':'&id=2&channelId=2&cateId=6638&last_page=20&type=rank&sort=newest',
    'sport':'&id=2&channelId=2&cateId=7227&last_page=550&type=rank&sort=newest',
    'global':'&id=2&channelId=2&cateId=7225&last_page=7&type=rank&sort=newest',
    'social':'&id=2&channelId=2&cateId=6639&last_page=7&type=rank&sort=newest',
    'produce':'&id=2&channelId=2&cateId=6644&last_page=17&type=rank&sort=newest',
    'stock':'&id=2&channelId=2&cateId=6645&last_page=26&type=rank&sort=newest',
    'life':'&id=2&channelId=2&cateId=6649&last_page=267&type=rank&sort=newest',
    'education':'&id=2&channelId=2&cateId=11195&last_page=341&type=rank&sort=newest',
    'comment':'&id=2&channelId=2&cateId=6643&last_page=25&type=rank&sort=newest',
    'local':'&id=2&channelId=2&cateId=6641&last_page=8&type=rank&sort=newest',
    'cntw':'&id=2&channelId=2&cateId=6640&last_page=13&type=rank&sort=newest',
    'digit':'&id=2&channelId=2&cateId=7226&last_page=154&type=rank&sort=newest',
    'travel':'&id=1013&channelId=2&cateId=0&last_page=1289&type=rank&sort=newest',
    'oops':'&id=2&channelId=2&cateId=120909&last_page=170&type=rank&sort=newest',
    'journal':'&id=1015&channelId=2&cateId=0&last_page=128&type=rank&sort=newest',
    }
category_list = list(category_url_list.keys())
api_list = list(category_url_list.values())

def getHttpError(status_code: int, url: str, category: str):
    """_summary_

    Args:
        status_code (int)
        url (str): request 的 url
        category (str): 版別

    Raises:
        status_dict: normal httpError
        UnknownHttpError: httpError
    """
    if status_code == 200:
        return
    status_dict = {
        400: HttpBadRequest("udn", url, category),
        401: HttpUnauthorized("udn", url, category),
        403: HttpForbidden("udn", url, category),
        404: HttpNotFound("udn", url, category),
        405: HttpMethodNotAllowed("udn", url, category),
        500: HttpInternalServerError("udn", url, category),
        503: HttpServiceUnavailable("udn", url, category),
    }
    if status_code in status_dict.keys():
        raise status_dict[status_code]
    elif status_code.status != 200:
        raise UnknownHttpError("udn", url, category, status_code)




def get_content_url_(s_time):
    
    
    url_list = []
    error_list = []
    
    for count in range(1, 30):
        
        url = "https://udn.com/api/more?page=" + str(count) + "&id=&channelId=1&cate_id=0&type=breaknews"
        href_resp = requests.get(url, headers=headers)
        
        
        try:
            # check response
            getHttpError(href_resp.status_code, url, count)
        except AbstractException as e:
            error_list.append(e)      
        try:
            crawl_href = json.loads(href_resp.content.decode('utf-8')) 
        except:
            error_list.append(ParseURLError("udn",url))
            continue
        
        if 'lists' not in crawl_href:
            break
        
        # 頁面第一篇的時間
        lim_time = datetime.strptime(crawl_href['lists'][0]['time']['date'], "%Y-%m-%d %H:%M")
        if datetime.strptime(s_time, "%Y%m%d %H%M%S") > lim_time:
        #if s_time > lim_time:
            break
        for link in crawl_href['lists']:
            if datetime.strptime(s_time, "%Y%m%d %H%M%S") > datetime.strptime(link['time']['date'], "%Y-%m-%d %H:%M"):
       
                break
            url_list.append("https://udn.com" + link['titleLink'].split("?")[0])
        

    return {'url_list': url_list, 'error_list': error_list}


def get_content_url(category: str,start_time):
    
    #start_time = start_time
    Time_stamp = True
    url_list = []
    error_list = []
    count = 1

    api = category_url_list.get(category)
      
    while(Time_stamp == True):
        url = "https://udn.com/api/more?page=" + str(count) + api
        href_resp = requests.get(url, headers=headers)
        
        
        try:
            # check response
            getHttpError(href_resp.status_code, url, count)
        except AbstractException as e:
            error_list.append(e)      
        try:
            crawl_href = json.loads(href_resp.content.decode('utf-8')) 
        except:
            error_list.append(ParseURLError("udn",url))
            continue
        
        if 'lists' not in crawl_href:
            break
        
        for link in crawl_href['lists']:
            url_list.append(link['titleLink'].split("?")[0])
            lim_time = datetime.strptime(link['time']['date'], "%Y-%m-%d %H:%M")
            #if lim_time < datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"):
            if lim_time < start_time:
                Time_stamp = False
                break
            #url_list.append(link['titleLink'].split("?")[0])
            #print("success")
        count = count + 1
        

    return {'url_list': url_list, 'error_list': error_list}
# =============================================================================
# def get_content_url(s_time):
#     
#     Time_stamp = True
#     url_list = []
#     error_list = []
#     count = 1
# 
#       
#     while(Time_stamp == True):
#         url = "https://udn.com/api/more?page=" + str(count) + "&id=&channelId=1&cate_id=0&type=breaknews"
#         href_resp = requests.get(url, headers=headers)
# 
#         
#         try:
#             # check response
#             getHttpError(href_resp.status_code, url, count)
#         except AbstractException as e:
#             error_list.append(e)      
#         try:
#             crawl_href = json.loads(href_resp.content.decode('utf-8')) 
#         except:
#             error_list.append(ParseURLError("udn",url))
#             continue
#         
#         if 'lists' not in crawl_href:
#             break
#         
#         for link in crawl_href['lists']:
#             lim_time = datetime.strptime(link['time']['date'], "%Y-%m-%d %H:%M")
#             if lim_time < datetime.strptime(s_time, "%Y%m%d %H%M%S"):
#                 Time_stamp = False
#                 #break
#             url_list.append("https://udn.com" + link['titleLink'].split("?")[0])
#             #print("success")
#         count = count + 1
#         
# 
#     return {'url_list': url_list, 'error_list': error_list}
# =============================================================================

        


def get_content_(url,category):
    result_list = []
    errors = []
    #category_for_test = "all"
    chi_class = "No"
 
    headers = {
        'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }
   
 
# 取得頁面的原始碼  # 参数：verify：Ture/False，默认是Ture，用于验证SSL证书开关
    try:
        response = requests.get(url=link, verify=False, headers = headers)
        
    except Exception as e:
        # recover 時須記錄做為回補資料所用
        error_df = pd.DataFrame(
            {
                "error": "HttpError",
                "date":datetime.now().strftime("%Y%m%d"),
                "url": link,
            },
            index=[0],
        )
        file = "./error_url.csv"
        error_df.to_csv(
            file,
            index=False,
            mode="a",
            header=not os.path.exists(file),
        )
        errors.append(e)
        raise Exception(errors)
        
    status_code = {
        400: HttpBadRequest("ct", link, chi_class),
        401: HttpUnauthorized("ct", link, chi_class),
        403: HttpForbidden("ct", link, chi_class),
        404: HttpNotFound("ct", link, chi_class),
        405: HttpMethodNotAllowed("ct", link, chi_class),
        500: HttpInternalServerError("ct", link, chi_class),
        503: HttpServiceUnavailable("ct", link, chi_class),
    }

    if response.status_code in status_code.keys():
        error_df = pd.DataFrame(
            {
                "error": "HttpError",
                "date":datetime.now().strftime("%Y%m%d"),
                "url": link,
            },
            index=[0],
        )
        file = "./error_url.csv"
        error_df.to_csv(
            file,
            index=False,
            mode="a",
            header=not os.path.exists(file),
        )
        errors.append(status_code[response.status_code])
        raise Exception(errors)
    else:                
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except:
            errors.append(ParseURLError("udn", error_url=link, content="article"))
        
        try:
            artUrl = next(soup.find('p').descendants)
            if type(artUrl) == bs4.element.Tag:
                artUrl = artUrl.string
                artUrl = artUrl.split('"')
                artUrl = artUrl[1]
                if artUrl in "opinion":
                    try:
                        soup = selenium_javascript(link)
                    except:
                        errors.append(ParseURLError("udn", error_url=link, content="article"))
                    # 去除圖片內容
                    try:
                        figure_soup = soup.figure.extract()
                    except:
                        pass
    
                    # title
                    try:
                        artTitle = soup.find('h1').text
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artTitle"))

                    # time
                    try:
                        artDate = soup.find_all('time')
                        
                        artDate = artDate[1].text + artDate[0].text 
                        
                        month = str(list(calendar.month_abbr).index(str(artDate[3:6])))
                        day = artDate[0:3]
                        year = str(getCurrentYear())
                        
                        artDate = year + "-" + month + "-" + day + artDate[12:]
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artDate"))

                    # class
                    try:
                        artCatagory = "opinion"
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artCatagory"))

                    # URL
                    artUrl = link
    
                    # All content
                    # artAllContent = soup
    
                    # Article content
                    artContent = ""
                    try:
                        #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                        sc  = soup.find_all('p')
                        for s in sc:
                            regex = re.compile("[\"\n\r\n]")
                            ss = regex.sub("", s.text)
                            artContent = artContent + ss
                        # 如果是要導去別的頁面的新聞，便不爬此則
                        # if "window.location.href" in artContent:
                        #     return None
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artContent"))
            
                    if errors:
                        # record ParseContentError
                        error_df = pd.DataFrame(
                            {
                                "error": "ParseContentError",
                                "date": datetime.now().strftime("%Y%m%d"),
                                "url": link,
                            },
                            index=[0],
                        )
                        file = "./error_url.csv"
                        error_df.to_csv(
                            file,
                            index=False,
                            mode="a",
                            header=not os.path.exists(file),
                        )
                        raise Exception(errors)     
        
                    result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}

                    return result
                    
                else:
                    try:
                        soup = selenium_javascript(link)
                    except:
                        errors.append(ParseURLError("udn", error_url=link, content="article"))
                    
                    # 去除圖片內容
                    try:
                        figure_soup = soup.figure.extract()
                    except:
                        pass
    
                    # title
                    try:
                        artTitle = soup.find('h1',{'class':'story_art_title'}).text
                        #artTitle = soup.find('h1').text
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artTitle"))

                    # time
                    try:
                        #artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
                        artDate = soup.find('div',{'class':'story_bady_info_author'}).text
                        artDate = artDate.split(" ")
                        artDate = artDate[0]
                        artDate = artDate.replace('/','-') + " 00:00:00"
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artDate"))

                    # class
                    try:
                        #clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
                        #artCatagory = clas[1].text
                        artCatagory = "international"

                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artCatagory"))

                    # URL
                    artUrl = link
    
                    # All content
                    # artAllContent = soup
    
                    # Article content
                    artContent = ""
                    try:
                        #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                        sc  = soup.find_all('p')
                        for s in sc:
                            regex = re.compile("[\"\n\r\n]")
                            ss = regex.sub("", s.text)
                            artContent = artContent + ss
                        # 如果是要導去別的頁面的新聞，便不爬此則
                        # if "window.location.href" in artContent:
                        #     return None
                    except:
                        errors.append(ParseContentError("udn", error_url=link, content="artContent"))
            
                    if errors:
                        # record ParseContentError
                        error_df = pd.DataFrame(
                            {
                                "error": "ParseContentError",
                                "date": datetime.now().strftime("%Y%m%d"),
                                "url": link,
                            },
                            index=[0],
                        )
                        file = "./error_url.csv"
                        error_df.to_csv(
                            file,
                            index=False,
                            mode="a",
                            header=not os.path.exists(file),
                        )
                        raise Exception(errors)     
        
                    result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}

                    return result
                    
            else:
                 # 去除圖片內容
                try:
                     figure_soup = soup.figure.extract()
                except:
                    pass
    
                # title
                try:
                    artTitle = soup.find('h1').text
                except:
                    errors.append(ParseContentError("udn", error_url=link, content="artTitle"))

                # time
                try:
                    artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
                except:
                    errors.append(ParseContentError("udn", error_url=link, content="artDate"))

                # class
                try:
                    clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
                    artCatagory = clas[1].text
                except:
                    errors.append(ParseContentError("udn", error_url=link, content="artCatagory"))

                # URL
                artUrl = link
    
                # All content
                # artAllContent = soup
    
                # Article content
                artContent = ""
                try:
                    sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                    for s in sc:
                        regex = re.compile("[\"\n\r\n]")
                        ss = regex.sub("", s.text)
                        artContent = artContent + ss
                # 如果是要導去別的頁面的新聞，便不爬此則
                # if "window.location.href" in artContent:
                #     return None
                except:
                    errors.append(ParseContentError("udn", error_url=link, content="artContent"))
            
                if errors:
                    # record ParseContentError
                    error_df = pd.DataFrame(
                        {
                            "error": "ParseContentError",
                            "date": datetime.now().strftime("%Y%m%d"),
                            "url": link,
                        },
                        index=[0],
                    )
                    file = "./error_url.csv"
                    error_df.to_csv(
                        file,
                        index=False,
                        mode="a",
                        header=not os.path.exists(file),
                    )
                    raise Exception(errors)     
        
                result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}

                return result
        except:
            errors.append(ParseContentError("udn", error_url=link, content="artTitle")) 
        



# def get_content(category:str, url:str):
#     result = {}
#     errors = []
#     # parse_error_url = []
#     # request_error_url = []
#     chi_class = category
 
#     headers = {
#         'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
#     }
   
#     #for url in urls:
#     # 取得頁面的原始碼  # 参数：verify：Ture/False，默认是Ture，用于验证SSL证书开关
#     try:
#         response = requests.get(url=url, verify=False, headers = headers)
        
#     except Exception as e:
#         print("requests error")
#         #request_error_url.append(UnknownHttpError("udn",url,category,"render error"))
#         #continue
#     try:
#         # check response
#         getHttpError(response.status_code, url, category)
#     except Exception as e:
#         print("getHttpError error")
#         #errors.append(e)
#         #continue
    
                
#     try:
#         soup = BeautifulSoup(response.text, "lxml")
#     except Exception as e:
#         print("BeautifulSoup error")
#         #errors.append(ParseContentError("udn", url, "html"))
#         #continue
        
#     try:
#         artUrl = next(soup.find('p').descendants)
#         artUrl = artUrl.string
#         if '\u4e00' <= artUrl <= '\u9fa5':
#             # 去除圖片內容
#             try:
#                 figure_soup = soup.figure.extract()
#             except Exception as e:
#                 pass
    
#             # title
#             try:
#                 artTitle = soup.find('h1').text
#             except Exception as e:
#                 errors.append(ParseContentError("udn", url, "artTitle"))
#                 #continue

#             # time
#             try:
#                 artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
#             except Exception as e:
#                 errors.append(ParseContentError("udn", url, "artDate"))
#                 #continue

#             # class
#             try:
#                 clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
#                 artCatagory = clas[1].text
#             except Exception as e:
#                 errors.append(ParseContentError("udn", url, "artCatagory"))
#                 #continue
#             # URL
#             artUrl = url

#             # Article content
#             artContent = ""
#             try:
#                 sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
#                 for s in sc:
#                     regex = re.compile("[\"\n\r\n]")
#                     ss = regex.sub("", s.text)
#                     artContent = artContent + ss

#             except Exception as e:
#                 errors.append(ParseContentError("udn", url, "artContent"))
#                 #continue

        
#             result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
#                 #result_list.append(result)
#                 #print(result)
#             # return result
            

#         else:
#             artUrl = artUrl.split('"')
#             artUrl = artUrl[1]
#             if artUrl in "opinion":
#                     try:
#                         response = requests.get(url=artUrl, verify=False, headers = headers)
                        
#                     except Exception as e:
#                         errors.append(UnknownHttpError("udn",url,category,"render error"))
#                         #continue
                    
#                     try:
#                         # check response
#                         getHttpError(response.status_code, url, category)
#                     except Exception as e:
#                         errors.append(e)
#                         #continue
                        
                                            
#                     try:
#                         soup = BeautifulSoup(response.text, "lxml")
#                     except Exception as e:
#                         errors.append(ParseContentError("udn", url, "html"))
#                         #continue
                    
#                     # 去除圖片內容
#                     try:
#                         figure_soup = soup.figure.extract()
#                     except Exception as e:
#                         pass
                    
#                     # title
#                     try:
#                         artTitle = soup.find('h1').text
#                     except Exception as e:
#                         errors.append(ParseContentError("udn", url, "artTitle"))
#                         #continue
                    
#                     # time
#                     try:
#                         artDate = soup.find_all('time')
                        
#                         artDate = artDate[1].text + artDate[0].text 
                        
#                         month = str(list(calendar.month_abbr).index(str(artDate[3:6])))
#                         day = artDate[0:3]
#                         year = str(getCurrentYear())
                        
#                         artDate = year + "-" + month + "-" + day + artDate[12:]
#                     except Exception as e:
#                         errors.append(ParseContentError("udn", url, "artDate"))
#                         #continue
                    
#                     # class
#                     try:
#                         artCatagory = "opinion"
#                     except Exception as e:
#                         errors.append(ParseContentError("udn", url, "artCatagory"))
#                         #continue
#                     # URL
#                     artUrl = url
                                    
#                     # Article content
#                     artContent = ""
#                     try:
#                         #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
#                         sc  = soup.find_all('p')
#                         for s in sc:
#                             regex = re.compile("[\"\n\r\n]")
#                             ss = regex.sub("", s.text)
#                             artContent = artContent + ss
#                         # 如果是要導去別的頁面的新聞，便不爬此則
#                         # if "window.location.href" in artContent:
#                         #     return None
#                     except Exception as e:
#                         errors.append(ParseContentError("udn", url, "artContent"))
#                         #continue
                            
    
                        
#                     result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
#                         #result_list.append(result)
#                         #print(result)
#                     # return result

#             else:
#                 try:
#                     response = requests.get(url=artUrl, verify=False, headers = headers)
                        
#                 except Exception as e:
#                     errors.append(UnknownHttpError("udn",url,category,"render error"))
#                     #continue
                
#                 try:
#                     # check response
#                     getHttpError(response.status_code, url, category)
#                 except Exception as e:
#                     errors.append(e)
#                     #continue                    
                                
#                 try:
#                     soup = BeautifulSoup(response.text, "lxml")
#                 except Exception as e:
#                     errors.append(ParseContentError("udn", url, "html"))
#                     #continue
                    
#                 # 去除圖片內容
#                 try:
#                     figure_soup = soup.figure.extract()
#                 except Exception as e:
#                     pass
                    
#                 # title
#                 try:
#                     artTitle = soup.find('h1',{'class':'story_art_title'}).text
#                     #artTitle = soup.find('h1').text
#                 except Exception as e:
#                     errors.append(ParseContentError("udn", url, "artTitle"))
#                     #continue
                
#                 # time
#                 try:
#                     #artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
#                     artDate = soup.find('div',{'class':'story_bady_info_author'}).text
#                     artDate = artDate.split(" ")
#                     artDate = artDate[0]
#                     artDate = artDate.replace('/','-') + " 00:00:00"
#                 except Exception as e:
#                     errors.append(ParseContentError("udn", url, "artDate"))
#                     #continue
                
#                 # class
#                 try:
#                     #clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
#                     #artCatagory = clas[1].text
#                     artCatagory = "international"

#                 except Exception as e:
#                     errors.append(ParseContentError("udn", url, "artCatagory"))
                
#                 # URL
#                 artUrl = url
                            
#                 # Article content
#                 artContent = ""
#                 try:
#                     #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
#                     sc  = soup.find_all('p')
#                     for s in sc:
#                         regex = re.compile("[\"\n\r\n]")
#                         ss = regex.sub("", s.text)
#                         artContent = artContent + ss
#                     # 如果是要導去別的頁面的新聞，便不爬此則
#                     # if "window.location.href" in artContent:
#                     #     return None
#                 except Exception as e:
#                     errors.append(ParseContentError("udn", url, "artContent"))
#                     #continue
                            
                        
#                 result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
#                         #result_list.append(result)
#                         #print(result)
#                 # return result
#     except StopIteration:
#         try:
#             figure_soup = soup.figure.extract()
#         except Exception as e:
#             pass

#         # title
#         try:
#             artTitle = soup.find('h1').text
#         except Exception as e:
#             errors.append(ParseContentError("udn", url, "artTitle"))
#             #continue

#         # time
#         try:
#             artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
#         except Exception as e:
#             errors.append(ParseContentError("udn", url, "artDate"))
#             #continue

#         # class
#         try:
#             clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
#             artCatagory = clas[1].text
#         except Exception as e:
#             errors.append(ParseContentError("udn", url, "artCatagory"))
#             #continue
#         # URL
#         artUrl = url

#         # Article content
#         artContent = ""
#         try:
#             sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
#             for s in sc:
#                 regex = re.compile("[\"\n\r\n]")
#                 ss = regex.sub("", s.text)
#                 artContent = artContent + ss

#         except Exception as e:
#             errors.append(ParseContentError("udn", url, "artContent"))
#             #continue

    
#         result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
#             #result_list.append(result)
#             #print(result)
#             # return result   
        
    
#     except Exception as e:
#         errors.append(ParseContentError("udn", url, "artUrl"))
#     if len(errors)>0:
#         raise Exception(errors)
#     else:
#         return result

def get_content(category:str, url:str):
    result = {}
    errors = []
    # parse_error_url = []
    # request_error_url = []
    chi_class = category
 
    headers = {
        'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }
   
    #for url in urls:
    # 取得頁面的原始碼  # 参数：verify：Ture/False，默认是Ture，用于验证SSL证书开关
    try:
        response = requests.get(url=url, verify=False, headers = headers)
        
    except Exception as e:
        #print("requests error")
        request_error_url.append(UnknownHttpError("udn",url,category,"render error"))
        #continue
    try:
        # check response
        getHttpError(response.status_code, url, category)
    except Exception as e:
        #print("getHttpError error")
        errors.append(e)
        #continue
    
                
    try:
        soup = BeautifulSoup(response.text, "lxml")
    except Exception as e:
        #print("BeautifulSoup error")
        errors.append(ParseContentError("udn", url, "html"))
        #continue
        
    try:
        artUrl = next(soup.find('p').descendants)
        artUrl = artUrl.string
        #if '\u4e00' <= artUrl <= '\u9fa5':
        if type(artUrl) is bs4.element.NavigableString or artUrl == None:
            # 去除圖片內容
            try:
                figure_soup = soup.figure.extract()
            except Exception as e:
                pass
    
            # title
            try:
                artTitle = soup.find('h1').text
            except Exception as e:
                errors.append(ParseContentError("udn", url, "artTitle"))
                #continue

            # time
            try:
                artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
            except Exception as e:
                errors.append(ParseContentError("udn", url, "artDate"))
                #continue

            # class
            try:
                clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
                artCatagory = clas[1].text
            except Exception as e:
                errors.append(ParseContentError("udn", url, "artCatagory"))
                #continue
            # URL
            artUrl = url

            # Article content
            artContent = ""
            try:
                sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                for s in sc:
                    regex = re.compile("[\"\n\r\n]")
                    ss = regex.sub("", s.text)
                    artContent = artContent + ss

            except Exception as e:
                errors.append(ParseContentError("udn", url, "artContent"))
                #continue

        
            result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
                #result_list.append(result)
                #print(result)
            # return result
            

        else:
            artUrl = artUrl.split('"')
            artUrl = artUrl[1]
            if "vpn" in artUrl:
                pass
            elif "opinion" in artUrl:
                    try:
                        response = requests.get(url=artUrl, verify=False, headers = headers)
                        
                    except Exception as e:
                        errors.append(UnknownHttpError("udn",url,category,"render error"))
                        #continue
                    
                    try:
                        # check response
                        getHttpError(response.status_code, url, category)
                    except Exception as e:
                        errors.append(e)
                        #continue
                        
                                            
                    try:
                        soup = BeautifulSoup(response.text, "lxml")
                    except Exception as e:
                        errors.append(ParseContentError("udn", url, "html"))
                        #continue
                    
                    # 去除圖片內容
                    try:
                        figure_soup = soup.figure.extract()
                    except Exception as e:
                        pass
                    
                    # title
                    try:
                        artTitle = soup.find('h1').text
                    except Exception as e:
                        errors.append(ParseContentError("udn", url, "artTitle"))
                        #continue
                    
                    # time
                    try:
                        artDate = soup.find_all('time')
                        
                        #artDate = artDate[1].text + artDate[0].text
                        artDate = artDate[0].text 
                        
                        month = str(list(calendar.month_abbr).index(str(artDate[3:6])))
                        day = artDate[0:3]
                        year = str(getCurrentYear())
                        
                        artDate = year + "-" + month + "-" + day + artDate[12:]
                    except Exception as e:
                        errors.append(ParseContentError("udn", url, "artDate"))
                        #continue
                    
                    # class
                    try:
                        artCatagory = "opinion"
                    except Exception as e:
                        errors.append(ParseContentError("udn", url, "artCatagory"))
                        #continue
                    # URL
                    artUrl = url
                                    
                    # Article content
                    artContent = ""
                    try:
                        #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                        sc  = soup.find_all('p')
                        for s in sc:
                            regex = re.compile("[\"\n\r\n]")
                            ss = regex.sub("", s.text)
                            artContent = artContent + ss
                        # 如果是要導去別的頁面的新聞，便不爬此則
                        # if "window.location.href" in artContent:
                        #     return None
                    except Exception as e:
                        errors.append(ParseContentError("udn", url, "artContent"))
                        #continue
                            
    
                        
                    result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
                        #result_list.append(result)
                        #print(result)
                    # return result

            else:
                try:
                    response = requests.get(url=artUrl, verify=False, headers = headers)
                        
                except Exception as e:
                    errors.append(UnknownHttpError("udn",url,category,"render error"))
                    #continue
                
                try:
                    # check response
                    getHttpError(response.status_code, url, category)
                except Exception as e:
                    errors.append(e)
                    #continue                    
                                
                try:
                    soup = BeautifulSoup(response.text, "lxml")
                except Exception as e:
                    errors.append(ParseContentError("udn", url, "html"))
                    #continue
                    
                # 去除圖片內容
                try:
                    figure_soup = soup.figure.extract()
                except Exception as e:
                    pass
                    
                # title
                try:
                    artTitle = soup.find('h1',{'class':'story_art_title'}).text
                    #artTitle = soup.find('h1').text
                except Exception as e:
                    errors.append(ParseContentError("udn", url, "artTitle"))
                    #continue
                
                # time
                try:
                    #artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
                    artDate = soup.find('div',{'class':'story_bady_info_author'}).text
                    artDate = artDate.split(" ")
                    artDate = artDate[0]
                    artDate = artDate.replace('/','-') + " 00:00:00"
                except Exception as e:
                    errors.append(ParseContentError("udn", url, "artDate"))
                    #continue
                
                # class
                try:
                    #clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
                    #artCatagory = clas[1].text
                    artCatagory = "international"

                except Exception as e:
                    errors.append(ParseContentError("udn", url, "artCatagory"))
                
                # URL
                artUrl = url
                            
                # Article content
                artContent = ""
                try:
                    #sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
                    sc  = soup.find_all('p')
                    for s in sc:
                        regex = re.compile("[\"\n\r\n]")
                        ss = regex.sub("", s.text)
                        artContent = artContent + ss
                    # 如果是要導去別的頁面的新聞，便不爬此則
                    # if "window.location.href" in artContent:
                    #     return None
                except Exception as e:
                    errors.append(ParseContentError("udn", url, "artContent"))
                    #continue
                            
                        
                result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
                        #result_list.append(result)
                        #print(result)
                # return result
    except StopIteration:
        try:
            figure_soup = soup.figure.extract()
        except Exception as e:
            pass

        # title
        try:
            artTitle = soup.find('h1').text
        except Exception as e:
            errors.append(ParseContentError("udn", url, "artTitle"))
            #continue

        # time
        try:
            artDate = soup.find('time', {'class': 'article-content__time'}).text + ":00"
        except Exception as e:
            errors.append(ParseContentError("udn", url, "artDate"))
            #continue

        # class
        try:
            clas = soup.find('nav', {'class': 'article-content__breadcrumb'}).find_all(['a'])
            artCatagory = clas[1].text
        except Exception as e:
            errors.append(ParseContentError("udn", url, "artCatagory"))
            #continue
        # URL
        artUrl = url

        # Article content
        artContent = ""
        try:
            sc = soup.find('section', {'class': 'article-content__editor'}).find_all('p')#art-content
            for s in sc:
                regex = re.compile("[\"\n\r\n]")
                ss = regex.sub("", s.text)
                artContent = artContent + ss

        except Exception as e:
            errors.append(ParseContentError("udn", url, "artContent"))
            #continue

    
        result = {'artTitle':artTitle, 'artUrl':artUrl, 'artDate':artDate, 'artCatagory':artCatagory, 'artContent':artContent}
            #result_list.append(result)
            #print(result)
            # return result   
        
    
    except Exception as e:
        errors.append(ParseContentError("udn", url, "artUrl"))
    if len(errors)>0:
        raise Exception(errors)
    else:
        return result

        
def recover_content_url(category:str, start_time):
    """_summary_

    Args:
        date (_type_): 要爬取的日期
    """
    
    return get_content_url(category=category,start_time=start_time)


def recover_content(category: str, url: str):
    """_summary_

    Args:
        url: 所要爬取文章的url

    Returns:
        _type_: {content,error_url}
    """
    return get_content(category=category,url=url)       