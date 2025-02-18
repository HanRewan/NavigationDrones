from libs.Map import Map
import numpy as np
import json
from dotenv import load_dotenv
#import asyncio
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

delta = 0.005
lat_min, lon_min = 48.21158821837459, 16.359301364935465
lat_max, lon_max = lat_min+delta, lon_min+delta
box = (lat_min, lon_min, lat_max, lon_max)
num_samples = 50

map = Map(box, num_samples, api_key)
#asyncio.run(map.fetch_elevations())
#map.get_buildings()

# Using preload data to not waste time on loading everything once again
# Then will be using Postgresql
with open("terrain_elevations.json", "r") as f:
    map.elevations = np.array(json.load(f)) 
with open("new_buildings.json", "r") as f:
    map.buildings = json.load(f)

map.gen_buildings_polygons()
map.plot_surface_buildings()



