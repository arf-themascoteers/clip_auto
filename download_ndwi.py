import ee
import geemap
import pandas as pd
import os

ee.Initialize(project='edge3-448100')

df = pd.read_csv("site.csv")
df.reset_index(inplace=True)
df["index"] += 1

os.makedirs("original", exist_ok=True)

def export_ndwi(row):
    point = ee.Geometry.Point(float(row['lon']), float(row['lat']))
    region = point.buffer(1000)

    image = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(point)
        .filterDate('2022-01-01', '2025-06-30')
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5))
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
    )

    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')

    vis = ndwi.visualize(min=0, max=1, palette=['000000', '00FFFF'])
    filename = f"original/{row['index']}.png"

    geemap.download_ee_image(vis, region=region, filename=filename, scale=10, crs='EPSG:3857')

for ind, row in df.iterrows():
    try:
        export_ndwi(row)
    except Exception as e:
        print(f"Failed for row {row['index']}: {e}")
    if ind == 5:
        break

