import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='flightgame_v2',
            user='root',
            password='ngoc',
            autocommit=True
        )

    def get_conn(self):
        return self.conn
