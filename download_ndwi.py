import ee
import geemap
import pandas as pd
import os

ee.Initialize(project='edge3-448100')

df = pd.read_csv("site.csv")
df.reset_index(inplace=True)
df["index"] += 1

os.makedirs("original", exist_ok=True)

def export_ndwi(row, faulty=False):
    point = ee.Geometry.Point(float(row['lon']), float(row['lat']))
    region = point.buffer(1000)

    start = "2021-06-01"
    end = "2025-05-30"
    cloud = 5

    if faulty:
        start = "2024-06-01"
        end = "2024-12-30"
        cloud = 10

    print("Attempting ", faulty)
    image = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(point)
        .filterDate(start, end)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud))
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
    )

    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    ndwi_scaled = ndwi.multiply(127.5).add(127.5).uint8()

    geemap.download_ee_image(
        ndwi_scaled,
        region=region,
        filename=f"original/{row['index']}.png",
        scale=10,
        crs='EPSG:3857'
    )

for ind, row in df.iterrows():
    faulty = False
    if ind == 1:
        faulty = True
    try:
        export_ndwi(row, faulty)
    except Exception as e:
        print(f"Failed for row {row['index']}: {e}")
    # if ind == 1:
    #     break