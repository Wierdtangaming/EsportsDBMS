from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Gatearray",
        database="esportsDBMS",
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/tournamentParticipation', methods=['GET'])
def get_tournament_participation():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM TOURNAMENT_PARTICIPATION")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/tournaments', methods=['GET'])
def get_tournaments():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM TOURNAMENTS")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Extract user data from request
    name = data.get('name')
    password = data.get('password')
    
    # Convert team_id to integer
    try:
        team_id = int(data.get('team_id'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid team_id format; it must be an integer"}), 400

    try:
        # Using get_db_connection() instead of mysql.connection for a proper connection
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Query the database using the converted team_id value
        cursor.execute(
            "SELECT * FROM LOGIN WHERE name = %s AND password = %s AND team_id = %s", 
            (name, password, team_id)
        )
        
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            # Adjusted key to login_id based on your schema
            return jsonify({"message": "Login successful", "login_id": user["login_id"]}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/players', methods=['GET'])
def get_players():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM PLAYERS")
        players = cursor.fetchall()
        return jsonify(players), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/loginData', methods=['GET'])
def get_login_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM LOGIN")
        login_data = cursor.fetchall()
        return jsonify(login_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/venues', methods=['GET'])
def get_venue_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM venues")
        login_data = cursor.fetchall()
        return jsonify(login_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/query', methods=['POST'])
def execute_query():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            return jsonify(result)
        else:
            connection.commit()
            return jsonify({"message": "Query executed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Extract data from request
    name = data.get("name")
    password = data.get("password")
    country = data.get("country")
    date_of_birth = data.get("date_of_birth")
    team_id = data.get("team_id")
    is_player = data.get("is_player")
    
    # Validate required fields
    if not all([name, password, country, date_of_birth, team_id]):
        return jsonify({"error": "All fields are required"}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Check if username already exists
        cursor.execute("SELECT * FROM LOGIN WHERE name = %s", (name,))
        if cursor.fetchone():
            return jsonify({"error": "Username already exists"}), 400
        
        # If registering as player, create player record first
        player_id = None
        if is_player:
            cursor.execute(
                "INSERT INTO PLAYERS (name, team_id, country, date_of_birth, rating) VALUES (%s, %s, %s, %s, %s)",
                (name, team_id, country, date_of_birth, 0)  # Default rating 0
            )
            connection.commit()
            
            # Get the auto-generated player_id
            cursor.execute("SELECT LAST_INSERT_ID() as player_id")
            player_id = cursor.fetchone()["player_id"]
        
        # Create login record
        cursor.execute(
            "INSERT INTO LOGIN (name, password, country, date_of_birth, team_id, player_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, password, country, date_of_birth, team_id, player_id)
        )
        connection.commit()
        
        return jsonify({"message": "Signup successful", "player_id": player_id})
    
    except Exception as e:
        # Rollback in case of error
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

@app.route('/teams/extra', methods=['GET'])
def get_teams_extra():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM TEAMS")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/teams', methods=['GET'])
def get_teams():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT team_id, name FROM TEAMS")
        teams = cursor.fetchall()
        return jsonify(teams)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



@app.route('/games', methods=['GET'])
def get_games():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM GAMES")
        games = cursor.fetchall()
        return jsonify(games)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

@app.route('/matches', methods=['GET'])
def get_matches():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM MATCHES")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/matchTeams', methods=['GET'])
def get_match_teams():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM MATCH_TEAMS")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/playerMatchStats', methods=['GET'])
def get_player_match_stats():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM PLAYER_MATCH_STATS")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/playerTeamHistory', methods=['GET'])
def get_player_team_history():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM PLAYER_TEAM_HISTORY")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)