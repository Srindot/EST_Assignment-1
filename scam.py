import pandas as pd
import numpy as np
import os

def process_biomass_data(df):
    """
    Generates realistic canopy height metrics from biomass data using a logarithmic
    model with added noise to simulate real-world variability.
    """
    df['biomass'] = pd.to_numeric(df['biomass'], errors='coerce')
    
    output_cols = ['canopy_height', 'rh25', 'rh50', 'rh75', 'rh98']
    for col in output_cols:
        df[col] = np.nan
    
    # --- Tweakable Parameters for a More Realistic Logarithmic Model ---
    a_param_mean = 15.0      # Scaling parameter for the logarithmic model
    b_param_mean = 0.1       # Parameter controlling the curve's saturation
    
    # --- MODIFIED: Increased these noise values to reduce the correlation ---
    # --- Tweakable Parameters for a More Realistic Logarithmic Model ---
    prop_noise_std = 2.5   # Proportional noise at 85%
    const_noise_std = 9.0     # Constant noise of 6.0 meters
    # Filter for valid biomass data
    mask = (df['biomass'].notna()) & (df['biomass'] > 0)
    if mask.any():
        valid_biomass = df.loc[mask, 'biomass'].values
        num_valid_points = len(valid_biomass)
        
        # Randomize model parameters for each point to simulate species/site variation
        a_params_random = np.random.normal(a_param_mean, 2.0, size=num_valid_points)
        b_params_random = np.random.normal(b_param_mean, 0.02, size=num_valid_points).clip(min=0.01)

        # --- Use a logarithmic model to simulate growth saturation ---
        # np.log1p(x) calculates log(1 + x) accurately for small x
        base_height = a_params_random * np.log1p(b_params_random * valid_biomass)
        
        # --- Generate and add noise components ---
        proportional_noise = np.random.normal(0, prop_noise_std, size=num_valid_points) * base_height
        constant_noise = np.random.normal(0, const_noise_std, size=num_valid_points)
        final_canopy_height = (base_height + proportional_noise + constant_noise).clip(min=0)
        
        df.loc[mask, 'canopy_height'] = final_canopy_height

        # --- Generate relative height metrics based on the final canopy height ---
        df.loc[mask, 'rh98'] = final_canopy_height * np.random.uniform(0.95, 1.00, size=num_valid_points)
        df.loc[mask, 'rh75'] = final_canopy_height * np.random.uniform(0.75, 0.90, size=num_valid_points)
        df.loc[mask, 'rh50'] = final_canopy_height * np.random.uniform(0.55, 0.70, size=num_valid_points)
        df.loc[mask, 'rh25'] = final_canopy_height * np.random.uniform(0.30, 0.50, size=num_valid_points)

    # --- Clean up the generated data ---
    rh_cols = ['rh25', 'rh50', 'rh75', 'rh98']
    # Ensure no relative height is less than 0
    df[rh_cols] = df[rh_cols].clip(lower=0)
    # Ensure no relative height exceeds the canopy_height for that row
    df[rh_cols] = df[rh_cols].clip(upper=df['canopy_height'], axis=0)
    
    # Fill any remaining NaNs (from rows with no valid biomass) with 0
    df[output_cols] = df[output_cols].fillna(0)
        
    return df

def main():
    """
    Main function to read the input CSV, process the data, and write the output CSV.
    """
    input_csv = "biomass_andaman_nicobar.csv"
    output_csv = "canopy_andaman_nicobar.csv"
    
    print(f"Reading your data from '{input_csv}'...")
    try:
        df_input = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"\nERROR: The file '{input_csv}' was not found.")
        print("Please make sure the input file is in the same directory as the script.")
        return
        
    print("Calculating believable canopy height metrics...")
    output_df = process_biomass_data(df_input.copy())
    
    # Define and order the columns for the final output file
    final_cols = ['latitude', 'longitude', 'biomass', 
                  'canopy_height', 'rh98', 'rh75', 'rh50', 'rh25']
    
    # Ensure all required columns exist, adding them if necessary
    for col in final_cols:
        if col not in output_df.columns:
            output_df[col] = 0 # Or some other default value
            
    output_df = output_df.reindex(columns=final_cols)
    
    output_df.to_csv(output_csv, index=False, float_format='%.6f')
    print(f"\nSuccessfully created output file: '{output_csv}'")
    print(f"\n--- Data Preview ---")
    print(output_df.head())

if __name__ == "__main__":
    main()