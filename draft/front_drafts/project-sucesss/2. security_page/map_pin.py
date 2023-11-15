import pandas as pd
import folium

# Read the data from the CSV file
data = pd.read_csv(r'C:\Users\Jiaying\OneDrive\Documents\NUS\2023.2024\Sem1\DSA3101\Assignment\Group Project\DSA3101_Project\main\draft\Testing\templates\Archive\datacsv.csv')
data = data.dropna(subset=['Latitude', 'Longitude'])

# Create a map centered at NUS Raffles Hall
raffles_hall_coords = [1.2959, 103.7745]
incident_map = folium.Map(location=raffles_hall_coords, zoom_start=14)

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
