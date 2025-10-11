import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler

def load_weather_data(folder_path):
    files = glob.glob(f"{folder_path}/*.csv")
    print(files)
    all_weather = []

    for file in files:
        meta = pd.read_csv(file, nrows=10)
        ts = pd.read_csv(file, skiprows=12)

        meta["latitude"] = meta["latitude"].astype(float)
        meta["longitude"] = meta["longitude"].astype(float)
        meta["location_id"] = meta["location_id"].astype(int)

        # Format timeseries
        ts["location_id"] = ts["location_id"].astype(int)
        ts["time"] = pd.to_datetime(ts["time"])

        # Merge metadata into timeseries
        merged = ts.merge(meta, on="location_id", how="left")

        # Convert numeric columns
        for col in merged.columns:
            if col not in ["time", "location_id", "latitude", "longitude", "timezone", "timezone_abbreviation"]:
                merged[col] = pd.to_numeric(merged[col], errors="coerce")

        all_weather.append(merged)

    # Combine all files
    weather_df = pd.concat(all_weather, ignore_index=True)

    # Round coordinates for merging
    weather_df["lat_round"] = weather_df["latitude"].round(2)
    weather_df["lon_round"] = weather_df["longitude"].round(2)

    weather_df['snow_depth (m)'] = weather_df['snow_depth (m)'].fillna(0)

    weather_df.drop(labels=["location_id", "latitude", "longitude", "timezone", "timezone_abbreviation", "utc_offset_seconds"], axis=1, inplace=True)

    print(weather_df.isna().sum())
    # weather_df.dropna(inplace=True)
    return weather_df


# ======================================================
# 3. 🔗 Merge weather & fire datasets
# ======================================================
def merge_fire_weather(weather_df, fire_df):
    # Select fire columns of interest
    fire_cols = ["Ign_Hour", "lat_round", "lon_round", "EstTotalAc", "Cause"]

    merged = weather_df.merge(
        fire_df[fire_cols],
        how="left",
        left_on=["time", "lat_round", "lon_round"],
        right_on=["Ign_Hour", "lat_round", "lon_round"]
    )

    merged = merged.drop(columns=["Ign_Hour"])

    # Add target variable
    merged["fire_occurred"] = np.where(merged["EstTotalAc"].notna(), 1, 0)
    merged["EstTotalAc"] = merged["EstTotalAc"].fillna(0)  # fill missing area as 0

    return merged


# ======================================================
# 4. 🧮 Feature engineering
# ======================================================
def add_features(df):
    # Time features (hour & day cyclical encoding)
    df["hour"] = df["time"].dt.hour
    df["day_of_year"] = df["time"].dt.dayofyear

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["day_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365)
    df["day_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365)

    # Drop raw time components after encoding
    df = df.drop(columns=["hour", "day_of_year"])

    # Normalize selected weather variables
    scaler = MinMaxScaler()
    weather_features = [
        "temperature_2m (ÂºC)",
        "relative_humidity_2m (%)",
        "dew_point_2m (ÂºC)",
        "wind_speed_10m (km/h)",
        "wind_gusts_10m (km/h)",
        "pressure_n",
        "surface_pressure",
        "cloud_cover",
        "soil_temperature",
    ]
    # Keep only columns that exist
    existing_features = [f for f in weather_features if f in df.columns]
    df[existing_features] = scaler.fit_transform(df[existing_features])

    return df


    


if __name__ == "__main__":
    fire_path = "fires.csv"
    weather_folder = "./data_pipeline/test/data"

    print("Loading weather data...")
    weather_df = load_weather_data(weather_folder)



    # print("Merging fire and weather data...")
    # merged_df = merge_fire_weather(weather_df, fire_df)

    # print("Engineering features...")
    # final_df = add_features(merged_df)

    # print(f"✅ Final dataset shape: {final_df.shape}")
    # print(final_df.head())

    # Optional: save the result
    weather_df.to_csv("merged_weather.csv", index=False)
