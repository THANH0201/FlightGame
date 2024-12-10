from database import Database

db = Database()

class Team:
    def __init__(self, name):
        self.name = name

    def create_new(self, player_id):
        conn = db.get_conn()
        cursor = conn.cursor(dictionary=True)

        try:
            # Create the team and get its ID
            create_team_sql = '''
                        INSERT INTO team (name)
                        VALUES (%s)
                    '''
            cursor.execute(create_team_sql, (self.name,))
            team_id = cursor.lastrowid

            # Update team id info of player
            update_team_sql = '''
                                UPDATE player
                                SET team_id = %s
                                WHERE id = %s
                            '''
            cursor.execute(update_team_sql, (team_id, player_id))

            conn.commit()
            return team_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_available_teams():
        # Fetch all available teams
        available_teams_query = '''SELECT id, name FROM team ORDER BY name ASC'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(available_teams_query)
        result = cursor.fetchall()
        cursor.close()
        return result

    @staticmethod
    def get_team_members(team_id):
        sql = '''
                SELECT username, total_score, total_adventure
                FROM player
                WHERE team_id = %s
                ORDER BY total_score DESC, total_adventure DESC, username
            '''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (team_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
