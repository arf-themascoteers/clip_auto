import ee
import geemap
import pandas as pd
import os

ee.Initialize(project='edge3-448100')

df = pd.read_csv("site.csv")
df.reset_index(inplace=True)
df["index"] += 1

os.makedirs("rgb", exist_ok=True)

def export_image(row):
    point = ee.Geometry.Point(float(row['lon']), float(row['lat']))
    region = point.buffer(1000).bounds()
    image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(point) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)) \
        .filterDate('2022-01-01', '2025-06-30') \
        .sort('CLOUD_COVER') \
        .first() \
        .select(['B4', 'B3', 'B2']) \
        .visualize(min=0, max=3000)

    filename = f"rgb/{row['index']}.png"
    geemap.download_ee_image(image, region=region, filename=filename, scale=10, crs='EPSG:3857')

for ind, row in df.iterrows():
    try:
        export_image(row)
    except Exception as e:
        print(f"Failed for row {row['index']}: {e}")
    if ind == 3:
        break
