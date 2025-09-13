import earthaccess
import os

# 1. Log in to your Earthdata account
earthaccess.login()

# 2. Define your search parameters
short_name = "GEDI02_A"
bbox = (92.1, 6.7, 94.3, 13.8) # Bounding box for Andaman & Nicobar
time_range = ("2020-01-01", "2021-01-01")

# 3. Search for the data
granules = earthaccess.search_data(
    short_name=short_name,
    bounding_box=bbox,
    temporal=time_range
)

# 4. Download the files to a local folder
if granules:
    earthaccess.download(granules, local_path="gedi_data")
    print(f"Successfully downloaded {len(granules)} GEDI files.")
else:
    print("No GEDI data found for the specified region and time.")