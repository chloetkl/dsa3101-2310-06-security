import pandas as pd

def engineer_features(data):
    data['Open'] = pd.to_datetime(data['Open'])
    data.sort_values('Open', inplace=True)

    data.set_index('Open', inplace=True)

    weekly_data = data['IncidentID'].resample('W').count()

    last_date = weekly_data.index[-1]

    split_date_1_year = last_date - pd.DateOffset(years=1)

    train = weekly_data.loc[weekly_data.index <= split_date_1_year]
    test = weekly_data.loc[weekly_data.index > split_date_1_year]

    return weekly_data, train, test