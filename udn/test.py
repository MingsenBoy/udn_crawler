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
        db_name= 'crawler_udn_' + category_list[catego]
        db_list=[]
        #拿到所有的資料庫名稱
        with connection.cursor() as cursor:
            #get all db name
            try:
                cursor.execute("SHOW DATABASES")
                # db_list = cursor.fetchall()
                for i in cursor.fetchall():
                    db_list.append(i[0])
            except pymysql.Error as e:
                raise e
        cursor.close()
        
        if db_name not in db_list:
        #print(TableNotExists("udn_crawler_op_mysql",category,table_name))
        # mysql_create_table(connection,category)
            try:
                print(db_name)
            except:
                raise
                
            db_name='crawler_udn_' + category_list[catego]
    
    
            with connection.cursor() as cursor:
                db_name='crawler_udn_' + category_list[catego]
                try:
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    connection.commit()
                except pymysql.Error as e:
                    raise e
            
                cursor.close()