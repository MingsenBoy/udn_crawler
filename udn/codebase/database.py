import pymysql
from datetime import datetime
from itertools import chain
import configparser
import json

from NEWS_crawler.system_exception import *
from NEWS_crawler.udn.codebase.logger import setup_logger

# In[]
def getValData():
    # 取得資料表長度及型別

    config = configparser.ConfigParser()
    config.read("./NEWS_crawler/udn/codebase/config.ini", encoding="utf-8")
    title_len = eval(config['val_data']['artTitle'])[1]
    title_type = eval(config['val_data']['artTitle'])[0]
    url_len = eval(config['val_data']['artUrl'])[1]
    url_type = eval(config['val_data']['artUrl'])[0]

    content_len = eval(config['val_data']['artContent'])[1]
    content_type = eval(config['val_data']['artContent'])[0]
    date_len = eval(config['val_data']['artDate'])[1]
    date_type = eval(config['val_data']['artDate'])[0]
    category_len = eval(config['val_data']['artCatagory'])[1]
    category_type = eval(config['val_data']['artCatagory'])[0]



    return title_len,title_type,url_len,url_type,content_len,content_type,date_len,date_type,category_len,category_type

def getCurrentYear():
    #取得現在年份

    currentDateTime = datetime.now()
    date = currentDateTime.date()

    return date.year

def getDataBaseConfig():
    #取得資料庫的連線資訊
    config = configparser.ConfigParser()
    config.read("./NEWS_crawler/udn/codebase/config.ini", encoding="utf-8")
    
    host = config['database']['host']
    user = config['database']['user']
    password = config['database']['password']
    return host,user,password
        
#connect to DB without the DB name
def dbConnect(host,user,password):
    """連到資料庫

    Args:
        host (str): 
        user (str): 
        password (str): 

    Raises:
        DatabaseConnectError: cannot connect the db

    Returns:
        _type_: the obj of pymysql.connect
    """
    try:
        connection = pymysql.connect(host=host, user=user, password=password)
    
    except:
        raise DatabaseConnectError("udn_crawler_op_mysql",host,user)
    
    return connection

def check_database(connection:pymysql.connect,category:str):
    """確認資料庫的存在，是以單個category

    Args:
        connection (pymysql.connect): the obj of pymysql.connect
        category (str): 版別

    Raises:
        e: 執行“SHOW DATABASES” 錯誤

    Returns:
        _type_: True
    """
    db_name= 'crawler_udn_' + category
    
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
    #如果不存在，就建立一個
    #check whether the db of the category exists
    if db_name not in db_list:
        print(DatabaseNotExists("use crawler_udn_",db_name))
        # mysql_create_database(connection,category)
        try:

            mysql_create_database(connection,category)
        except:
            raise

    return True
    
    
def check_table(connection:pymysql.connect,category , year=str(getCurrentYear())):
    
    """確認資料表的存在，是以單個category

    Args:
        connection (pymysql.connect): the obj of pymysql.connect
        category (_type_): 版別
        year (_type_, optional): 現在時間的年份 Defaults to str(getCurrentYear()).

    Raises:
        e: 執行“"use crawler_apple_”、“SHOW TABLES”時，有錯

    Returns:
        _type_: True
    """
    table_name = category + "_" + str(year)
    table_list = []
    
    with connection.cursor() as cursor:
        
        try:
            cursor.execute("use crawler_udn_" + category)
            cursor.execute("SHOW TABLES")
            # fet = cursor.fetchall()
            for k in cursor.fetchall():
                table_list.append(k[0])
            cursor.close()
        except pymysql.Error as e:
            raise e
    # connection.close()
    #check whether the table of category exists
    if table_name not in table_list:
        #print(TableNotExists("udn_crawler_op_mysql",category,table_name))
        # mysql_create_table(connection,category)
        try:
            mysql_create_table(connection,category)
        except:
            raise 
        
    return True
 
