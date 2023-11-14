import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import folium
from folium.plugins import HeatMap
from connect_sql import establish_sql_connection

def heatmap():
  db,cursor = establish_sql_connection()
  query = "SELECT  iloc.latitude as Latitude, iloc.longitude as Longitude \
        FROM Incident_logs ilog, Incidents i,  Incident_locations iloc\
        WHERE ilog.incident_id=i.id AND i.location_id=iloc.id \
        AND ilog.status='OPEN' "
  cursor.execute(query)
  result = cursor.fetchall()
  # loading data
  df=pd.DataFrame(result, columns=['Latitude','Longitude'])
  df_l = df.dropna(subset=['Latitude', 'Longitude'])
  m = folium.Map([1.3521, 103.8198], zoom_start=12)
  heat_data = [[row['Latitude'], row['Longitude']] for index, row in df_l.iterrows()]
  
  # Add heatmap to map
  HeatMap(heat_data).add_to(m)
  m.save('templates/heatmap1.html')

  return "Heatmap generated."
