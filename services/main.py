import json
import socket

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from FlightGame.services.player import Player
from database import Database

db = Database()

# Set timeout for long queries
socket.setdefaulttimeout(60)

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/continents')
def continents():
    sql = f'''SELECT DISTINCT continent
              FROM country'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return json.dumps(result)


@app.route('/countries/<continent>')
def countries_by_continent(continent):
    sql = f'''SELECT iso_country, name
              FROM country
              WHERE continent = %s'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (continent,))
    result = cursor.fetchall()
    return json.dumps(result)


@app.route('/airports/<country>')
def airports_by_country(country):
    sql = f'''SELECT ident, name, latitude_deg, longitude_deg
              FROM airport
              WHERE iso_country = %s'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (country,))
    result = cursor.fetchall()
    return json.dumps(result)


@app.route('/airport/<icao>')
def airport_by_icao(icao):
    sql = f'''SELECT name, latitude_deg, longitude_deg
              FROM airport
              WHERE ident=%s'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchone()
    return json.dumps(result)


@app.route('/register', methods=['POST'])
def register():
    try:
        # Get data from the form
        data = request.json
        username = data['username']
        password = data['password']
        continent = data['continent']
        country = data['country']
        start_location = data['airport']
        plane = data['plane']

        # Check if username already exists
        check_sql = '''SELECT 1 FROM player WHERE username = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(check_sql, (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400

        # Create a new player
        player = Player(username, password, continent, country, start_location, plane)
        player_id = player.create_new()

        return jsonify({'message': 'User registered successfully', 'player_id': player_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/player/<username>')
def get_player_by_username(username):
    return json.dumps(Player.get_player_by_username(username))


@app.route('/login', methods=['POST'])
def login():
    try:
        # Get data from the request
        data = request.json
        username = data['username']
        password = data['password']

        # Validate the input
        if not username or not password:
            return jsonify({'error': 'Username and password are required!'}), 400

        # Query to check if user exists
        user = Player.login(username, password)

        if not user:
            return jsonify({'error': 'Invalid username or password!'}), 401

        return jsonify({
            'message': 'Login successful',
            'player_id': user['id'],
            'username': username
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<int:player_id>', methods=['GET'])
def get_game_data(player_id):
    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    # Fetch player info
    player_sql = '''
        SELECT p.total_adventure, p.total_score, p.current_location, a.name AS current_airport
        FROM player p INNER JOIN airport a ON a.ident = p.current_location
        WHERE p.id = %s
    '''
    cursor.execute(player_sql, (player_id,))
    player_data = cursor.fetchone()

    # Fetch completed missions
    progress_query = '''
        SELECT pp.location, a.name, a.latitude_deg, a.longitude_deg, pp.status 
        FROM player_progress pp
        JOIN airport a ON a.ident = pp.location
        WHERE pp.player_id = %s
    '''
    cursor.execute(progress_query, (player_id,))
    missions = cursor.fetchall()

    return jsonify({
        'player': player_data,
        'missions': missions
    })


@app.route('/mission/<int:player_id>', methods=['GET'])
@cross_origin()
def get_next_mission(player_id):
    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check last mission status
        last_mission_sql = '''
            SELECT location, status, a.name, a.latitude_deg, a.longitude_deg
            FROM player_progress INNER JOIN airport a ON location = ident
            WHERE player_id = %s AND status <> 1
            ORDER BY location DESC LIMIT 1
        '''
        cursor.execute(last_mission_sql, (player_id,))
        last_mission = cursor.fetchone()

        if last_mission:  # Incomplete mission
            return jsonify(last_mission), 200

        # Generate a random location
        random_offset_query = '''
                SELECT a.ident, a.name, a.latitude_deg, a.longitude_deg
                FROM airport a INNER JOIN player p ON a.continent = p.continent AND a.iso_country = p.country
                WHERE a.ident NOT IN (
                    SELECT location FROM player_progress WHERE player_id = %s
                )
                ORDER BY RAND() LIMIT 1
            '''
        cursor.execute(random_offset_query, (player_id,))
        next_airport = cursor.fetchone()

        # Insert progress and update current location
        if next_airport:
            insert_progress = '''
                    INSERT INTO player_progress (player_id, location, score, status)
                    VALUES (%s, %s, 0, 0)
                '''
            cursor.execute(insert_progress, (player_id, next_airport['ident']))

            update_progress = '''
                    UPDATE player SET current_location = %s WHERE id = %s
                '''
            cursor.execute(update_progress, (next_airport['ident'], player_id))

        conn.commit()
        return jsonify(next_airport), 200

    except Exception as e:
        conn.rollback()  # Roll back the transaction on error
        return jsonify({"error": str(e)}), 500


@app.route('/complete-mission', methods=['POST'])
def update_progress():
    data = request.json
    player_id = data['player_id']
    score = data['score']
    location = data['location']
    mission_status = 1 if data['isPass'] else 2

    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Update player_progress status and score
        update_progress_sql = '''
            UPDATE player_progress
            SET score = %s, status = %s
            WHERE player_id = %s AND location = %s
        '''
        cursor.execute(update_progress_sql, (score, mission_status, player_id, location))

        if mission_status == 1:
            # Update total_score and total_adventure in player table
            update_player_sql = '''
                UPDATE player
                SET total_score = total_score + %s, total_adventure = total_adventure + 1
                WHERE id = %s
            '''
            cursor.execute(update_player_sql, (score, player_id))

            # Find the next available random location
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
                update_current_location_sql = '''
                    UPDATE player SET current_location = %s WHERE id = %s
                '''
                cursor.execute(update_current_location_sql, (next_airport['ident'], player_id))
            conn.commit()
            return jsonify({
                "message": "Mission completed",
                "next_airport": next_airport
            }), 200
        else:
            return jsonify({
                "message": "Mission failed"
            }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the top 10 players based on total_score
        leaderboard_sql = '''
            SELECT username, total_score, IFNULL(total_adventure, 0) AS total_adventure
            FROM player
            ORDER BY total_score DESC, total_adventure DESC
            LIMIT 5
        '''
        cursor.execute(leaderboard_sql)
        players = cursor.fetchall()

        return jsonify(players), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/my-team/<int:player_id>', methods=['GET'])
def get_my_team(player_id):
    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if player belongs to a team
        team_sql = '''
            SELECT t.id AS team_id, t.name AS team_name, p.username, p.total_score
            FROM team t INNER JOIN player p ON t.id = p.team_id
            WHERE p.id = %s
        '''
        cursor.execute(team_sql, (player_id,))
        team = cursor.fetchone()

        if not team:
            return jsonify({"message": "No team found"}), 200

        member_list_sql = '''
            SELECT username, total_score, total_adventure
            FROM player
            WHERE team_id = %s
            ORDER BY total_score DESC, total_adventure DESC, username
        '''
        cursor.execute(member_list_sql, (team['team_id'],))
        members = cursor.fetchall()

        return jsonify({
            "team": team,
            "members": members
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/join-team', methods=['POST'])
def join_team():
    data = request.json
    player_id = data['player_id']
    team_id = data['team_id']

    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Update team id info of player
        join_team_sql = '''
            UPDATE player
            SET team_id = %s
            WHERE id = %s
        '''
        cursor.execute(join_team_sql, (team_id, player_id))
        conn.commit()

        return jsonify({"message": "Successfully joined the team!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/create-team', methods=['POST'])
def create_new_team():
    data = request.json
    team_name = data['team_name']
    player_id = data['player_id']

    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Create the team and get its ID
        create_team_sql = '''
            INSERT INTO team (name)
            VALUES (%s)
        '''
        cursor.execute(create_team_sql, (team_name,))
        team_id = cursor.lastrowid

        # Update team id info of player
        update_team_sql = '''
                    UPDATE player
                    SET team_id = %s
                    WHERE id = %s
                '''
        cursor.execute(update_team_sql, (team_id, player_id))
        conn.commit()

        return jsonify({"message": "Team created successfully!", "team_id": team_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/teams', methods=['GET'])
def get_available_teams():
    conn = db.get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch all available teams
        available_teams_query = '''
            SELECT id, name
            FROM team
            ORDER BY name ASC
        '''
        cursor.execute(available_teams_query)
        teams = cursor.fetchall()

        return jsonify({"teams": teams}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(use_reloader=True, host='127.0.0.1', port=5000)

# inputs and prints are moved to web page
