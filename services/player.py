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

    def update(self, player_id):
        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = '''UPDATE player_progress SET score = %s, status = %s WHERE player_id = %s AND location = %s'''
            cursor.execute(sql, (self.score, self.status, player_id, self.location))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


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

    # Method to update player info to the database
    @staticmethod
    def update(player_id, score):
        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)

        try:
            # Update total_score and total_adventure in player table
            sql = '''
                UPDATE player
                SET total_score = total_score + %s, total_adventure = total_adventure + 1
                WHERE id = %s
            '''
            cursor.execute(sql, (score, player_id))
            conn.commit()
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

    # Method to get player information by id
    @staticmethod
    def get_player_by_id(player_id):
        sql = '''
                SELECT p.total_adventure, p.total_score, p.current_location, a.name AS current_airport
                FROM player p INNER JOIN airport a ON a.ident = p.current_location
                WHERE p.id = %s
            '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    # Method to get all missions of a player
    @staticmethod
    def get_all_missions(player_id):
        sql = '''
            SELECT pp.location, a.name, a.latitude_deg, a.longitude_deg, pp.status 
            FROM player_progress pp INNER JOIN airport a ON a.ident = pp.location
            WHERE pp.player_id = %s
        '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (player_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    # Method to get current mission of a player
    @staticmethod
    def get_incomplete_mission(player_id):
        sql = '''
            SELECT location, status, a.name, a.latitude_deg, a.longitude_deg
            FROM player_progress INNER JOIN airport a ON location = ident
            WHERE player_id = %s AND status <> 1
            ORDER BY location DESC LIMIT 1
        '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @staticmethod
    def next_mission(player_id):
        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)

        try:
            next_mission_sql = '''
                SELECT a.ident, a.name, a.latitude_deg, a.longitude_deg
                FROM airport a INNER JOIN player p ON a.continent = p.continent AND a.iso_country = p.country
                WHERE a.ident NOT IN (
                    SELECT location FROM player_progress WHERE player_id = %s
                )
                ORDER BY RAND() LIMIT 1
            '''
            cursor.execute(next_mission_sql, (player_id,))
            next_airport = cursor.fetchone()

            if next_airport:
                # Insert new mission into player_progress
                insert_next_mission_sql = '''
                    INSERT INTO player_progress (player_id, location, score, status)
                    VALUES (%s, %s, 0, 0)
                '''
                cursor.execute(insert_next_mission_sql, (player_id, next_airport['ident']))

                # Update player's current location
                update_current_location_sql = '''UPDATE player SET current_location = %s WHERE id = %s'''
                cursor.execute(update_current_location_sql, (next_airport['ident'], player_id))
                conn.commit()

            return next_airport
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    # Method to update team info of a player
    @staticmethod
    def update_team_info(player_id, team_id):
        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = '''UPDATE player SET team_id = %s WHERE id = %s'''
            cursor.execute(sql, (team_id, player_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    # Method to get team info of a player
    @staticmethod
    def get_player_team(player_id):
        # Check if player belongs to a team
        sql = '''
            SELECT t.id AS team_id, t.name AS team_name, p.username, p.total_score
            FROM team t INNER JOIN player p ON t.id = p.team_id
            WHERE p.id = %s
        '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    # Method to get top 5 players based on total_score
    @staticmethod
    def get_leaderboard():
        sql = '''
            SELECT username, total_score, IFNULL(total_adventure, 0) AS total_adventure
            FROM player
            ORDER BY total_score DESC, total_adventure DESC
            LIMIT 5
        '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result