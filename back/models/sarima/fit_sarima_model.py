import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
import joblib


from back.models.sarima.feature_eng import engineer_features

def fit_sarima_model():
    data = pd.read_csv("back/data/data_v0.2_intermediate(for checking)_with_status.csv")

    weekly_incidents = engineer_features(data)

    auto_model = auto_arima(weekly_incidents,
                            start_p=0, start_q=0, 
                            max_p=0, max_q=0,     
                            m=52,                 
                            start_P=0, start_Q=0, 
                            max_P=3, max_Q=3,     
                            seasonal=True,        
                            d=0,                  
                            D=1,                  
                            trace=True,           
                            error_action='ignore',  
                            suppress_warnings=True, 
                            stepwise=True)

    joblib.dump(auto_model, 'back/output/sarima_model.pkl')
    print("Model added")