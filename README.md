# 3D Terrain and Building Visualization

This project demonstrates how to:
1. Retrieve elevation data from the Google Maps Elevation API.
2. Retrieve building footprints from OpenStreetMap (using the Overpass API).
3. Combine both data sources to visualize a 3D surface with extruded building polygons using Matplotlib.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Usage](#usage)
- [Details & Explanation](#details--explanation)
  - [Map Class](#map-class)
  - [Buildings Class](#buildings-class)
  - [endpoint.py](#endpointpy)
- [License](#license)

---

## Overview

1. **Fetch Elevation Data**: Uses the Google Maps Elevation API (asynchronously) to get elevation for a grid of lat/lon samples.
2. **Fetch Building Data**: Uses Overpass (OpenStreetMap) to get building footprints (lat/lon for building polygons).
3. **Visualization**: Generates a 3D plot in Python (Matplotlib) showing the terrain and the extruded building geometries.

---

## Features

- **Asynchronous Elevation Retrieval**: Speeds up HTTP requests to the Google Maps Elevation API using `aiohttp` and `asyncio`.
- **Dynamic Building Footprints**: Retrieves building data from OpenStreetMap to construct 3D building polygons.
- **3D Plotting**: Displays the terrain as a 3D surface (with optional color shading by elevation) and extruded 3D buildings.

---

## Project Structure

```
├── endpoint.py
├── libs
│   ├── Map.py
│   └── Buildings.py
├── new_buildings.json
├── terrain_elevations.json
└── README.md  <-- (You are here)
```

- **endpoint.py**  
  Demonstrates how to use the `Map` class (and indirectly the `Buildings` class) to:
  1. Load terrain elevations from a local file (or potentially fetch anew).
  2. Load building data from a local file (or fetch via Overpass API).
  3. Generate 3D polygons and visualize them.

- **libs/Map.py**  
  Contains the `Map` class which orchestrates:
  - Fetching or loading elevation data.
  - Fetching or loading building data.
  - Generating building polygons in 3D.
  - Plotting with Matplotlib.

- **libs/Buildings.py**  
  Contains the `Buildings` class which:
  - Fetches raw building data from Overpass.
  - Parses that data into a list of footprints & heights.
  - Generates extruded walls and roofs in 3D (using `matplotlib`’s `Poly3DCollection`).

- **new_buildings.json** (optional or generated)  
  Example building data (to avoid fetching from Overpass repeatedly).

- **terrain_elevations.json** (optional or generated)  
  Example elevation data (to avoid repeated API calls to Google).

---

## Getting Started

### Installation

1. **Clone or Download** this repository.
2. **Install dependencies** (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
   
   If you do not have a `requirements.txt`, ensure you install the following (typical):
   ```bash
   pip install numpy matplotlib requests aiohttp python-dotenv
   ```

### Environment Variables

Create a `.env` file at the root of your project (or ensure environment variables are set) with the following variable:

```
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
```

- **GOOGLE_API_KEY**  
  A valid Google Maps Elevation API key. This is required if you want to fetch elevation data dynamically from Google.  
  *Note: If you only want to test visualization with pre-saved data (`terrain_elevations.json`, etc.), you can skip this step.*

### Usage

1. **Set up your environment**:  
   ```bash
   pip install -r requirements.txt
   cp .env.example .env  # or manually create .env with your API key
   ```

2. **Run the script**:
   ```bash
   python endpoint.py
   ```
   - This will:
     1. Load pre-saved elevation data from `terrain_elevations.json`.
     2. Load pre-saved building data from `new_buildings.json`.
     3. Convert building footprints into 3D polygons.
     4. Show a Matplotlib 3D window with terrain and extruded buildings.

3. **Optional**: If you want to fetch fresh data:
   - Uncomment the relevant lines in `endpoint.py` to:
     - `asyncio.run(map.fetch_elevations())` (for Google Elevation)
     - `map.get_buildings()` (for Overpass building footprints)
   - Then call:
     ```python
     map.save_elevations("terrain_elevations.json")
     map.save_buildings("new_buildings.json")
     ```
   - This will generate `.json` files so you can reuse them.

---

## Details & Explanation

### Map Class

Defined in `libs/Map.py`. Responsibilities:
1. **Coordinates and Grid Setup**:  
   - `lat_min`, `lon_min`, `lat_max`, `lon_max`: bounding box for the area of interest.  
   - `num_samples`: how many grid points in each dimension for elevation sampling.  
   - Creates a mesh grid of lat/lon using `numpy.linspace`.

2. **fetch_elevations()**:  
   - Makes asynchronous requests to [Google Maps Elevation API](https://developers.google.com/maps/documentation/elevation/intro) for each grid point.

3. **get_buildings()**:  
   - Invokes `Buildings.get_buildings_parsed(...)` to retrieve building footprints from Overpass.

4. **gen_buildings_polygons()**:  
   - Uses `Buildings.build_footprint_walls_polygons(...)` to convert footprints + heights into 3D polygons.

5. **plot_surface_buildings()**:  
   - Creates a 3D surface plot from `self.elevations` using `matplotlib`.
   - Overlays building polygons.

### Buildings Class

Defined in `libs/Buildings.py`. Responsibilities:
1. **get_buildings_raw()**:  
   - Sends a query to the Overpass API for buildings within the bounding box.

2. **get_buildings_parsed()**:  
   - Converts raw Overpass JSON into a structured list of building footprints with associated heights.

3. **build_footprint_walls_polygons()**:  
   - Generates 3D “roof” polygons and wall “Quad” polygons using `matplotlib`’s `Poly3DCollection`.
   - Looks up ground elevation under each footprint node.

4. **get_elevation()**:  
   - Helper to find the closest grid point in the `LAT`/`LON` arrays to the building node’s lat/lon.  
   - Returns the corresponding elevation from the `elevations` array.

### endpoint.py

- Loads environment variables.
- Sets bounding box (`lat_min`, `lon_min`, `lat_max`, `lon_max`) and grid resolution (`num_samples`).
- Creates a `Map` object, loads or fetches data, then calls `plot_surface_buildings()`.

---

## License

This project does not have a specific license.

---

**Enjoy exploring 3D terrain and buildings with this code!**