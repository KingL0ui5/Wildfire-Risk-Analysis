import pandas as pd
import numpy as np

def reshape_population_data(file_path):
    """
    Reshape population data from wide to long format
    Each location will have 3 rows (2020, 2021, 2022)
    """
    # Read the CSV file
    df = pd.read_excel(file_path)
    print(df.shape)
    
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

    df.drop(labels=["location", "date"], axis=1, inplace=True)
    # Drop rows with missing coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Reshape from wide to long format using melt
    long_df = pd.melt(
        df, 
        id_vars=['latitude', 'longitude'],
        value_vars=['2020', '2021', '2022'],
        var_name='year',
        value_name='population'
    )
    
    
    # Convert year to datetime (using July 1st as reference date)
    long_df['date'] = pd.to_datetime(long_df['year'] + '-07-01')
    return long_df

# Example usage and output
if __name__ == "__main__":
    # Assuming your file is named 'city_pop.csv'
    reshaped_df = reshape_population_data('./data_pipeline/data/city_pop.xlsx')
    print(reshaped_df)
    print(reshaped_df.head())
    print(reshaped_df.tail())
    print(reshaped_df.info())
    print(reshaped_df.isna().sum())
    
    print("\n📊 Sample of reshaped data:")
    print(reshaped_df.head(12))
    
    print("\n📈 Data structure info:")
    print(reshaped_df.info())
    