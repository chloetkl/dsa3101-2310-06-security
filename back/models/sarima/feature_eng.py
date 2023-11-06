import pandas as pd

def engineer_features(data):
    data['Open'] = pd.to_datetime(data['Open'])
    data['Open'].sort_values()
    data.set_index('Open', inplace=True)

    split_date = pd.Timestamp('2019-01-01')
    data = data.loc[data.index >= split_date]
    split_date = pd.Timestamp('2023-10-15')
    data = data.loc[data.index <= split_date]
    split_date = pd.Timestamp('2022-08-31')
    train = data.loc[data.index <= split_date]
    test = data.loc[data.index > split_date]

    weekly_incidents = train['IncidentID'].resample('W').count()
    return weekly_incidents
    