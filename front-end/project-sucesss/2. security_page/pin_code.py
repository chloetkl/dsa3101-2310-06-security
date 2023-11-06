import pandas as pd
import folium

# Read the data from the CSV file
data = pd.read_csv('C:\\Users\\Jiaying\\OneDrive\\Documents\\NUS\\2023.2024\\Sem1\\DSA3101\\Assignment\\Group Project\\DSA3101_Project\\back-end\\data\\data_v0.3_with_status.csv')

# Create a map centered at NUS Raffles Hall
raffles_hall_coords = [1.2959, 103.7745]
incident_map = folium.Map(location=raffles_hall_coords, zoom_start=14)

# Add markers for each incident location
for index, row in data.iterrows():
    folium.Marker([row['Latitude'], row['Longitude']], popup=row['Location']).add_to(incident_map)

# Save the map to an HTML file
incident_map.save('map.html')
