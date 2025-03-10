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

if __name__ == '__main__':
    app.run(debug=True, port=5000)