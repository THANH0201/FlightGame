# import mysql.connector
# db_connection = mysql.connector.connect(
#     host='localhost',
#     port=3306,
#     database='flightgame',
#     user='root',
#     password='ngoc',
#     autocommit=True
# )
from mysql.connector import Error

def getTaskByAirport(conn, airport):
    sql = f"SELECT id, task_name, task_description, task_answer, reward, penalty FROM task WHERE airport = '{airport}'"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")
