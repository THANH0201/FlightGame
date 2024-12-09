# import mysql.connector
#
# db_connection = mysql.connector.connect(
#     host='localhost',
#     port=3306,
#     database='flightgame',
#     user='root',
#     password='ngoc',
#     autocommit=True
# )
from mysql.connector import Error

def getAllAirportByPlaneAndUser(conn, plane_id, player_id):
    if not player_id:
        sql = f"SELECT ident, name, iso_country FROM airport, airport_plane WHERE airport.ident = airport_plane.airport AND plane_id = '{plane_id}'"
    else:
        sql = (f"SELECT ident, name, iso_country "
               f"FROM airport, airport_plane "
               f"WHERE airport.ident = airport_plane.airport "
               f"AND plane_id = (SELECT plane FROM player WHERE id = {player_id})"
               f"AND airport.ident NOT IN ("
               f"SELECT airport FROM task, player_task WHERE task.id = player_task.task_id AND player_id = {player_id})")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def getAllAirportByPlane(conn, plane_id):
    return getAllAirportByPlaneAndUser(conn, plane_id, None)

def getInitialScoreByPlaneAndAirport(conn, plane_id, airport_ident):
    sql = f"SELECT initial_score FROM airport_plane WHERE airport = '{airport_ident}' AND plane_id = '{plane_id}'"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        if cursor.rowcount > 0:
            score = result['initial_score']
        else:
            score = 0
        cursor.close()
        return score
    except Error as err:
        print(f"Error: ' {err}'")

def getNextAirportByPlayer(conn, player_id):
    return getAllAirportByPlaneAndUser(conn, None, player_id)

# Testing
# airport = getAllAirportByPlane(db_connection, '001')
# if len(airport) > 0:
#     for row in airport:
#         print(f"{row['ident']} - {row['name']} - {row['iso_country']}")
#
# score = getInitialScoreByPlaneAndAirport(db_connection, '001', '00A')
# print(score)