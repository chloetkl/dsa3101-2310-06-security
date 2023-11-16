from functools import wraps
from flask import request, send_file, render_template, jsonify, Blueprint
from flask_login import login_required, current_user
from back.models.sarima.sarima_model import forecast_all_sarima, train_all_sarima
from back.models.apriori import get_rank
from back.analytics.nuseda import plots
from back.analytics.generate_heatmap import heatmap
from jinja2.exceptions import TemplateNotFound


analytics_bp = Blueprint('analytics', __name__)

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                return f"Unauthorized, page only accessible to {required_role}", 403  # Adjust the response accordingly
        return wrapper
    return decorator


## Analytics Page

@analytics_bp.route('/analytics', methods=['GET'])
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

@analytics_bp.route('/analytics/generate-plots', methods=['GET'])
@login_required
@role_required('analytics')
def plot_generation():
    try:
        return plots(), 200 
    except Exception as e:
        error_message = f"Plot generation failed: {e}"
        return jsonify({'error': error_message}), 500


@analytics_bp.route('/analytics/plots/Monthly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def monthly_plot():
    try:
        return send_file("static/Monthly_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@analytics_bp.route('/analytics/plots/Daily-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def daily_plot():
    try:
        return send_file("static/Daily_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@analytics_bp.route('/analytics/plots/Hourly-Counts-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def hourly_plot():
    try:
        return send_file("static/Hourly_Counts_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@analytics_bp.route('/analytics/plots/Count-of-Location-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def location_plot():
    try:
        return send_file("static/Count_of_Location_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@analytics_bp.route('/analytics/plots/Count-of-Incidents-by-Year', methods=['GET'])
@login_required
@role_required('analytics')
def incident_plot():
    try:
        return send_file("static/Count_of_Incidents_by_Year.html", mimetype='text/html'), 200
    except TemplateNotFound:
        return 'TemplateNotFound: Please generate plot first!', 404

@analytics_bp.route('/analytics/generate-heatmap', methods=['GET'])
@login_required
@role_required('analytics')
def heatmap_generation():
    try:
        return heatmap(), 200
    except Exception as e:
        error_message = f"Plot generation failed: {e}"
        return jsonify({'error': error_message}), 500 

@analytics_bp.route('/analytics/plot/heatmap', methods=['GET'])
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
@analytics_bp.route('/analytics/predictions/rank-priority', methods=['GET'])
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
@analytics_bp.route('/analytics/predictions/time-series/train-all', methods=['GET'])
@login_required
@role_required('analytics')
def train_all():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    train_all_sarima(incident_types)
    return jsonify({'message': 'All models trained successfully'})

# Endpoint to generate forecast for all incident types
@analytics_bp.route('/analytics/predictions/time-series/forecast-all', methods=['GET'])
@login_required
@role_required('analytics')
def get_all_forecasts():
    incident_types = ['LOST AND FOUND','DAMAGED PROPERTY','SEXUAL INCIDENTS','STOLEN ITEMS','EMERGENCY INCIDENTS']
    forecast_all_sarima(incident_types)
    return jsonify({'message': 'Forecasts generated for all incident types'})

# Endpoint to get forecast plots for specified type
@analytics_bp.route('/analytics/predictions/time-series/get-forecast-plot', methods=['GET'])
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
