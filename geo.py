import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv(".csv", header=None)
#load
df.columns = [
    "network", "mcc", "mnc", "lac", "cell_id", "psc",
    "longitude", "latitude", "range", "samples",
    "changeable", "created_at", "updated_at", "confidence"
]

#type cast
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce") 
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

text_cols = df.select_dtypes(include="object").columns

df[text_cols] =(
        df[text_cols]
        .apply(lambda col: col.str.strip())
        .apply(lambda col: col.str.replace(";","", regex=False))
        .apply(lambda col: col.str.replace(r"[^a-zA-Z0-9_\-\.]", "",regex=True))
        .apply(lambda col: col.str.replace(r"\s+", "", regex=True))
)

df =df.dropna(subset=["latitude","longitude"])

df =df[(df["latitude"].between(-90,90)) & (df["longitude"].between(-180,180))]
#Remove ซ้ำ
df =(df.sort_values("confidence", ascending=False)).drop_duplicates(subset = ["mcc","mnc","lac","cell_id"])


gdf_points = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.longitude, df.latitude),crs="EPSG:4326")

print("GeoDataFrame created successfully")

gdf_province = gpd.read_file("-")
gdf_province = gdf_province.to_crs(gdf_points.crs)

gdf_result = gpd.sjoin(
    gdf_points,
    gdf_province,
    how="left",
    predicate="within"
).rename(columns={"NAME_1": "province"})

gdf_result.drop(columns="geometry").to_csv("output_with_province.csv",index=False)

print("Done! Province mapping completed.")