def mysql_create_table(connection:pymysql.connect,category,year=str(getCurrentYear())):
    
    """建立新資料表

    Args:
        connection (pymysql.connect): the obj of pymysql.connect
        category (_type_): 版別
        year (_type_, optional): 現在時間的年份. Defaults to str(getCurrentYear()).

    Raises:
        e: 建立資料表失敗
    """

    with connection.cursor() as cursor:
        try:
                
            cursor.execute("use crawler_udn_" + category)

        except pymysql.Error as e:
                
            raise e
        
        try:
            
            title_len,title_type,url_len,url_type,content_len,content_type,date_len,date_type,category_len,category_type = getValData()
            cursor.execute(f"CREATE TABLE  {category+'_'+year}"
                        f"(artTitle			{title_type}({title_len})	NOT NULL,"
                        f"artDate				{date_type}		NOT NULL,"
                        f"artCatagory	{category_type}({category_len})	NOT NULL,"
                        f"artUrl				{url_type}({url_len})	NOT NULL,"
                        f"artContent			{content_type}		NOT NULL,"
                        "PRIMARY KEY (artUrl))")
        except pymysql.Error as e:
            raise(e)
        cursor.close()

      

def mysql_create_database(connection:pymysql.connect,category):
    """建立資料庫

    Args:
        connection (pymysql.connect): the obj of pymysql.connect
        category (_type_): 新的版別

    Raises:
        e: 建立資料庫失敗
    """

    db_name='crawler_udn_' + category


    with connection.cursor() as cursor:
        db_name='crawler_udn_' + category
        try:
            cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
        except pymysql.Error as e:
            raise e
        
        cursor.close()

def validate_content(dict_result: dict) -> bool:
    # validate

    # limit = {
    #     "artUrl": json.loads(config["VALIDATION"]["artUrl"])[1],
    #     "artCatagory": json.loads(config["VALIDATION"]["artCatagory"])[1],
    #     "artTitle": json.loads(config["VALIDATION"]["artTitle"])[1],
    # }
    
    limit = {
        "artUrl": 100,
        "artCatagory": 5,
        "artTitle": 255,
        "artContent":16777215
    }

    def is_str(x: str):
        return isinstance(x, str)

    def valid_date(str_date: str):
        try:
            datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
            return True
        except:
            return False

    check = []
    errors = []
    # 缺欄位
    field = ["artUrl", "artCatagory", "artTitle", "artDate", "artContent"]
    for f in field:
        if f not in dict_result.keys():
            errors.append(
                MissingField(
                    "udn",
                    error_url=dict_result["artUrl"],
                    miss_field=f,
                    content=dict_result["artCatagory"],
                )
            )
            check.append(False)
        else:
            check.append(True)

    # 長度不符
    for k, v in limit.items():
        if not len(dict_result[k]) < v:
            errors.append(
                ExceedLimitLength(
                    source="udn",
                    error_url=dict_result["artUrl"],
                    field=k,
                    field_length=len(dict_result[k]),
                    schema_limit_length=v,
                )
            )
            check.append(False)

        check.append(len(dict_result[k]) < v)

    # 日期不符
    if not valid_date(dict_result["artDate"]):
        errors.append(
            MismatchDataType(
                source="udn",
                error_url=dict_result["artUrl"],
                field="artDate",
                field_type=type(dict_result["artDate"]),
                schema_data_type=str,
            )
        )
    check.append(valid_date(dict_result["artDate"]))

    # 形態不符
    for k, v in dict_result.items():
        if not is_str(v):
            errors.append(
                MismatchDataType(
                    source="udn",
                    error_url=dict_result["artUrl"],
                    field=k,
                    field_type=type(v),
                    schema_data_type=str,
                )
            )
        check.append(is_str(v))
    if errors:
        raise Exception(errors)

    return all(check)



    return title_len,title_type,url_len,url_type,content_len,content_type,date_len,date_type,category_len,category_type


