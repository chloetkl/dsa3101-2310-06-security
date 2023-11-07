<<<<<<< HEAD
from flask import Flask, request, send_file, render_template

=======
from flask import Flask
import mysql.connector
import bcrypt
from back_end.database.populate import add_user, check_auth
>>>>>>> d00846954874a39f01f5d4be11d882adc0967496

app = Flask(__name__)

        
@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

<<<<<<< HEAD
@app.route("/prediction")
def send_p():
    return send_file("back/data/test.png")
=======
@app.route("/add_user", methods = ["POST"])
def add_user(email, username, role_id, password):
    email = request.args.get('email')
    username = request.args.get('username')
    role_id = request.args.get('role_id')
    password = request.args.get('password')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password, salt)

    db = establish_sql_connection()
    cursor = db.cursor
    query = f"\
        INSERT INTO Users\
        (email, username, role_id, salt, hash)\
        VALUES ('{email}', '{username}', {role_id}, '{salt}', '{hash}')"
>>>>>>> d00846954874a39f01f5d4be11d882adc0967496

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
