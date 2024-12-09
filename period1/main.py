from enum import Enum

import airport
import plane
import player
import story
import mysql.connector

db_connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='flightgame',
    user='root',
    password='ngoc',
    autocommit=True
)

# GAME SETTINGS
class GameStatus(Enum):
    IN_PROGRESS = 1
    EXIT = 2
    FAIL = 3
    WIN = 4

class TaskStatus(Enum):
    NOT_START = 0
    COMPLETED = 1
    FAILED = 2


GAME_STATUS = GameStatus.IN_PROGRESS
# maximum score to win
MAX_SCORE = 500

def user_win(score):
    return score >= MAX_SCORE

def do_task(tasks):
    print("Below is your tasks, you need to complete them. Good luck!")
    i = 1
    for task in tasks:
        if task['task_type'] != 1:
            print(f"{i} - {task['task_name']}: {task['task_description']}")
            answer = input('Your answer: ')
            if answer.casefold() == task['task_answer'].casefold():
                player.updatePlayerTask(db_connection, user['id'], task['id'], task['reward'],
                                        TaskStatus.COMPLETED.value)
                new_score = user['score'] + task['reward']
                print(f"Well done! You earned a reward {task['reward']} points.")
            else:
                player.updatePlayerTask(db_connection, user['id'], task['id'], 0 - task['penalty'],
                                        TaskStatus.FAILED.value)
                new_score = user['score'] - task['penalty']
                print(f"Incorrect! You lose {task['penalty']} points.")
                print(f"Hints: The correct answer is {task['task_answer']}")
        else: # Refill energy
            player_plane = plane.getPlaneById(db_connection, user['plane'])
            print(f"{i} - {task['task_name']}: -{player_plane['consume_energy']}")
            if user['score'] < player_plane['consume_energy']:
                return GameStatus.FAIL
            new_score = user['score'] - player_plane['consume_energy']
            player.updatePlayerTask(db_connection, user['id'], task['id'], new_score, TaskStatus.COMPLETED.value)

        print(f"Your total score is {new_score}.")
        user['score'] = new_score
        player.updatePlayerScore(db_connection, user['id'], new_score)

        if user_win(new_score):
            return GameStatus.WIN
        else:
            continue_game = input("Do you want to continue the game? (Y/N): ")
            if continue_game.lower() != 'y':
                return GameStatus.EXIT
        i += 1
    return GameStatus.IN_PROGRESS

try:
    # Game starts
    # Ask to show the story
    storyDialog = input("Do you want to read the background story? (Y/N): ")
    if storyDialog.lower() == 'y':
        # print wrapped string line by line
        for line in story.getStory():
            print(line)

    # start input
    print("When you are ready to start, ")
    username = input("type your username: ")

    # check if user exists?
    user = player.getPlayerByUsername(db_connection, username)
    if not user: # User not exist
        # Ask user choose plane type
        print("Which type of plane do you want to use?")
        plane_types = plane.getAllPlaneTypes(db_connection)
        # print all type of plane
        if len(plane_types) > 0:
            for row in plane_types:
                print(f"{row['id']}. {row['plane_type']} - {row['description']}")
        plane_type = input('Your plane type: ')

        # Ask user choose plane
        print("Which plane do you want to use?")
        plane_list = plane.getAllPlanesByType(db_connection, plane_type)
        if len(plane_list) > 0:
            for row in plane_list:
                print(f"{row['plane_id']} - {row['plane_name']} - {row['plane_color']} - {row['consume_energy']}")
        plane_id = input("Your plane: ")

        # Ask user choose airport
        print("Where do you want to start your journey?")
        airport_list = airport.getAllAirportByPlane(db_connection, plane_id)
        if len(airport_list) > 0:
            for row in airport_list:
                print(f"{row['ident']} - {row['name']} - {row['iso_country']}")
        airport_ident = input("Your airport: ").upper()

        initial_score = airport.getInitialScoreByPlaneAndAirport(db_connection, plane_id, airport_ident)

        # Add new record to database (player)
        user_id = player.createNew(db_connection, username, airport_ident, plane_id, initial_score)
        player.assignTask(db_connection, user_id, airport_ident)
        user = player.getPlayerByUsername(db_connection, username)
    else:
        print("Welcome back!")
        print("Your current score is", user['score'])

    # GAME LOOP
    while GAME_STATUS == GameStatus.IN_PROGRESS:
        if user_win(user['score']):
            GAME_STATUS = GameStatus.WIN
            break
        else:
            current_tasks = player.getPlayerIncompletedTasks(db_connection, user['id'])
            if len(current_tasks) == 0:
                airport_list = airport.getNextAirportByPlayer(db_connection, user['id'])
                if len(airport_list) == 0:
                    print("You completed all the journey. No where to go now.")
                    GAME_STATUS = GameStatus.EXIT
                    break
                else:
                    for row in airport_list:
                        print(f"{row['ident']} - {row['name']} - {row['iso_country']}")
                    next_airport = input("Choose your next airport: ")
                    user['location'] = next_airport
                    print("Your journey continues!")

                    # Update player location and assign tasks
                    player.updatePlayerLocation(db_connection, user['id'], next_airport)
                    player.assignTask(db_connection, user['id'], next_airport)

                    current_tasks = player.getPlayerIncompletedTasks(db_connection, user['id'])
                    if len(current_tasks) > 0:
                        GAME_STATUS = do_task(current_tasks)
                    else:
                        print("Currently there is no task in this place.")
                        GAME_STATUS = GameStatus.EXIT
            else:
                GAME_STATUS = do_task(current_tasks)

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    db_connection.close()

# if loop stops
# show game result
if GAME_STATUS == GameStatus.WIN:
    print("Congratulations! You've reached the maximum score and completed the game.")
elif GAME_STATUS == GameStatus.FAIL:
    print("You don't have enough energy to continue. Game over!")
elif GAME_STATUS == GameStatus.EXIT:
    print("Game exited. See you next time!")
