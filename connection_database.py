import MySQLdb

# LOCAL_HOST
IP_HOST = "192.168.1.57"
NAME_DB = "db_wikipedia"
USER = "marco"
PWD = ""


class Connection:

    def __init__(self):
        self.db = MySQLdb.connect(host=IP_HOST, user=USER, passwd=PWD, db=NAME_DB)
        self.cursor = self.db.cursor()

    def get_cursor():
        return self.cursor

    def query_request(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.db.close()
