from bs4 import BeautifulSoup
import requests
import pymysql
from datetime import datetime
import json
#from codebase.output import output_mysql
#from codebase.multi_thread import multi_crawling
import configparser
import re
import csv
import os,sys
import pandas as pd
import bs4
sys.path.append(os.getcwd())

from codebase.logger import setup_logger
#from codebase import database
from codebase.database import (
    getCurrentYear,
    getDataBaseConfig,
    dbConnect,
    check_database,
    check_table,
    get_last_date,
    insert_database,
    insert_database_,
    validate_content,
    )
from codebase.utils import (
    get_content_url,
    get_content,
    getHttpError,
    get_content_,
    )

from system_exception import (
    AbstractException,
    UnknownHttpError,
    ParseContentError,
    )


config = configparser.ConfigParser()
config.read("./codebase/config.ini", encoding="utf-8")

#取得config.ini["category"]["category_chi_list"]的values()
category = eval(config["category"]["category_chi_list"])
category_list = list(category.values())




if __name__ == "__main__":

    main_logger = setup_logger('first_logger', "./udn.log")
    host,user,password = getDataBaseConfig()
    count_saved = 0
    #connect to the DB
    try:
        connection = dbConnect(host=host,user=user,password=password)
    except AbstractException as e:
        main_logger.error(e)
          
        
    #s_time = get_last_date(connection,category_list)
    
    for catego in range(len(category_list)):
        #check the DB
        try:
            check_database(connection,category_list[catego])
        except Exception as e:
            main_logger.error(e)
            continue
        #step2: check the table
        try:
            check_table(connection,category_list[catego])
        except Exception as e:
            main_logger.error(e)
            continue
        #step3: get the last day of the category
        try:
            s_time = get_last_date(connection,category_list[catego])
        except Exception as e:
            main_logger.error(e)
            continue
    connection.close()

    #get the news url
    article_dict= get_content_url(s_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    url_list = article_dict['url_list']
    error_list = article_dict['error_list']
    if len(error_list)>1:

        for i in error_list:   
            main_logger.error(i)
     
            
    try:
        connection = dbConnect(host=host,user=user,password=password) 
    #parse news
        for url in url_list:
        #result_list = []
            try:
                result_dict = get_content(url)            
            except Exception as e:
                for err in e.args[0]:
                    main_logger.error(e)
                
            try:
                insert_database(connection,result_dict)
                count_saved += 1
            except Exception as e:
                for err in e.args[0]:
                    main_logger.error(e)
                
    except Exception as e:
        for err in e.args[0]:
            main_logger.error(e)
    
            
    
    main_logger.info(f"所有分類完成！共存入 {count_saved} 筆！")
    main_logger.info(
        f"-聯合- 更新筆數: {count_saved}, 完成時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
    )
     
    with open("udn.txt", "w", encoding='utf-8') as result_file:
        result_file.write(f"-聯合- 更新筆數: {count_saved}, 完成時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")

