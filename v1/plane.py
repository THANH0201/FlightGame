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

def getAllPlaneTypes(conn):
    sql = f"SELECT id, plane_type, description FROM plane_type"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def getAllPlanesByType(conn, type):
    sql = f"SELECT plane_id, plane_name, plane_color, consume_energy FROM plane WHERE plane_type = {type}"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def getPlaneById(conn, plane_id):
    sql = f"SELECT plane_id, plane_name, plane_color, consume_energy FROM plane WHERE plane_id = {plane_id}"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

# Testing
# plane_types = getAllPlaneTypes(db_connection)
# # print all type of plane
# if len(plane_types) > 0:
#     for row in plane_types:
#         print(f"{row['id']}. {row['plane_type']} - {row['description']}")

# plane_list = getAllPlanesByType(db_connection, 1)
# if len(plane_list) > 0:
#     for row in plane_list:
#         print(f"{row['plane_id']} - {row['plane_name']} - {row['plane_color']} - {row['consume_energy']}")

# plane = getPlaneById(db_connection, '001')
# print(f"{plane['consume_energy']}")



