## Flask API that connects to MYSQL database 
# Provides real-time environmental and seat ocuppancy data
# Retrives the latest environmental readings
# Retrives seat occupancy status from the chairs
# Two endpoints/urls,  /api/environment and /api/seats 

# Creates a web server that listens for HTTP requests
from flask import Flask, jsonify     # Converts Python dictionaries into JSON
from flask_cors import CORS          # To let WordPress access the API
import mysql.connector   
import os
         
app = Flask(__name__)
CORS(app)
# Creates the Flask application instance


def get_db_connection():
    host = os.environ.get("MYSQL_HOST")
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    database = os.environ.get("MYSQL_DATABASE")
    port = int(os.environ.get("MYSQL_PORT", 3306))  # padrão 3306 se não setado

    print(f"Conectando ao MySQL em {host}:{port} com usuário {user}")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )




# Fetching Environmental Data (/api/environment)
@app.route('/api/environment', methods=['GET']) # Defines a GET API endpoint
def get_environment_data():

    db = get_db_connection()                    # Connect to the database
    cursor = db.cursor(dictionary=True)         # Creates a cursor to interact with the database
    cursor.execute("""
        SELECT table_id, CO2, Temperature, Noise, update_time
        FROM Environment
        ORDER BY update_time DESC
        LIMIT 1
    """)
    row = cursor.fetchone() # Fetch the most recent data
    # Limit1 - only one row   ORDER BY update_time- latest entry
                        
    cursor.close()
    db.close()

    # If no data exists return a default JSON response
    if not row:
        row = {
            "table_id": 0,
            "CO2": 0.0,
            "Temperature": 0.0,
            "Noise": 0,
            "update_time": "N/A"
        }
    
    return jsonify(row) # Convert the data to JSON and return it




# Fetching Seat Occupancy Data (/api/seats)
@app.route('/api/seats', methods=['GET'])
def get_seat_data():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT chair_id, is_occupied FROM Chairs ORDER BY update_time DESC")
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    seat_data = {str(row["chair_id"]): ("occupied" if row["is_occupied"] else "available") for row in rows}

    return jsonify(seat_data)



if __name__ == "__main__":
    print("DEBUG: MYSQL_HOST =", os.environ.get("MYSQL_HOST"))
    print("DEBUG: MYSQL_USER =", os.environ.get("MYSQL_USER"))
    print("DEBUG: MYSQL_PASSWORD =", os.environ.get("MYSQL_PASSWORD"))
    print("DEBUG: MYSQL_DATABASE =", os.environ.get("MYSQL_DATABASE"))
    print("DEBUG: MYSQL_PORT =", os.environ.get("MYSQL_PORT"))
    port = int(os.environ.get("PORT", 5000))  # Railway define a porta no ambiente
    app.run(host="0.0.0.0", port=port, debug=True)
