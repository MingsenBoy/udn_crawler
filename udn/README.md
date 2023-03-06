# UDN_Scraper_Module
聯合報爬蟲模組

以下分為兩個部分，更新爬蟲與基本爬蟲：
+ **更新爬蟲**(auto_udn_scraper.py): 會自動檢查MySQL資料庫中最新一篇新聞的時間，並以此時間為開始，爬至執行當下的所有新聞存入資料庫中。
+ **基本爬蟲**(udn_scraper.py): 為更新爬蟲程式的基礎，可以多種方式匯出所爬到的資料。

## 資料來源
<a href="https://udn.com/news/index">UDN聯合新聞網</a>

## 更新爬蟲(auto_udn_scraper.py)

### 使用方式與參數

此程式自動檢查MySQL資料庫中最新一篇新聞的時間，並以此時間為起始將到執行當下的新聞爬下來存至資料庫中。

此程式無需要輸入的參數。
+ 若需要更改資料庫設定，請將 udn/auto_udn_scraper.py 中的 check_last_time() 函式與 udn/codebase/output.py 中的 output_mysql() 函式中更改。

## 基本爬蟲(udn_scraper.py)

### 使用方式與參數

此程式用來爬取UDN聯合新聞網的新聞之文字資料。

使用者依下述要求格式輸入時間區間、新聞類型與輸出方式，即可取得該時間區間內的所有新聞。

參數共有以下八個，只有start_time(-st)為必填，括號()內為縮寫：
+ **start_time(-st)**: (起始時間，格式為"YYYY-mm-dd HH:MM:SS"，選填，預設為"2014-01-01 00:00:00")
    > 因為來源資料中最舊的一篇為"2014-12-17"，故使用預設值會將所有可爬到之新聞爬入。
+ **end_time(-et)**: (結束時間，格式為"YYYY-mm-dd HH:MM:SS"，選填，預設為當下時間)
+ **category(-cg)**: (新聞類型分為以下13類，選填，預設為:"all")
    + important: 要聞
    + sport: 運動
    + global: 全球
    + social: 社會
    + produce: 產經
    + stock: 股市
    + life: 生活
    + education: 文教
    + comment: 評論
    + local: 地方
    + cn-tw: 兩岸
    + digit: 數位
    + read: 閱讀
+ **output(-op)**: (輸出方式，有 mysql, mongo 與 csv 可以選擇，選填，預設為:"mysql")
+ **path(-pt)**: (csv匯出後要儲存的位置，選填，預設為:"output/")
+ **mongoURI(-mgu)**: (存入 MongoDB 的 URI，選填，預設為:"mongodb://localhost:27017/")
+ **mongodb(-mgd)**: (存入 MongoDB 的 database，選填，預設為:"udn")
+ **mongocol(-mgc)**: (存入 MongoDB 的 collection，選填，預設為:"all")

### 輸出方式與欄位

共可選擇三種輸出方式：MySQL、MongoDB、CSV，預設為MySQL。
+ **MySQL**: 可以存入Lab的爬蟲資料庫(host="140.117.69.136"、user="crawler"、password="lab_30241#")，並依照所爬到的新聞類型與年份，分別存進不同分類的資料庫與不同年份的資料表中。
    > 若需要更改請至 udn/codebase/output.py 中的 output_mysql 函式中更改。另外，創建資料表的SQL式在 udn/codebase/mysql_create_table.sql 中。
+ **MongoDB**: 可按照社定的URI、Database、Collection，將資料存入mongoDB。
+ **CSV**: 可以按照指定的路徑匯出，檔名為「UDN_開始日期_結束日期.csv」。

依照設定的輸出格式，主程式會進行不同的函式：
+ udn_crawler_op_mysql(start_time, end_time, category)。
+ udn_crawler_op_mongo(start_time, end_time, category, path)。
+ udn_crawler_op_csv(start_time, end_time, category, mongoURI, mongodb, mongocol)。

共有以下六個輸出欄位：
+ artTitle: 新聞標題。
+ artDate: 發佈時間。
+ artCatagory: 新聞第一層分類，例:運動。
+ artSecondCategory: 新聞第二層分類，例:籃球、棒球。
+ artUrl: 新聞網址。
+ artContent: 新聞內文。

### 使用範例

若是要爬「2019年6月4日中午12點」至「2019年6月4日下午1點」的聯合新聞網的「全部」新聞，存入「MySQL」中，可在terminal下：
```
python udn_scraper.py --start_time="2019-06-04 12:00:00" --end_time="2019-06-04 13:00:00" --category="all" 
--output="mysql"
```
若是要爬「2019年6月4日中午12點」至「2019年6月4日下午1點」的聯合新聞網的「全部」新聞，透過「csv」匯出至「output」資料夾中，可在terminal下：
```
python udn_scraper.py --start_time="2019-06-04 12:00:00" --end_time="2019-06-04 13:00:00" --category="all" 
--output="csv" --path="output/"
```
若是要爬「2019年6月4日中午12點」至「2019年6月4日下午1點」的聯合新聞網的「全部」新聞，存入「MongoDB」中，
存入的URI為"mongodb://localhost:27017/"，存入的database為"udn"，存入的collection為"all"，可在terminal下：
```
python udn_scraper.py --start_time="2019-06-04 12:00:00" --end_time="2019-06-04 13:00:00" --category="all" 
--output="mongo" --mongoURI="mongodb://localhost:27017/" --mongodb="udn" --mongocol="all"
```
也可以透過縮寫的方式在terminal下：
```
python udn_scraper.py -st="2019-06-04 12:00:00" -et="2019-06-04 13:00:00" -cg="all" -op="mongo" 
-mgu="mongodb://localhost:27017/" -mgd="udn" -mgc="all"
```

### 使用上的限制與可能遭遇的問題

1. 因為聯合新聞網站方會將一段時間前的新聞，除了文教、生活、閱讀、數位、運動等類型以外的新聞做刪除，
所以離現在越久以前的新聞量會越少，所以若是要找一週以前的資料，新聞量會比昨天或今天的少很多。
2. 因為在網站頁面撈取新聞連結時，會從今天開始往過去搜尋，所以若設定的時間區間在距離現在24小時以前，會花較長時間。
    + 爬過去一個小時的新聞並匯出成csv，大約需花費30秒。
    + 爬過去一天的新聞並匯出成csv，大約需花費3分30秒。

### 需要預先安裝之套件

+ json
+ bs4
+ lxml
    > lxml是一個BeautifulSoup的解析器，根據官方文件，解析速度較快，另外若使用 html.parser 解析器會出現錯誤。
+ requests
+ pymysql
+ pymongo

