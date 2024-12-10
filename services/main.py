import json
import socket

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from FlightGame.services.player import Player, PlayerProgress
from FlightGame.services.team import Team
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
        id = Player.get_player_by_username(username)
        if id:
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
    player_data = Player.get_player_by_id(player_id)
    missions = Player.get_all_missions(player_id)
    return jsonify({
        'player': player_data,
        'missions': missions
    })


@app.route('/mission/<int:player_id>', methods=['GET'])
@cross_origin()
def get_next_mission(player_id):
    try:
        # Check last mission status
        last_mission = Player.get_incomplete_mission(player_id)
        if last_mission:  # Incomplete mission
            return jsonify(last_mission), 200

        next_airport = Player.next_mission(player_id)
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

    try:
        # Update player_progress status and score
        player_progress = PlayerProgress(location, score, mission_status)
        player_progress.update(player_id)

        if mission_status == 1:
            # Update total_score, total_adventure in player table. Assign new mission (random airport)
            Player.update(player_id, score)
            next_airport = Player.next_mission(player_id)

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
    try:
        players = Player.get_leaderboard()
        return jsonify(players), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/my-team/<int:player_id>', methods=['GET'])
def get_my_team(player_id):
    try:
        team = Player.get_player_team(player_id)
        if not team:
            return jsonify({"message": "No team found"}), 200

        members = Team.get_team_members(team['team_id'])
        return jsonify({
            "team": team,
            "members": members
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/join-team', methods=['POST'])
def join_team():
    try:
        data = request.json
        player_id = data['player_id']
        team_id = data['team_id']
        Player.update_team_info(player_id, team_id)
        return jsonify({"message": "Successfully joined the team!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/create-team', methods=['POST'])
def create_new_team():
    try:
        data = request.json
        team_name = data['team_name']
        player_id = data['player_id']

        # Create a new team and update player info
        team = Team(team_name)
        team_id = team.create_new(player_id)
        return jsonify({"message": "Team created successfully!", "team_id": team_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/teams', methods=['GET'])
def get_available_teams():
    try:
        teams = Team.get_available_teams()
        return jsonify({"teams": teams}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(use_reloader=True, host='127.0.0.1', port=5000)

# inputs and prints are moved to web page
