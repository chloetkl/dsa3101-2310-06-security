from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

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

def update_csv(new):
    df = pd.read_csv('./data/data.csv')
    df = df.append(new, ignore_index=True)
    df.to_csv('./data/data.csv', index=False)

@app.route('/security', methods=['GET', 'POST'])
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
    return render_template('security_table.html', data=data_dict)

@app.route('/analytics', methods=['GET'])
def analytics():
    return render_template('analytics.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
