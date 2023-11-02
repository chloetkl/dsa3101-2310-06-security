from flask import Flask
import mysql.connector

app = Flask(__name__)

def establish_sql_connection():
    db = mysql.connector.connect(
        host = "database_1", #this is what the container was called when i did docker compose up so i just put that name here first
        user = "user",
        password = "dsa3101",
        database = "db"
        )
    return db
        
@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

@app.route("/add_user", methods = ["POST"])
def add_user(username, role, password):

    
    db = establish_sql_connection()
    cursor = db.cursor
    query = 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
