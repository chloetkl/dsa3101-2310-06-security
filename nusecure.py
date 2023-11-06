## UNUSED, go to main > testing

from flask import Flask, render_template
import mysql.connector
import bcrypt
import pandas as pd

#add functions from other files 
#from back.database.populate.defaults import add_user, authenticate

app = Flask(__name__)

        
@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

data = pd.read_csv('back/data/data_v0.4(front).csv')
@app.route('/security')
def index():
    # Get column names from the DataFrame
    columns = data.columns.tolist()
    # Pass column names and data to the template
    return render_template('project-success/2. security_page/index.html', columns=columns, data=data.values.tolist())

if __name__ == '__main__':
    app.run(debug=True)

# @app.route("/add_user", methods = ["POST"])
# def add_user(email, username, role_id, password):
#     email = request.args.get('email')
#     username = request.args.get('username')
#     role_id = request.args.get('role_id')
#     password = request.args.get('password')
#     salt = bcrypt.gensalt()
#     hash = bcrypt.hashpw(password, salt)

#     db = establish_sql_connection()
#     cursor = db.cursor
#     query = f"\
#         INSERT INTO Users\
#         (email, username, role_id, salt, hash)\
#         VALUES ('{email}', '{username}', {role_id}, '{salt}', '{hash}')"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
