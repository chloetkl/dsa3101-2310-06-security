from flask import Flask, request, send_file, render_template, jsonify
from back.models.sarima.sarima_model import forecast_all_sarima, train_all_sarima

import mysql.connector
import bcrypt
# from back_end.database.populate import add_user, check_auth

app = Flask(__name__)


@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

@app.route("/prediction")
def send_p():
    return send_file("back/data/test.png")

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

# Endpoint to train SARIMA models for all incident types
@app.route('/train_all', methods=['GET'])
def train_all():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    train_all_sarima(incident_types)
    return jsonify({'message': 'All models trained successfully'})

# Endpoint to generate forecast for all incident types
@app.route('/forecast_all', methods=['GET'])
def get_all_forecasts():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    forecast_all_sarima(incident_types)
    return jsonify({'message': 'Forecasts generated for all incident types'})

# Endpoint to get forecast plots for specified type
@app.route('/get_forecast_plot', methods=['GET'])
def get_forecast_plot():
    incident_type = request.args.get('incident_type', default=False)

    if incident_type:
        plot_file = f'back/models/sarima/forecast_plot/forecast_plot_{incident_type}.html'
    else:
        plot_file = f'back/models/sarima/forecast_plot/forecast_plot_False.html'

    try:
        return send_file(plot_file, mimetype='text/html')
    except FileNotFoundError:
        return 'File not found.', 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