# =============================================================================
# def get_last_date(connection:pymysql.connect,category_list,year=str(getCurrentYear())):
#     """得到資料的最新日期
# 
#     Args:
#         connection (pymysql.connect): the obj of pymysql.connect
#         category_list (_type_): 版別清單
#         year (_type_, optional): 現在時間的年份. Defaults to str(getCurrentYear()).
# 
#     Raises:
#         e: 執行“use crawler_apple_”、“SELECT MAX(`artDate`) FROM”時，有誤
# 
#     Returns:
#         _type_: 離最近現在最近一筆新聞的時間
#     """
#     date=None
#     
#     with connection.cursor() as cursor:
#         # get the last time by executing "SELECT MAX(`artDate`)..."
#         last_time = datetime(2021, 1, 1)
#         for category in category_list:
#             try:
#                 cursor.execute("use crawler_udn_" + category)
#                 for year in range(2021, datetime.now().year+1): 
#                     cursor.execute(f"SELECT MAX(`artDate`) FROM {'`'+category+'_'+str(getCurrentYear())+'`'}")
#                     date=cursor.fetchone()[0]
#                     if date is None or isinstance(date, str):
#                         continue
#                     if date > last_time:
#                         last_time = date
#             except pymysql.Error as e:
#                 raise e
#         cursor.close()
#     if date == None:
#         date = datetime(getCurrentYear(),1,1)
#     return date
# =============================================================================

def get_last_date(connection:pymysql.connect,category,year=str(getCurrentYear())):
    """得到資料的最新日期

    Args:
        connection (pymysql.connect): the obj of pymysql.connect
        category (_type_): 版別
        year (_type_, optional): 現在時間的年份. Defaults to str(getCurrentYear()).

    Raises:
        e: 執行“use crawler_apple_”、“SELECT MAX(`artDate`) FROM”時，有誤

    Returns:
        _type_: 離最近現在最近一筆新聞的時間
    """
    date=None
    
    with connection.cursor() as cursor:
        # get the last time by executing "SELECT MAX(`artDate`)..."
        try:
            cursor.execute("use crawler_udn_" + category)
            cursor.execute(f"SELECT MAX(`artDate`) FROM {'`'+category+'_'+str(getCurrentYear())+'`'}")
            date=cursor.fetchone()[0]
        except pymysql.Error as e:
            raise e
        cursor.close()
        if date == None:
            date = datetime(getCurrentYear(),1,1)
    return date


def validate_content(dict_result: dict) -> bool:
    """確傳入的新聞, 是否資料庫各欄位限制

    Args:
        dict_result (dict): 一篇新聞

    Raises:
        Exception: 記錄各類不符合限制的錯誤。包含 MissingField 缺欄位,
          ExceedLimitLength 長度過長, MismatchDataType 日期格式不符或非 str 型別

    Returns:
        bool: True 代表傳入的文章符合資料庫各欄位限制
    """
# =============================================================================
#     limit = {
#         "artUrl": json.loads(config["VALIDATION"]["artUrl"])["length"],
#         "class": json.loads(config["VALIDATION"]["class"])["length"],
#         "artTitle": json.loads(config["VALIDATION"]["artTitle"])["length"],
#         "artContent": json.loads(config["VALIDATION"]["artContent"])["length"],
#     }
# =============================================================================

    limit = {
        "artUrl": 100,
        "artCatagory": 5,
        "artTitle": 255,
        "artContent":16777215
    }

    def is_str(x: str):
        return isinstance(x, str)

    def valid_date(str_date: str):
        try:
            datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
            return True
        except:
            return False

    check = []
    errors = []
    # 缺欄位
    field = ["artUrl", "artCatagory", "artTitle", "artDate", "artContent"]
    for f in field:
        if f not in dict_result.keys():
            errors.append(
                MissingField(
                    "udn",
                    error_url=dict_result["artUrl"],
                    miss_field=f,
                    content=dict_result["artCatagory"],
                )
            )
            check.append(False)
        else:
            check.append(True)

    # 長度不符
    for k, v in limit.items():
        if not len(dict_result[k]) < v:
            errors.append(
                ExceedLimitLength(
                    source="udn",
                    error_url=dict_result["artUrl"],
                    field=k,
                    field_length=len(dict_result[k]),
                    schema_limit_length=v,
                )
            )
            check.append(False)

        check.append(len(dict_result[k]) < v)

    # 日期不符
    if not valid_date(dict_result["artDate"]):
        errors.append(
            MismatchDataType(
                source="udn",
                error_url=dict_result["artUrl"],
                field="artDate",
                field_type=type(dict_result["artDate"]),
                schema_data_type=str,
            )
        )
    check.append(valid_date(dict_result["artDate"]))

    # 形態不符
    for k, v in dict_result.items():
        if not is_str(v):
            errors.append(
                MismatchDataType(
                    source="udn",
                    error_url=dict_result["artUrl"],
                    field=k,
                    field_type=type(v),
                    schema_data_type=str,
                )
            )
        check.append(is_str(v))
    if errors:
        raise Exception(errors)

    return all(check)



    
