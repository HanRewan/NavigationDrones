import requests
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Buildings:
    @staticmethod
    def get_buildings_raw(min_lat, min_lon, max_lat, max_lon):
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
        way["building"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        (._;>;);
        out body;
        """
        response = requests.get(overpass_url, params={'data': query})
        print(response)
        return response.json()
    
    @staticmethod
    def get_buildings_parsed(min_lat, min_lon, max_lat, max_lon):
        osm_data = Buildings.get_buildings_raw(
            min_lat, min_lon, max_lat, max_lon)

        nodes = {}
        ways = []
        
        for element in osm_data.get("elements", []):
            if element["type"] == "node":
                nid = element["id"]
                lat = element["lat"]
                lon = element["lon"]
                nodes[nid] = (lat, lon)
            elif element["type"] == "way":
                ways.append(element)
        
        # Now parse ways (building footprints)
        building_list = []
        
        for way in ways:
            tags = way.get("tags", {})
            if "building" not in tags:
                continue
            
            # Attempt to get building height
            height_m = None
            
            # If "height" is explicitly set
            if "height" in tags:
                try:
                    height_m = float(tags["height"])
                except ValueError:
                    pass
            
            # Otherwise, if "building:levels" is present
            if not height_m and "building:levels" in tags:
                try:
                    levels = float(tags["building:levels"])
                    height_m = levels * 3.0  # naive assumption: 3m per floor
                except ValueError:
                    pass
            
            # If there's still no height info, skip
            if not height_m:
                continue
            
            # Construct the building footprint from node refs
            node_refs = way.get("nodes", [])
            coords = []
            for nid in node_refs:
                if nid in nodes:
                    coords.append(nodes[nid])  # (lat, lon)
            
            if len(coords) < 3:
                continue
            
            building_list.append({
                'footprint': coords,
                'height_m': height_m
            })
        
        return building_list
    
    @staticmethod
    def get_elevation(lat, lon, LAT_grid, LON_grid, elevations):
        diff = np.abs(LAT_grid - lat) + np.abs(LON_grid - lon)
        row, col = np.unravel_index(np.argmin(diff), diff.shape)
        return elevations[row, col]
    
    @staticmethod
    def build_footprint_walls_polygons(building_data, LAT_grid, LON_grid, elevations):
        polys_3d = []
        
        for b in building_data:
            footprint = b['footprint']
            height_m  = b['height_m']

            top_coords = []
            bot_coords = []
            
            for (lat, lon) in footprint:
                ground_z = Buildings.get_elevation(
                    lat, lon, LAT_grid, LON_grid, elevations)
                top_z = ground_z + height_m

                top_coords.append((lon, lat, top_z))
                bot_coords.append((lon, lat, ground_z))
            
            roof_poly = Poly3DCollection([top_coords], facecolor='blue', alpha=1)
            roof_poly.set_edgecolor('k')
            roof_poly.set_zsort('max')
            polys_3d.append(roof_poly)

            wall_polys = []
            n = len(footprint)
            for i in range(n):
                j = (i + 1) % n  
                wall_quad = [
                    bot_coords[i],  # bottom-left
                    bot_coords[j],  # bottom-right
                    top_coords[j],  # top-right
                    top_coords[i]   # top-left
                ]
                wall_polys.append(wall_quad)

            
            
            walls = Poly3DCollection(wall_polys, facecolor='red', alpha=0.2)
            walls.set_edgecolor('k')
            walls.set_zsort('max')
            polys_3d.append(walls)
        
        return polys_3d