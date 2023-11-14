from functools import wraps
from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from back.models.sarima.sarima_model import forecast_all_sarima, train_all_sarima
from back.database.users.users import authenticate, add_user
from back.models.apriori import get_rank
from back.analytics.nuseda import plots
from back.analytics.generate_heatmap import heatmap
from back.analytics.map_pin import generate_map_points
from connect_sql import establish_sql_connection
from jinja2.exceptions import TemplateNotFound
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

def get_user_from_username(username):
    db,cursor = establish_sql_connection()
    query = f'SELECT Users.id, Users.username, User_roles.role \
        FROM Users LEFT JOIN User_roles ON Users.role_id = User_roles.id \
            WHERE Users.username = "{username}";'

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()

    # Check if the result is not None
    if result:
        user_id, username, role = result
        print(f'User {username} added')
        return User(user_id, username,role)
    else:
        print('No user found')
        return None

@login_manager.user_loader
def load_user(user_id):
    db,cursor = establish_sql_connection()
    query = f'SELECT Users.id, Users.username, User_roles.role \
        FROM Users LEFT JOIN User_roles ON Users.role_id = User_roles.id \
            WHERE Users.id= "{user_id}";'

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()

    # Check if the result is not None
    if result:
        user_id, username, role = result
        print(f'User {username} logged in')
        return User(user_id, username,role)
    else:
        print('No user found')
        return None


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                return "Unauthorized", 403  # Adjust the response accordingly
        return wrapper
    return decorator

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['UserID']
        password = request.form['Password']
        
        authenticated, role = authenticate(username,password)
        
        if authenticated:
            user = get_user_from_username(username) # create user
            login_user(user)
        else:
            return "Invalid UserID or Password"
        
        if role == 'security':
            return redirect(url_for('security'))
        elif role == 'analytics':
            return redirect(url_for('analytics'))
        
    return render_template('home.html')

@app.route('/add-new-user', methods=['POST'])
def add_new_user():
    data = request.get_json()

    if not data or 'username' not in data or 'role' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid JSON format'}), 400

    username = data['username']
    role = data['role']
    password = data['password']
    email = None
    if 'email' in data:
        email = data['email']

    add_user(username,password,role,email)

    return "User added"

@app.route("/prediction")
@login_required
def send_p():
    return send_file("back/data/test.png")

@app.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    username = current_user.id
    print(f"User {username} is authenticated")
    # if request.method == 'POST':
    #     new_report = {
    #         'IncidentID': request.form['id'],
    #         'Description': request.form['description'],
    #         'Incidents': request.form['type'],
	#     'FirstUpdate': request.form['datetime'],
	#     'Priority': request.form['priority'],
    #         'Location': request.form['location'],
	#     'Building': request.form['building'],
	#     'Status': request.form['status'],
	#     'User': request.form['user'],
	#     'Latitude': request.form['latitude'],
	#     'Longitude': request.form['longitude']
    #     }

    #     update_csv(new_report)

    data = pd.read_csv('front/data/data_test.csv')

    ## CODES TO UPDATE CSV IN THE FORMAT YOU WANT - use pandas to wrangle instead of java
    # df['FirstUpdate'] = pd.to_datetime(df['FirstUpdate'])
    # df['Date'] = df['FirstUpdate'].dt.date
    # df['Time'] = df['FirstUpdate'].dt.time
    # df.rename(columns={'IncidentID': 'Incident ID',
    #                    'Incidents': 'Incident Type'}, inplace=True)
    # df = df[['Incident ID','Description','Date','Time',
    #          'Incident Type','Location','Building','Status','Priority',
    #          'User','Latitude','Longitude'
    #          ]]
    data_dict = data.to_dict(orient='records')

    return render_template('security.html', data=data_dict)

@app.route('/analytics', methods=['GET'])
@login_required
@role_required('analytics')
def analytics():
    user_id = current_user.id
    return render_template('analytics.html')


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
@app.route('/train-all', methods=['GET'])
@login_required
@role_required('analytics')
def train_all():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    train_all_sarima(incident_types)
    return jsonify({'message': 'All models trained successfully'})

# Endpoint to generate forecast for all incident types
@app.route('/forecast-all', methods=['GET'])
@login_required
@role_required('analytics')
def get_all_forecasts():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    forecast_all_sarima(incident_types)
    return jsonify({'message': 'Forecasts generated for all incident types'})

# Endpoint to get forecast plots for specified type
@app.route('/get-forecast-plot', methods=['GET'])
@login_required
@role_required('analytics')
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
    
# Apriori Algorithm 

# Endpoint to get rank_priority
@app.route('/rank-priority', methods=['GET'])
@login_required
@role_required('analytics')
def rank_priority():

    location = request.args.get('location')
    day = request.args.get('day')
    hour = request.args.get('hour')

    try:
        return get_rank(location,day,hour)
    except TypeError:
        return 'Input not found.', 404
    
#Data Visualization

@app.route('/generate-plots', methods=['GET'])
@login_required
@role_required('analytics')
def plot_generation():
    return plots()



@app.route('/plots/Monthly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def monthly_plot():
    try:
        return render_template("Monthly_Counts_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/plots/Daily-Counts-by-Year', methods=['GET'])
def daily_plot():
    try:
        return render_template("Daily_Counts_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/plots/Hourly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def hourly_plot():
    try:
        return render_template("Hourly_Counts_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/plots/Coun-_of-Location-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def location_plot():
    try:
        return render_template("Count_of_Location_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/plots/Count-ofIncidents-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def incident_plot():
    try:
        return render_template("Count_of_Incidents_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/generate-heatmap', methods=['GET'])
@login_required
@role_required('analytics')
def heatmap_generation():
    return heatmap()

@app.route('/plots/heatmap', methods=['GET'])
@login_required
@role_required('analytics')
def heatmap_plot():
    try:
        return render_template("heatmap1.html")
    except TemplateNotFound:
        return 'Template not found: Please generate plot first!'

@app.route('/generate-map-pin', methods=['GET'])
@login_required
@role_required('security')
def map_pin_generation():
    return generate_map_points()



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
