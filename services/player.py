from enum import Enum
from database import Database

db = Database()

class TaskStatus(Enum):
    NOT_START = 0
    COMPLETED = 1
    FAILED = 2


class PlayerProgress:
    def __init__(self, location, score, status):
        self.location = location
        self.score = score
        self.status = status


class Player:
    def __init__(self, username, password, continent, country, start_location, plane):
        self.username = username
        self.password = password
        self.continent = continent
        self.country = country
        self.start_location = start_location
        self.current_location = start_location
        self.plane = plane
        self.progress = []
        self.progress.append(PlayerProgress(start_location, 0, TaskStatus.NOT_START))
        self.total_score = 0
        self.total_adventure = 0

    def get_player_progress(self):
        return self.progress

    # Method to insert new player to the database
    def create_new(self):
        player_sql = '''INSERT INTO player (username, password, continent, country, start_location, current_location, plane, total_score, total_adventure)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        progress_sql = '''INSERT INTO player_progress (player_id, location, score, status)
                          VALUES (%s, %s, %s, %s)'''

        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)

        try:
            # Insert player and get player_id
            cursor.execute(player_sql, (
                self.username, self.password, self.continent, self.country,
                self.start_location, self.start_location, self.plane, self.total_score, self.total_adventure
            ))
            player_id = cursor.lastrowid

            # Insert progress for the player
            cursor.execute(progress_sql, (
                player_id, self.start_location, 0, TaskStatus.NOT_START.value
            ))

            # Commit transaction
            conn.commit()
            return player_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    # Method to check if a username exists in the database
    @staticmethod
    def get_player_by_username(username):
        sql = '''SELECT id FROM player WHERE username = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        cursor.close()
        return result

    # Method to login
    @staticmethod
    def login(username, password):
        sql = '''SELECT id FROM player WHERE username = %s AND password = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (username, password))
        result = cursor.fetchone()
        cursor.close()
        return result
