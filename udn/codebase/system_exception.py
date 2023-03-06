from pymongo import MongoClient
from datetime import datetime
import configparser

class AbstractException(Exception):
    "abstract system exception"
    def insert_to_mongodb(self):

        config = configparser.ConfigParser()
        config.read('config.ini')
        MongoDB = config["MongoDB"]["Database"]
        MongoUser = config["MongoDB"]["User"]
        MongoPW = config["MongoDB"]["PW"]
        MongoURL = config["MongoDB"]["URL"]
        Collection = config["MongoDB"]["Collection"]

        MongoURI = f"mongodb://{MongoUser}:{MongoPW}@{MongoURL}/{MongoDB}?authMechanism=SCRAM-SHA-1"

        with MongoClient(MongoURI) as client:
            db = client[MongoDB]
            data = dict()
            data['exception'] = self.__class__.__name__
            data['date'] = datetime.now()
            data.update(self.__dict__)
            db[Collection].insert_one(data)
        

    def __str__(self):
        self.insert_to_mongodb()
        tmp_text = ""
        for key, value in self.__dict__.items():
            tmp_text += f"{key}={value};"
        return tmp_text

class DatabaseConnectError(AbstractException):
    "Database connection exception"
    def  __init__(self, source, db_host, user):
        self.source = source
        self.db_host = db_host
        self.user = user
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+"message=MYSQL連線錯誤，請查看MYSQL主機是否有開啟"

class DatabaseNotExists(AbstractException):
    "Database not exists exception"
    def  __init__(self, source, db_name):
        self.source = source
        self.db_name = db_name
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.db_name}不存在於MYSQL中，請檢查是否有建立該DB"

class TableNotExists(AbstractException):
    "Table not exists exception"
    def  __init__(self, source, db_name, table_name):
        self.source = source
        self.db_name = db_name
        self.table_name = table_name
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.table_name}不存在於DB：{self.db_name}中，\
        請檢查是否有建立該TABLE"

class MissingField(AbstractException):
    "Missing field in the schema exception"
    def  __init__(self, source, error_url, miss_field, content):
        self.source = source
        self.miss_field = miss_field
        self.error_url = error_url
        self.content = content
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.error_url}的內容中缺乏{self.miss_field}必要欄位，\
        請確認欄位符合schema要求"


class MismatchDataType(AbstractException):
    "field type not match the schema exception"
    def  __init__(self, source, error_url, field, field_type , schema_data_type):
        self.source = source
        self.error_url = error_url
        self.field = field
        self.field_type = field_type
        self.schema_data_type = schema_data_type
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.field}\
            的資料型態為{self.field_type}，不符合schema要求應為{self.schema_data_type}，請確認資料型態符合schema要求"


class ExceedLimitLength(AbstractException):
    "field exceed the limit of the schema exception"
    def  __init__(self, source, error_url, field, field_length , schema_limit_length):
        self.source = source
        self.field = field
        self.error_url = error_url
        self.field_length = field_length
        self.schema_limit_length = schema_limit_length
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.field}\
        的字串長度為{self.field_length}，不符合schema要求長度應為{self.schema_limit_length}，將會進行裁減長度以符合schema限制"

class InsertDataFailed(AbstractException):
    "Insert data failed exception"
    def  __init__(self, source, error_sql):
        self.source = source
        self.error_sql = error_sql
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=執行SQL失敗，SQL：{self.error_sql}"

class ParseURLError(AbstractException):
    "parse url error exception"
    def  __init__(self, source, error_url, category, post_data=None):
        self.source = source
        self.error_url = error_url
        self.category = category
        self.post_data = post_data
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=解析URL欄位失敗，該網站可能改版"

class ParseContentError(AbstractException):
    "parse content error exception"
    def  __init__(self, source, error_url, content, post_data=None):
        self.source = source
        self.error_url = error_url
        self.content = content
        self.post_data = post_data
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.error_url}解析內容錯誤，無法從中解析出欄位"

class ParseCommentError(AbstractException):
    "parse comment error exception"
    def  __init__(self, source, error_url, comment, post_data=None):
        self.source = source
        self.error_url = error_url
        self.comment = comment
        self.post_data = post_data
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message={self.error_url}解析內容錯誤，無法從中解析出欄位"

class HttpBadRequest(AbstractException):
    "http status code 400 Bad Request"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，可能無回應或被阻擋，請檢查URL是否正確或稍後再嘗試存取"

class HttpUnauthorized(AbstractException):
    "http status code 401 Unauthorized"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，伺服器拒絕處理請求，需要認證資訊，可能已經被禁止ip訪問"

class HttpForbidden(AbstractException):
    "http status code 403 Forbidden"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，伺服器拒絕處理請求，請稍候嘗試存取"

class HttpNotFound(AbstractException):
    "http status code 404 Not Found"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，可能無回應或被阻擋，請檢查URL是否正確或稍後再嘗試存取"

class HttpMethodNotAllowed(AbstractException):
    "http status code 405 Method Not Allowed"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，請求方法已經改變，請改用POST或GET嘗試存取"

class HttpInternalServerError(AbstractException):
    "http status code 500 Internal Server Error"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，請求的伺服器發生內部錯誤，請稍候再進行存取"

class HttpServiceUnavailable(AbstractException):
    "http status code 503 Service Unavailable"
    def  __init__(self, source, error_url, category):
        self.source = source
        self.error_url = error_url
        self.category = category
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，請求的伺服器忙碌中，請稍候再進行存取"

class UnknownHttpError(AbstractException):
    "http status code which do not include above"
    def  __init__(self, source, error_url, category, http_code):
        self.source = source
        self.error_url = error_url
        self.category = category
        self.http_code = http_code
    def __str__(self):
        tmp_text = super().__str__()
        return tmp_text+f"message=請求{self.error_url}失敗，得到未知的錯誤。"