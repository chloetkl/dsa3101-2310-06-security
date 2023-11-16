import pandas as pd
import folium
from connect_sql import establish_sql_connection

def generate_map_points():
  db,cursor = establish_sql_connection()
  query = "SELECT  iloc.latitude as Latitude, iloc.longitude as Longitude \
        FROM Incident_logs ilog, Incidents i,  Incident_locations iloc\
        WHERE ilog.incident_id=i.id AND i.location_id=iloc.id \
        AND ilog.status='OPEN' "
  cursor.execute(query)
  result = cursor.fetchall()
  # loading data
  df=pd.DataFrame(result, columns=['Latitude','Longitude'])
  # Create a map centered at NUS Raffles Hall
  raffles_hall_coords = [1.3521, 103.8198]
  incident_map = folium.Map(location=raffles_hall_coords, zoom_start=12)
  # Dictionary to map incident types to colors
  color_mapping = {
    'Normal': 'green',
    'High': 'red'
  }
  # Add markers for each incident location with color coding based on incident type
  for index, row in data.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=row['Description'],
        icon=folium.Icon(color=color_mapping.get(row['Priority']))
    ).add_to(incident_map)
  # Save the map as an HTML file
  incident_map.save('color_coded_incidents_map.html')
  return "Map generated."
