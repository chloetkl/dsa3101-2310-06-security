from functools import wraps
from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, Blueprint
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from back.models.sarima.sarima_model import forecast_all_sarima, train_all_sarima
from back.database.users.users import authenticate, add_user
from back.models.apriori import get_rank
from back.analytics.nuseda import plots
from back.analytics.generate_heatmap import heatmap
from connect_sql import establish_sql_connection
from jinja2.exceptions import TemplateNotFound
from connect_sql import establish_sql_connection, get_location_id, get_incident_type_id
from datetime import datetime
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

## Add Blueprints
from app.admin import admin_bp
app.register_blueprint(admin_bp)
from app.security import security_bp
app.register_blueprint(security_bp)


## For Authentication
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

## Home - Login page
@app.route('/', methods=['GET'])
def home():
    try:
        return render_template('home.html'), 200
    except Exception as e:
        error_message = f"Error rendering template: {e}"
        return jsonify({'error': error_message}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['UserID']
        password = request.form['Password']

        authenticated, role = authenticate(username,password)

        if authenticated:
            user = get_user_from_username(username) # create user
            login_user(user)
        else:
            return "Invalid UserID or Password", 401

        if role == 'security':
            return redirect(url_for('security.security')), 302
        elif role == 'analytics':
            return redirect(url_for('analytics')), 302
        elif role == 'admin':
            return redirect(url_for('admin.admin')), 302
    except HTTPException as http_error:
        return jsonify({'error': str(http_error)}), http_error.code
    except Exception as e:
        return jsonify({'error': f"Internal Server Error: {e}"}), 500

## Analytics Page

@app.route('/analytics', methods=['GET'])
@login_required
@role_required('analytics')
def analytics():
    try:
        return render_template('analytics.html'), 200
    except TemplateNotFound:
        return "Template not found", 404
    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {e}")
        return "Internal Server Error", 500

# @app.route("/prediction")
# @login_required
# @role_required('analytics')
# def send_p():
#     return send_file("back/data/test.png")

### Data Visualization

@app.route('/analytics/generate-plots', methods=['GET'])
@login_required
@role_required('analytics')
def plot_generation():
    try:
        return plots(), 200 
    except Exception as e:
        error_message = f"Plot generation failed: {e}"
        return jsonify({'error': error_message}), 500


@app.route('/analytics/plots/Monthly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def monthly_plot():
    try:
        return send_file("static/Monthly_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@app.route('/analytics/plots/Daily-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def daily_plot():
    try:
        return send_file("static/Daily_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@app.route('/analytics/plots/Hourly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def hourly_plot():
    try:
        return send_file("static/Hourly_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@app.route('/analytics/plots/Count-of-Location-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def location_plot():
    try:
        return send_file("static/Count_of_Location_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@app.route('/analytics/plots/Count-of-Incidents-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def incident_plot():
    try:
        return send_file("static/Count_of_Incidents_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@app.route('/analytics/generate-heatmap', methods=['GET'])
@login_required
@role_required('analytics')
def heatmap_generation():
    try:
        return heatmap(), 200
    except Exception as e:
        error_message = f"Plot generation failed: {e}"
        return jsonify({'error': error_message}), 500 

@app.route('/analytics/plot/heatmap', methods=['GET'])
@login_required
@role_required('analytics')
def heatmap_plot():
    try:
        plot_file = "static/heatmap.html"
        return send_file(plot_file, mimetype='text/html'), 200
    except TemplateNotFound:
        return 'Template not found: Please generate plot first!', 404
    
### Apriori Algorithm

# Endpoint to get rank_priority
@app.route('/analytics/rank-priority', methods=['GET'])
@login_required
@role_required('analytics')
def rank_priority():

    location = request.args.get('location')
    day = request.args.get('day')
    hour = request.args.get('hour')

    try:
        return get_rank(location,day,hour), 200
    except TypeError:
        return 'Input not found.', 404
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return jsonify({'error': error_message}), 500


### SARIMA

# Endpoint to train SARIMA models for all incident types
@app.route('/analytics/predictions/time-series/train-all', methods=['GET'])
@login_required
@role_required('analytics')
def train_all():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    train_all_sarima(incident_types)
    return jsonify({'message': 'All models trained successfully'})

# Endpoint to generate forecast for all incident types
@app.route('/analytics/predictions/time-series/forecast-all', methods=['GET'])
@login_required
@role_required('analytics')
def get_all_forecasts():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    forecast_all_sarima(incident_types)
    return jsonify({'message': 'Forecasts generated for all incident types'})

# Endpoint to get forecast plots for specified type
@app.route('/analytics/predictions/time-series/get-forecast-plot', methods=['GET'])
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



@app.route('/logout', methods=['GET'])
def logout():
    try:
        logout_user()
        return redirect('/'), 302
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
