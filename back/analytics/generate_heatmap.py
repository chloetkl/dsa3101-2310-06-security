import pandas as pd
import numpy as np
import os
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import geopandas as gpd

df=pd.read_csv('../data/data_v0.3_with_status.csv')
df_l = df.dropna(subset=['Latitude', 'Longitude'])

m = folium.Map([1.3050, 103.7927], zoom_start=15)
heat_data = [[row['Latitude'], row['Longitude']] for index, row in df_l.iterrows()]

# Add heatmap to map
HeatMap(heat_data).add_to(m)

m.save('../data/heatmap.html')
m.save('../../main/draft/Testing/data/heatmap.html')
