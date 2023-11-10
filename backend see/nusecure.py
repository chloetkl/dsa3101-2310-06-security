from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import folium

app = Flask(__name__)

### Functions
def create_map():
    try:
        data = pd.read_csv('data/data.csv')  # Adjust the path to your CSV file
        data = data.dropna(subset=['Latitude', 'Longitude'])

        raffles_hall_coords = [1.2959, 103.7745]
        incident_map = folium.Map(location=raffles_hall_coords, zoom_start=14)

        color_mapping = {
            'Normal': 'green',
            'High': 'red'
        }

        for index, row in data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Description'],
                icon=folium.Icon(color=color_mapping.get(row['Priority']))
            ).add_to(incident_map)

        return incident_map._repr_html_()

    except Exception as e:
        return f"Error generating map: {str(e)}"

def update_csv(new):
    df = pd.read_csv('./data/data.csv')
    df = df.append(new, ignore_index=True)
    df.to_csv('./data/data.csv', index=False)

### Locations
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = request.form['UserID']
        password = request.form['Password']  

        if user_id == 'security' and password == 'security':
            return redirect(url_for('security'))
        elif user_id == 'analytics' and password == 'analytics':
            return redirect(url_for('analytics'))
        else:
            return "Invalid UserID or Password"
    return render_template('home.html')

@app.route('/security', methods = ['GET', 'POST'])
def security():
    if request.method == 'POST':
        new_report = {
            'IncidentID': request.form['id'],
            'Description': request.form['description'],
            'Incidents': request.form['type'],
            'FirstUpdate': request.form['datetime'],
            'Priority': request.form['priority'],
            'Location': request.form['location'],
            'Building': request.form['building'],
            'Status': request.form['status'],
            'User': request.form['user'],
            'Latitude': request.form['latitude'],
            'Longitude': request.form['longitude']
        }

        update_csv(new_report)

    data = pd.read_csv('./data/data.csv')
    data_dict = data.to_dict(orient='records')

    map_html = create_map()

    return render_template('security.html', map_html=map_html, data=data_dict)

@app.route('/analytics', methods=['GET'])
def analytics():
    return render_template('analytics.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
