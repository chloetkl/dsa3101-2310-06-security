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

def retrieve_security_table():
    df = pd.read_csv('data/data.csv')
    df['FirstUpdate'] = pd.to_datetime(df['FirstUpdate'])
    df['Date'] = df['FirstUpdate'].dt.date
    df['Time'] = df['FirstUpdate'].dt.time
    df.rename(columns={'IncidentID': 'Incident ID',
                       'Incidents': 'Incident Type'}, inplace=True)
    df = df[['Incident ID','Description','Date','Time',
             'Incident Type','Location','Building','Status','Priority',
             'User','Latitude','Longitude'
             ]]
    # df = df.append(new, ignore_index=True)
    # df.to_csv('../data/data.csv', index=False)
    return df

@app.route('/security', methods=['GET', 'POST'])
def security():
    data = retrieve_security_table()
    columns = data.columns.tolist()
    print(columns)
    data_dict = data.to_dict(orient='records')
    return render_template('security_table.html',columns=columns,data=data_dict)

@app.route('/analytics', methods=['GET'])
def analytics():
    return render_template('analytics.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
