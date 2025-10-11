import pandas as pd
import numpy as np

def reshape_population_data(file_path):
    """
    Reshape population data from wide to long format
    Each location will have 3 rows (2020, 2021, 2022)
    """
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Clean column names
    df.columns = ['location', '2020', '2021', '2022']
    
    # Remove commas from population numbers and convert to numeric
    for year in ['2020', '2021', '2022']:
        df[year] = df[year].astype(str).str.replace(',', '').astype(float)
    
    # Extract latitude and longitude from location column
    def extract_lat_lon(coord_str):
        if pd.isna(coord_str):
            return np.nan, np.nan
        try:
            coords = str(coord_str).split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lon = float(coords[1].strip())
                return lat, lon
            else:
                return np.nan, np.nan
        except:
            return np.nan, np.nan
    
    # Apply coordinate extraction
    coord_results = df['location'].apply(extract_lat_lon)
    df['latitude'] = coord_results.apply(lambda x: x[0])
    df['longitude'] = coord_results.apply(lambda x: x[1])
    
    # Drop rows with missing coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Round coordinates for merging
    df['lat_round'] = df['latitude'].round(2)
    df['lon_round'] = df['longitude'].round(2)
    
    # Reshape from wide to long format using melt
    long_df = pd.melt(
        df, 
        id_vars=['location', 'latitude', 'longitude', 'lat_round', 'lon_round'],
        value_vars=['2020', '2021', '2022'],
        var_name='year',
        value_name='population'
    )
    
    # Convert year to datetime (using July 1st as reference date)
    long_df['date'] = pd.to_datetime(long_df['year'] + '-07-01')
    
    # Sort by location and year
    long_df = long_df.sort_values(['location', 'year']).reset_index(drop=True)
    
    print(f"Original shape: {df.shape}")
    print(f"Reshaped shape: {long_df.shape}")
    print(f"Number of unique locations: {long_df['location'].nunique()}")
    
    return long_df

# Example usage and output
if __name__ == "__main__":
    # Assuming your file is named 'city_pop.csv'
    reshaped_df = reshape_population_data('city_pop.csv')
    
    print("\n📊 Sample of reshaped data:")
    print(reshaped_df.head(12))
    
    print("\n📈 Data structure info:")
    print(reshaped_df.info())
    
    # Show a specific location to demonstrate the structure
    sample_location = reshaped_df['location'].iloc[0]
    print(f"\n📍 Example of one location across all years:")
    print(reshaped_df[reshaped_df['location'] == sample_location])