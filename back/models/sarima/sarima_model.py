import pandas as pd
import matplotlib.pyplot as plt
import csv
from sklearn.metrics import mean_absolute_error
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pickle
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima

from back.models.sarima.feature_eng import engineer_features

def fetch_data(incident_type=False):
    # to edit to load from sql server
    data = pd.read_csv("back/data/data_v0.2_intermediate(for checking)_with_status.csv")
    if incident_type:
        data = data.loc[data['Incidents'] == f"{incident_type}"]
    return data

def train_and_evaluate(model, train, test):
    model.fit(train)
    predictions = model.predict(n_periods=len(test))

    mae = mean_absolute_error(test, predictions)
    return model, mae

def save_model(model, filename):
    with open(filename, 'wb') as pkl:
        pickle.dump(model, pkl)

def train_sarima(incident_type=False):
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
    mae_df.loc[len(mae_df)] = [datetime.now(),incident_type, mae]
    mae_df.to_csv('back/models/sarima/mae_tracking.csv', index=False)

    trained_model.fit(weekly_data)
    save_model(trained_model, f'back/models/sarima/sarima_model_{incident_type}.pkl')

def train_all_sarima(incident_types):
    train_sarima()
    for incident_type in incident_types:
        train_sarima(incident_type)

def forecast_sarima(incident_type=False):
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

def forecast_all_sarima(incident_types):
    forecast_sarima()
    for incident_type in incident_types:
        forecast_sarima(incident_type)