import numpy as np
import json
import aiohttp
import asyncio
from libs.Buildings import Buildings
import matplotlib.pyplot as plt

class Map:
    def __init__(self, box, num_samples, API_KEY):
        self.API_KEY = API_KEY
        self.lat_min, self.lon_min, self.lat_max, self.lon_max = box
        self.num_samples = num_samples

        self.lats = np.linspace(self.lat_min, self.lat_max, self.num_samples)
        self.lons = np.linspace(self.lon_min, self.lon_max, self.num_samples)
        self.LON, self.LAT = np.meshgrid(self.lons, self.lats)

    async def get_elevation(self, session, lat, lon):
        url = "https://maps.googleapis.com/maps/api/elevation/json"
        params = {
            "locations": f"{float(lat):.5f},{float(lon):.5f}",
            "key": self.API_KEY
        }
        async with session.get(url, params=params) as response:
            data = await response.json()
            if data["status"] == "OK":
                return data["results"][0]["elevation"]
            return None
        
    async def fetch_elevations(self):
        elevations = np.zeros_like(self.LAT)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.num_samples):
                for j in range(self.num_samples):
                    lat_ij = self.LAT[i, j]
                    lon_ij = self.LON[i, j]
                    tasks.append(self.get_elevation(session, lat_ij, lon_ij))
                
            results = await asyncio.gather(*tasks)
            
            index = 0
            for i in range(self.num_samples):
                for j in range(self.num_samples):
                    elevations[i, j] = results[index]
                    index += 1
        
        self.elevations = elevations

    def get_buildings(self):
        self.buildings = Buildings.get_buildings_parsed(
            self.lat_min, self.lon_min, self.lat_max, self.lon_max)
        
    def gen_buildings_polygons(self):
        self.buildings_polygons = Buildings.build_footprint_walls_polygons(
            self.buildings, self.LAT, self.LON, self.elevations)
        
    def save_elevations(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.elevations.tolist(), f)
        
    def save_buildings(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.buildings, f)
        
    def plot_surface_buildings(self):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_zlim(150, 300)
        surf = ax.plot_surface(self.LON, self.LAT, self.elevations,
                        color='gray',
                        alpha=0.3,
                        rstride=1,
                        cstride=1,
                        edgecolor='black')
        plt.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Elevation (m)')
        plt.title("3D Terrain + Buildings")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation (m)')

        polygons_3d_walls = self.buildings_polygons
        for poly in polygons_3d_walls:
            ax.add_collection3d(poly)

        plt.show()
            
        
