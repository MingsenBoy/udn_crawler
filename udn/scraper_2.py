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
    )

from system_exception import (
    AbstractException,
    UnknownHttpError,
    ParseContentError,
    InsertDataFailed,
    )


config = configparser.ConfigParser()
config.read("./codebase/config.ini", encoding="utf-8")

#取得config.ini["category"]["category_chi_list"]的values()
category = eval(config["category_url"]["category_url_list"])
category_list = list(category.keys())
api_list = list(category.values())
# In[]


if __name__ == '__main__':
    main_logger = setup_logger('first_logger', "./udn.log")
    host,user,password = getDataBaseConfig()
    count_saved = 0
    
    try:
        connection = dbConnect(host=host,user=user,password=password)
    except AbstractException as e:
        main_logger.error(e)
    
    total_count=0    
    for catego in range(len(category_list)):
        #step1: check the DB
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
        #step4: get the news url
        article_dict= get_content_url(api_list[catego],s_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        url_list = article_dict['url_list']
        error_list = article_dict['error_list']
        if len(error_list)>1:

            for i in error_list:   
                main_logger.error(i)
                
        # step5: parse news
        content_dict = get_content(category_list[catego],url_list)
        result = content_dict['results']
        parse_content_error = content_dict['parse_content_error']
        request_content_error = content_dict['request_content_error']
        with open("./udn/error_url_both.csv",'a',newline='') as file:
            writer = csv.writer(file)
            for i in parse_content_error:
                main_logger.error(i)
                writer.writerow(["parse_Url",category_list[catego],i.error_url])
            for i in request_content_error:
                main_logger.error(i)
                writer.writerow(["request_Url",category_list[catego],i.error_url])
        
        # step6: insert the data
        count = 0
        for k in result:
            try:
                insert_database(connection,k,category_list[catego])
            except InsertDataFailed as e:
                main_logger.error(e)
                continue
            except Exception as e:
                for er in e.args[0]:
                    main_logger.error(er)
                continue
            count+=1
        print(category_list[catego]+'的存入筆數:', count)
        print('------------------------------------')
        total_count += count
        
    connection.close()
    
    main_logger.info(f"所有分類完成！共存入 {total_count} 筆！")
    main_logger.info(
        f"-聯合- 更新筆數: {total_count}, 完成時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
    )
     
    with open("udn.txt", "w", encoding='utf-8') as result_file:
        result_file.write(f"-聯合- 更新筆數: {total_count}, 完成時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")