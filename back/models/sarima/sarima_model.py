import pandas as pd
import matplotlib.pyplot as plt
import csv
from sklearn.metrics import mean_absolute_error
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pickle
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from connect_sql import establish_sql_connection
from back.models.sarima.feature_eng import engineer_features
import traceback


def fetch_data(incident_type=False):
    db,cursor = establish_sql_connection()
    query = f'SELECT Incident_logs.incident_id,\
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
        LEFT JOIN Users ON Incident_logs.user_id = Users.id'
    
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(result, columns = columns)

    cond1 = data['status'] == 'Open'
    cond2 = data['status'] =='Close'
    data['Open'] = ''
    data['Close'] = ''
    data.loc[cond1, 'Open'] = data.loc[cond1, 'time']
    data.loc[cond2, 'Close'] = data.loc[cond2, 'time']
    data['Close'] = data['Close'].shift(-1)
    del data['time'], data['status']
    data['Open'] = pd.to_datetime(data['Open'])
    data['Close'] = pd.to_datetime(data['Close'])
    data['Add'] = ((data['Close'] - data['Open']).dt.total_seconds()) / (24*3600)
    data = data.dropna()

    data['Year'] = data['Open'].dt.year
    data['DayOfYear'] = data['Open'].dt.dayofyear
    data['Month'] = data['Open'].dt.month
    data['DayOfWeek'] = data['Open'].dt.dayofweek
    data['time_period'] = data['DayOfWeek'].apply(lambda x: 'day_weekday' if x < 5 else 'weekend')

    data.rename(columns={'incident_id': 'IncidentID', 'type':'Incidents', 'location_group':'Location', 'location':'Building', 'latitude':'Latitude', 'longitude':'Longitude', 'username':'User'}, inplace=True)
    data = data[['IncidentID', 'Open', 'Add', 'Close', 'Year', 'DayOfYear', 'Month', 'DayOfWeek', 'time_period', 'Building', 'Location', 'Latitude', 'Longitude', 'Incidents', 'User']]

    #data = pd.read_csv("back/data/data_v0.2_intermediate(for checking)_with_status.csv")
    if incident_type:
        data = data.loc[data['Incidents'] == f"{incident_type}"]
    return data

def train_and_evaluate(model, train, test):
    model.fit(train)
    predictions = model.predict(n_periods=len(test))

    mae = mean_absolute_error(test, predictions)
    return model, mae

def save_model(model, filename):
    try:
        with open(filename, 'wb') as pkl:
            pickle.dump(model, pkl)
    except Exception as e:
        print(f"An error occurred during SARIMA model saving: {e}")
        traceback.print_exc()


def train_sarima(incident_type=False):
    try:
        if incident_type:
            data = fetch_data(incident_type)
        else:
            data = fetch_data()

        weekly_data, train, test = engineer_features(data)

        model = auto_arima(train,
                           start_p=0, start_q=0, 
                           max_p=0, max_q=0,     
                           m=52,                 
                           start_P=0, start_Q=0, 
                           max_P=2, max_Q=2,     
                           seasonal=True,        
                           d=0,                  
                           D=1,                  
                           trace=True,           
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True)

        trained_model, mae = train_and_evaluate(model, train, test)

        mae_df = pd.read_csv('back/models/sarima/mae_tracking.csv')
        mae_df.loc[len(mae_df)] = [datetime.now(), incident_type, mae]
        mae_df.to_csv('back/models/sarima/mae_tracking.csv', index=False)

        trained_model.fit(weekly_data)
        save_model(trained_model, f'back/models/sarima/sarima_model_{incident_type}.pkl')

    except Exception as e:
        print(f"An error occurred during SARIMA model training: {e}")
        traceback.print_exc()
        
def train_all_sarima(incident_types):
    train_sarima()
    for incident_type in incident_types:
        train_sarima(incident_type)

def forecast_sarima(incident_type=False):
    try:
        with open(f'back/models/sarima/sarima_model_{incident_type}.pkl', 'rb') as pkl:
            model = pickle.load(pkl)

        future_forecast = model.predict(n_periods=52)

        last_date = datetime.now()
        future_dates = [last_date + timedelta(weeks=i) for i in range(1, 53)]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=future_dates, y=round(future_forecast), mode='lines', name='Forecast'))

        if incident_type:
            fig.update_layout(title=f'1 YEAR FORECAST OF WEEKLY COUNTS OF {incident_type}',
                            xaxis_title='Time',
                            yaxis_title='Predicted Count')
        else:
            fig.update_layout(title=f'1 YEAR FORECAST OF WEEKLY COUNTS OF ALL INCIDENTS',
                            xaxis_title='Time',
                            yaxis_title='Predicted Count')

        forecast_plot = f'back/models/sarima/forecast_plot/forecast_plot_{incident_type}.html'
        fig.write_html(forecast_plot)
        print("Forecast generated")
    
    except Exception as e:
        print(f"An error occurred during forecasting: {e}")
        traceback.print_exc()


def forecast_all_sarima(incident_types):
    forecast_sarima()
    for incident_type in incident_types:
        forecast_sarima(incident_type)
