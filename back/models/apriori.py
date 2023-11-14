from flask import Flask, request
import pandas as pd
from connect_sql import establish_sql_connection
from mlxtend.frequent_patterns import apriori
import matplotlib.pyplot as plt
import warnings

def get_rank(location,day,hour):
  db,cursor = establish_sql_connection()
  query = "SELECT  ilocg.location_group as Location, ilog.time as Time\
        FROM Incident_logs ilog, Incidents i,  Incident_locations iloc, Incident_location_groups ilocg\
        WHERE ilog.id=i.id AND i.location_id=iloc.id AND iloc.location_group_id=ilocg.id\
        AND ilog.status='OPEN' "
  cursor.execute(query)
  result = cursor.fetchall()
  # loading data
  df=pd.DataFrame(result, columns=['Location','Time'])

  warnings.filterwarnings("ignore")
  #changing data types
  def convert_dataframe(data):
    data['Time']=pd.to_datetime(data['Time'])
    data['Year'] = data['Time'].dt.year
    data['DayOfYear'] = data['Time'].dt.dayofyear
    data['Month'] = data['Time'].dt.month_name()
    data['DayOfWeek'] = data['Time'].dt.day_name()
    data['HourOfDay']=data['Time'].dt.hour
    data['HourOfDay']=data['HourOfDay'].map({0:'Late Night',1:'Late Night',2:'Late Night',3:'Late Night',4:'Late Night',5:'Early Morning',6:'Early Morning',7:'Early Morning',8:'Morning',9:'Morning',10:'Morning',11:'Afternoon',12:'Afternoon',13:'Afternoon',14:'Afternoon',15:'Evening',16:'Evening',17:'Evening',18:'Evening',19:'Night',20:'Night',21:'Night',22:'Night',23:'Late Night'})
    return data

  df=convert_dataframe(df)
  #print('df')
  #print(df.head(3))

  #selecting necessary columns
  data=df[['Location','DayOfWeek','HourOfDay']]
  # print('data')
  # print(data.head(3))

  #one-hot encoding all data
  encoded_data = pd.get_dummies(data, columns=['Location', 'DayOfWeek','HourOfDay'], prefix='', prefix_sep='')
  # print('encoded_data')
  # print(encoded_data.head(3))

  # using apriori algorithm
  frequent_crimes = apriori(encoded_data, min_support=0.0001, use_colnames=True)
  # print('frequent_crimes')
  # print(frequent_crimes.head(3))

  #conversion for prediction
  fc={'support':[],'itemsets':[]}
  for i in range(frequent_crimes.shape[0]):
    if len(frequent_crimes['itemsets'][i])==3:
      fc['support'].append(frequent_crimes['support'][i])
      temp=list(frequent_crimes['itemsets'][i])
      temp.sort()
      fc['itemsets'].append(temp)

  fc=pd.DataFrame(fc)
  fc=fc.sort_values(by=['support'],ascending=False)
  fc=fc.reset_index()
  fc=fc.drop(columns=['index'])
  fc=fc.reset_index()
  fc=fc.rename(columns={'index':'rank'})
  # print('fc')
  # print(fc.head(10))

  #predicting hotspot
  test=list((location,day,hour))
  test.sort()
  for i in range(fc.shape[0]-1):
      if test==fc['itemsets'][i]:
        rank=fc['rank'][i]
        total=fc.shape[0]
        return f'Priority {rank+1} out of {total}'

  return "Error: Check spelling or format! e.g. location=PGP, day=Saturday, hour=Afternoon \nOR \nNew Combination. Please add to the database!"
