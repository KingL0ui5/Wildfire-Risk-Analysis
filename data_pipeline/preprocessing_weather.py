import pandas as pd
import glob
import zipfile
import os
from tqdm import tqdm

def load_weather_data(folder_path):
    # unzip_weather_folder(folder_path)
    files = glob.glob(f"{folder_path}/*.csv")
    print(files)
    all_weather = []
    bad_files = [] 
    
    for file in files:
        print(f"processing file: {file}")
        try:
            # meta, ts = split_file(file)
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
        
        except Exception as e:
            print(f"Error reading file: {file}")
            print(f"    {type(e).__name__}: {e}")
            bad_files.append(file)
            continue

    # Combine all files
    weather_df = pd.concat(all_weather, ignore_index=True)


    weather_df['snow_depth (m)'] = weather_df['snow_depth (m)'].fillna(0)

    weather_df.drop(labels=["location_id", "timezone", "timezone_abbreviation", "utc_offset_seconds"], axis=1, inplace=True)

    # weather_df.dropna(inplace=True)
    return weather_df

def split_file(file):
    with open(file, 'r') as f:
        lines = f.readlines()

    # find the index of the blank (space) row
    split_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "":   # blank line found
            split_idx = i
            break

    if split_idx is None:
        raise ValueError(f"No blank line found in file {file}")

    # read metadata up to the blank line
    meta = pd.read_csv(file, nrows=split_idx - 1)

    # read time series after the blank line
    ts = pd.read_csv(file, skiprows=split_idx + 1)

    return meta, ts

def unzip_weather_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".zip"):
            zip_path = os.path.join(folder_path, file)
            print(f"📦 Unzipping {zip_path} ...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
            print(f"✅ Unzipped: {file}")


def slice_time(file, n, chunksize=100_000):
    """
    Return rows from the last n years from a CSV, using chunked reading
    with a progress bar.
    """
    # find latest time
    latest_time = None
    total_rows = 0

    # total rows 
    with open(file, 'r') as f:
        total_rows = sum(1 for _ in f) - 1  # subtract header

    num_chunks = max(1, total_rows // chunksize + 1)
    
    print("Finding latest timestamp...")
    for chunk in tqdm(pd.read_csv(file, usecols=['time'], chunksize=chunksize), total=num_chunks):
        chunk['time'] = pd.to_datetime(chunk['time'])
        max_time = chunk['time'].max()
        if latest_time is None or max_time > latest_time:
            latest_time = max_time

    cutoff = latest_time - pd.DateOffset(years=n)
    
    # collect rows >= cutoff
    chunks = []
    print(f"Filtering rows from the last {n} years...")
    for chunk in tqdm(pd.read_csv(file, chunksize=chunksize), total=num_chunks):
        chunk['time'] = pd.to_datetime(chunk['time'])
        filtered = chunk[chunk['time'] >= cutoff]
        if not filtered.empty:
            chunks.append(filtered)
    
    df_last_n_years = pd.concat(chunks, ignore_index=True)
    return df_last_n_years


if __name__ == "__main__":
    # weather_folder = "./data_pipeline/weather_data/"

    # print("Loading weather data...")
    # weather_df = load_weather_data(weather_folder)

    # weather_df.to_csv("merged_weather.csv", index=False)

    merged_file = "./merged_weather.csv"
    sliced_df = slice_time(merged_file, 2)

    sliced_df.to_csv("sliced_weather.csv", index=False)