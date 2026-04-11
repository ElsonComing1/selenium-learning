import pymysql

class Mysql_tool:
    def __init__(self,host:str='localhost',port:int=3306,user:str=None,password:str=None,db:str=None):
        self.conn=pymysql.connect(
            host=host,port=port,user=user,password=password,database=db,
            charset='utf8mb4',autocommit=False,
            cursorclass=pymysql.cursors.DictCursor
            )
        # autocommit用于测试时，手动提交，避免污染数据
        # pymysql.cursors.Dictcursor设置cursor的返回类型

if __name__=='__main__':
    mysql_item=Mysql_tool(host='localhost',port=3306,user='root',password='1234567',db='api_db_test')
    print(mysql_item,type(mysql_item),mysql_item.__class__)