def insert_database_(
    connection:pymysql.connect,
    result_dict,
):
    """將新聞寫入至該版別該年份的 table

    Args:
        db (pymysql.connect): 與 host 的連線
        result_dict (dict): 欲寫入的新聞

    Raises:
        Exception: 記錄 pymysql 執行時的錯誤, 以及自定義的寫入失敗錯誤 InsertDataFailed

    Returns:
        bool: 若寫入成功, 回傳 True
    """
    
    all_count = 0
    
    for dictResult in result_dict:
        year = dictResult['artDate'][0:4]
        placeholders = '", "'.join(dictResult.values())
        columns = ', '.join(dictResult.keys())
        try:
            category = category_list_dic[dictResult["artCatagory"]]
        # 沒出現在分類中則歸為 other 類
        except KeyError:
            category = 'other'
        # 檢查是否有該年份資料表
        table_name = category + "_" + year
# =============================================================================
#         if table_name not in table_list:
#             mysql_create_table(connection, category, table_name)
# =============================================================================

        categoryResult[category].append("REPLACE INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, '"' + placeholders + '"'))
        
    for categoryName in categoryResult:
        if len(categoryResult[categoryName]) > 0:
            count = 0
            host,user,password = getDataBaseConfig()
            try:
                connection = dbConnect(host=host,user=user,password=password)
            except AbstractException as e:
                main_logger.error(e)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("use crawler_udn_" + categoryName)
                    for dictResult in categoryResult[categoryName]:
                        cursor.execute(dictResult)
                        count += 1
                        all_count += 1
                connection.commit()
            except InsertDataFailed as e:
                main_logger.error(e)
                continue
            except Exception as e:
                for er in e.args[0]:
                    main_logger.error(er)
                continue
# =============================================================================
#             except Exception as e:
#                 # 方便找出錯誤
#                 print(e)
# =============================================================================
            finally:
                print("存入'crawler_udn_" + categoryName + "'資料庫，筆數:", count)
    connection.close()
    print('總存入筆數:', all_count)
    print('------------------------------------')
    return all_count
        

def insert_database(
    connection: pymysql.connect,
    one_data: dict,
    category:str,
):  
  
    
# =============================================================================
#     category_list_dic = {
#      "要聞": 'important',
#      "運動": 'sport',
#      "全球": 'global',
#      "社會": 'social',
#      "產經": 'produce',
#      "股市": 'stock',
#      "生活": 'life',
#      "文教": 'education',
#      "評論": 'comment',
#      "地方": 'local',
#      "兩岸": 'cntw',
#      "數位": 'digit',
#      "閱讀": 'read',
#      "Can't find it.": 'other'
#      }
# =============================================================================

# =============================================================================
#     try:
#         category = category_list_dic[result_dict["artCatagory"]]
#     # 沒出現在分類中則歸為 other 類
#     except KeyError:
#         category = 'other'
# =============================================================================
    # 存進MySQL
    if validate_content(one_data):
        cursor = connection.cursor()
        cursor.execute("use crawler_udn_" + category)
        cursor = connection.cursor()
        placeholders = "', '".join(one_data.values())
        year = datetime.strptime(one_data["artDate"], "%Y-%m-%d %H:%M:%S").year
        sql_replace = f"REPLACE INTO {category}_{year}\
                        (artTitle,artUrl,artDate,artCatagory,artContent)\
                        VALUES ('{placeholders}')"
        try:
            cursor.execute(sql_replace)
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            raise Exception([e, InsertDataFailed(source="udn", error_sql=sql_replace)])

        finally:
            cursor.close()
        