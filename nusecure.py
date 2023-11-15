from functools import wraps
from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, Blueprint
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from back.models.sarima.sarima_model import forecast_all_sarima, train_all_sarima
from back.database.users.users import authenticate, add_user
from back.models.apriori import get_rank
from back.analytics.nuseda import plots
from back.analytics.generate_heatmap import heatmap
from back.analytics.map_pin import generate_map_points
from connect_sql import establish_sql_connection
from jinja2.exceptions import TemplateNotFound
from connect_sql import establish_sql_connection, get_location_id, get_incident_type_id
import pandas as pd
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

## add blueprints
from app.admin import admin_bp
app.register_blueprint(admin_bp)

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
        elif role == 'admin':
            return redirect(url_for('admin.admin'))
        
    return render_template('home.html')


@app.route("/prediction")
@login_required
def send_p():
    return send_file("back/data/test.png")

@app.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    user_id = current_user.id
    print(f"User {user_id} is authenticated")

    if request.method == 'POST':
        try:
            new_report = {
                'Description': request.form['description'],
                'Incident Type': request.form['type'],
                'Datetime': request.form['datetime'],
                'Priority': request.form['priority'],
                'Location': request.form['building'],
                'Status': request.form['status'],
            }

            db,cursor = establish_sql_connection()

            ## Add incident
            description = new_report['Description']
            location_id = get_location_id(new_report['Location'])
            incident_type_id = get_incident_type_id(new_report['Incident Type'])
            query = f"INSERT INTO Incidents (description, location_id, incident_type_id) \
                VALUES ('{description}', '{location_id}', '{incident_type_id}')"
            cursor.execute(query)
            db.commit()

            ## Add incident logs(s)
            incident_id = cursor.lastrowid
            ## Add both open and close logs if new incident is close
            status = new_report['Status']
            priority = new_report['Priority']
            time = new_report['Datetime']
            notes = ""           

            ## Add open log if new incident is open
            if status == 'Close':
                query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                        ('{incident_id}','Open','{priority}','{time}','{user_id}','{notes}')"
                cursor.execute(query)
                db.commit()
                query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                        ('{incident_id}','Close','{priority}','{time}','{user_id}','{notes}')"
                cursor.execute(query)
                db.commit()
            else:
                query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                        ('{incident_id}','{status}','{priority}','{time}','{user_id}','{notes}')"
                cursor.execute(query)
                db.commit()

            ## success
            return jsonify({'message': f'New incident added successfully. Incident code: {incident_id}'}), 200

        except Exception as e:
            # Handle exceptions
            print(f"An error occurred: {e}")
            db.rollback()  # Rollback the changes in case of an error
            return jsonify({'error': f'Failed to add data due to {e}'}), 500

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
  

    db,cursor = establish_sql_connection()
    query = f'SELECT Incident_logs.incident_id,\
        Incidents.description,\
        Incident_logs.priority,\
        Incident_types.type,\
        Incident_location_groups.location_group,\
        Incident_locations.location,\
        Incident_locations.latitude,\
        Incident_locations.longitude,\
        Users.username,\
        Incident_logs.time,\
        Incident_logs.status\
        FROM Incident_logs\
        LEFT JOIN Incidents ON Incident_logs.incident_id = Incidents.id\
        LEFT JOIN Incident_locations ON Incidents.location_id = Incident_locations.id\
        LEFT JOIN Incident_location_groups ON Incident_locations.location_group_id = Incident_location_groups.id\
        LEFT JOIN Incident_types ON Incidents.incident_type_id = Incident_types.id\
        LEFT JOIN Users ON Incident_logs.user_id = Users.id\
        ORDER BY Incident_logs.time DESC;'
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(result, columns = columns)

    # Grouping by specified columns and aggregating time column
    data = data.groupby(['incident_id', 'description', 'priority', 'type', 'location_group',
                                    'location', 'latitude', 'longitude']).agg(
                                        FirstUpdate=('time', 'min'), LatestUpdate=('time', 'max'),
                                        username=('username', 'first'), 
                                        status=('status', 'first') 
                                        ).reset_index() 
    data = data.sort_values('LatestUpdate', ascending=False)
    now = datetime.now()
    end_of_today = datetime(now.year, now.month, now.day, 23, 59, 59)
    data = data[data['LatestUpdate'] <= end_of_today]
    data.rename(columns={'incident_id': 'IncidentID', 'description':'Description','priority': 'Priority', 
                         'type':'Incidents', 'location_group':'Location', 'location':'Building', 
                         'latitude':'Latitude', 'longitude':'Longitude', 'username':'User', 
                         'time': 'LatestUpdate', 'status':'Status'}, inplace=True)
    data['FirstUpdate'] = pd.to_datetime(data['FirstUpdate'])
    data['LatestUpdate'] = pd.to_datetime(data['LatestUpdate'])


    data = data[['IncidentID', 'Description', 'Priority', 'Incidents', 'Location', 'Building', 'Latitude', 'Longitude', 'User', 'FirstUpdate', 'LatestUpdate', 'Status']]

    
    data['FirstUpdate'] = pd.to_datetime(data['FirstUpdate'])
    data['Date'] = data['FirstUpdate'].dt.date
    data['Time'] = data['FirstUpdate'].dt.time
    data.rename(columns={'IncidentID': 'Incident ID',
             'Incidents': 'Incident Type',
	     'User': 'User Added'}, inplace=True)
    data = data[['Incident ID','Description','Date','Time',
             'Incident Type','Location','Building','Status','Priority',
             'User Added','Latitude','Longitude'
             ]]
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

@app.route('/plots/Count-of-Location-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def location_plot():
    try:
        return render_template("Count_of_Location_by_Year.html")
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!'

@app.route('/plots/Count-of-Incidents-by-Year', methods=['GET'])
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


    
@app.route('/logout', methods=['GET'])
def logout():
    try:
        logout_user()
        return redirect('/'), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
