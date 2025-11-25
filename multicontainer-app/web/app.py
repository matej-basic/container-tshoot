from flask import Flask
import os
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        cursor.close()
        conn.close()
        return "<h1>Connected to MySQL!</h1><p>Databases:</p>" + "<br>".join([db[0] for db in databases])
    except Exception as e:
        return f"<h1>Error connecting to MySQL</h1><pre>{e}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
