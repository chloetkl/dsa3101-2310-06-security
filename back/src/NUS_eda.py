from flask import Flask, request, render_template, redirect, jsonify
import pandas as pd
from connect_sql import establish_sql_connection
import plotly.express as px
import plotly.graph_objs as go


app = Flask(__name__)


@app.route('/generate_plots', methods=['GET'])
def plots():
  test=request.args.get('test')
  db, cursor = establish_sql_connection()
  query = "SELECT  ilocg.location_group as Location, ilog.time as Time, it.type as Incidents\
        FROM Incident_logs ilog, Incidents i,  Incident_locations iloc, Incident_location_groups ilocg, Incident_types it\
        WHERE ilog.id=i.id AND i.location_id=iloc.id AND iloc.location_group_id=ilocg.id AND i.incident_type_id=it.id\
        AND ilog.status='OPEN' "
  cursor.execute(query)
  result = cursor.fetchall()
  df=pd.DataFrame(result, columns=['Location','Time','Incidents'])
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

  #Monthly_Counts_by_Year
  count_data = df.groupby(['Month', 'Year']).size().reset_index(name='Count')
  days =  ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
  count_data['Month'] = pd.Categorical(count_data['Month'], categories=days, ordered=True)
  count_data.sort_values(by='Month',inplace=True)
  fig=px.line(count_data, x='Month', y='Count', color='Year', title='Monthly Counts by Year')
  fig.write_html("templates/Monthly_Counts_by_Year.html")

  #Daily_Counts_by_Year
  count_data = df.groupby(['DayOfWeek', 'Year']).size().reset_index(name='Count')
  days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
  count_data['DayOfWeek'] = pd.Categorical(count_data['DayOfWeek'], categories=days, ordered=True)
  count_data.sort_values(by='DayOfWeek',inplace=True)
  fig=px.line(count_data, x='DayOfWeek', y='Count', color='Year', title='Daily Counts by Year')
  fig.write_html("templates/Daily_Counts_by_Year.html")

  #Hourly_Counts_by_Year
  days = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night','Late Night']
  df['HourOfDay'] = pd.Categorical(df['HourOfDay'], categories=days, ordered=True)
  count_data = df.groupby(['HourOfDay', 'Year']).size().reset_index(name='Count')
  fig = px.line(count_data, x='HourOfDay', y='Count', color='Year', title='Hourly Counts by Year')
  fig.write_html("templates/Hourly_Counts_by_Year.html")

  #Count_of_Location_by_Year
  grouped_data = df.groupby([ 'Year','Location']).size().reset_index(name='Count')
  sorted_years = sorted(df['Year'].unique())
  traces = []
  for year in sorted_years:
    year_data = grouped_data[grouped_data['Year'] == year]
    trace = go.Bar(
       x=year_data['Location'],
       y=year_data['Count'],
       name=str(year)
       )
    traces.append(trace)
  layout = go.Layout(
    barmode='group',
    title='Count of Location by Year',
    xaxis=dict(title='Location'),
    yaxis=dict(title='Count')
    )
  fig = go.Figure(data=traces, layout=layout)
  fig.write_html("templates/Count_of_Location_by_Year.html")

  #Count_of_Incidents_by_Year
  grouped_data = df.groupby([ 'Year','Incidents']).size().reset_index(name='Count')
  sorted_years = sorted(df['Year'].unique())
  traces = []
  for year in sorted_years:
    year_data = grouped_data[grouped_data['Year'] == year]
    trace = go.Bar(
       x=year_data['Incidents'],
       y=year_data['Count'],
       name=str(year)
       )
    traces.append(trace)
  layout = go.Layout(
    barmode='group',  
    title='Count of Incidents by Year',
    xaxis=dict(title='Incidents'),
    yaxis=dict(title='Count')
    )
  fig = go.Figure(data=traces, layout=layout)
  fig.write_html("templates/Count_of_Incidents_by_Year.html")

  return "HTMLs generated"

@app.route('/plots/Monthly_Counts_by_Year', methods=['GET'])
def month_plot():
    return render_template(
        "Monthly_Counts_by_Year.html"
    )

@app.route('/plots/Daily_Counts_by_Year', methods=['GET'])
def daily_plot():
    return render_template(
        "Daily_Counts_by_Year.html"
    )

@app.route('/plots/Hourly_Counts_by_Year', methods=['GET'])
def hourly_plot():
    return render_template(
        "Hourly_Counts_by_Year.html"
    )

@app.route('/plots/Count_of_Location_by_Year', methods=['GET'])
def location_plot():
    return render_template(
        "Count_of_Location_by_Year.html"
    )

@app.route('/plots/Count_of_Incidents_by_Year', methods=['GET'])
def incident_plot():
    return render_template(
        "Count_of_Incidents_by_Year.html"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4999)