from mysql.connector import Error
# import mysql.connector
# db_connection = mysql.connector.connect(
#     host='localhost',
#     port=3306,
#     database='flightgame',
#     user='root',
#     password='ngoc',
#     autocommit=True
# )

def getPlayerByUsername(conn, username):
    sql = f"SELECT id, user_name, location, plane, score FROM player WHERE user_name = %s;"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def createNew(conn, username, location, plane, score):
    sql = "INSERT INTO player (user_name, location, plane, score) VALUES (%s, %s, %s, %s);"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (username, location, plane, score))
        result = cursor.lastrowid
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def getTaskByAirport(conn, airport):
    sql = f"SELECT id, task_name, task_description, task_answer, reward, penalty FROM task WHERE airport = %s;"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (airport,))
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def assignTask(conn, user_id, airport):
    task_list = getTaskByAirport(conn, airport)
    cursor = conn.cursor(dictionary=True)
    try:
        for task in task_list:
            sql = "INSERT INTO player_task (player_id, task_id, score, status) VALUES (%s, %s, 0, 0);"
            cursor.execute(sql, (user_id, task['id']))
        cursor.close()
    except Error as err:
        print(f"Error: ' {err}'")

def getPlayerIncompletedTasks(conn, user_id):
    sql = f"SELECT id, user_name, location, plane, score FROM player WHERE id = %s"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()

        sql = f'''SELECT id, task_name, task_description, task_answer, task_type, reward, penalty 
            FROM task, player_task 
            WHERE task.id = player_task.task_id AND player_id = %s AND airport = %s AND status = 0'''
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (user_id, user['location']))
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        print(f"Error: ' {err}'")

def updatePlayerLocation(conn, user_id, new_location):
    sql = f"UPDATE player SET location = %s WHERE id = %s"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (new_location, user_id))
        cursor.close()
    except Error as err:
        print(f"Error: ' {err}'")

def updatePlayerTask(conn, user_id, task_id, score, status):
    sql = f"UPDATE player_task SET score = %s, status = %s WHERE player_id = %s AND task_id = %s"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (score, status, user_id, task_id))
        cursor.close()
    except Error as err:
        print(f"Error: ' {err}'")

def updatePlayerScore(conn, user_id, new_score):
    sql = f"UPDATE player SET score = %s WHERE id = %s"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (new_score, user_id))
        cursor.close()
    except Error as err:
        print(f"Error: ' {err}'")

# Testing
# a = getUserByUsername(db_connection, 'a')
# if not a:
#     print('not found')
# print('user found', a['score'])

# a = getPlayerIncompletedTasks(db_connection, 1)
# if len(a) > 0:
#     for row in a:
#         print(f"{row['id']}. {row['task_name']} - {row['task_description']}")
