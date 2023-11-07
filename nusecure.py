from flask import Flask, request, send_file, render_template
from back.models.sarima.fit_sarima_model import fit_sarima_model

import mysql.connector
import bcrypt
from back_end.database.populate import add_user, check_auth

app = Flask(__name__)


@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

@app.route("/prediction")
def send_p():
    return send_file("back/data/test.png")

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

@app.route("/fit_sarima")
def fit_sarima():
    fit_sarima_model()
    return "sarima pkl added in container"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
