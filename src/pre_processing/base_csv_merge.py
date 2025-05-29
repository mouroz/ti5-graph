import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.columns import *
from src.entries.csv_split import *
from src.graph_plot import *
from src.entries import *

def join_csv_files(base_csv_path:str, rpm_csv_path:str, output_path=None) -> pd.DataFrame:
    # Read both CSV files
    base_df = pd.read_csv(base_csv_path)
    rpm_df = pd.read_csv(rpm_csv_path)

    # Remove last line of base_df
    if not base_df.empty and base_df.iloc[-1].isnull().all():
        base_df = base_df[:-1]
    
    # Convert 'Time' to string first, then create join key by removing milliseconds
    base_df['join_time'] = base_df['Time'].astype(str).str.split('.').str[0]
    
    # Create corresponding join key from rpm_base_manual.csv Timestamp column
    rpm_df['join_time'] = rpm_df['Timestamp']
    
    # Perform the join operation
    merged_df = pd.merge(base_df, rpm_df, on='join_time', how='inner')
    
    # Remove the temporary join column
    merged_df = merged_df.drop('join_time', axis=1)
    merged_df = merged_df.drop('Time', axis=1, errors='ignore') 
    
    final_df = fix_dataframe_inconsistencies(merged_df)
    # Save the result if output path is provided
    if output_path:
        final_df.to_csv(output_path, index=False)
        
    return final_df

def fix_dataframe_inconsistencies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Fix gaps in the CSV file by:
    1. Converting timestamps to datetime format
    2. Filling in missing timestamps (when gap > 1 second) with interpolated rows
    3. Removing duplicates
    """
    # Ensure 'Timestamp' is in datetime format
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'], errors='coerce', format="%H:%M:%S")
    
    # Sort by 'Timestamp'
    dataframe = dataframe.sort_values(by='Timestamp')
    
    # Create a list to hold the original and interpolated rows
    all_rows = []
    
    # Process rows to fill gaps
    for i in range(len(dataframe) - 1):
        current_row = dataframe.iloc[i].copy()
        next_row = dataframe.iloc[i+1]
        
        all_rows.append(current_row)
        
        # Calculate the time difference in seconds
        time_diff = (next_row['Timestamp'] - current_row['Timestamp']).total_seconds()
        
        # If gap is more than 1 second, create interpolated rows
        if time_diff > 1.0:
            print(f"Filling gap of {time_diff} seconds between {current_row['Timestamp']} and {next_row['Timestamp']}")
            for sec in range(1, int(time_diff)):
                # Create a new row by copying the current row
                new_row = current_row.copy()
                
                # Update Timestamp
                new_row['Timestamp'] = current_row['Timestamp'] + pd.Timedelta(seconds=sec)
                
                # Update relativeTime if it exists (format: MM:SS)
                if 'relativeTime' in dataframe.columns:
                    # Parse the relative time
                    if isinstance(current_row['relativeTime'], str) and ':' in current_row['relativeTime']:
                        mins, secs = map(int, current_row['relativeTime'].split(':'))
                        total_secs = mins * 60 + secs + sec
                        new_mins = total_secs // 60
                        new_secs = total_secs % 60
                        new_row['relativeTime'] = f"{new_mins:02d}:{new_secs:02d}"
                
                # Reset the index so the new row does not keep the original index
                new_row = new_row.copy()
                new_row.name = None  # Remove the index name
                
                all_rows.append(new_row)
    
    # Add the last row
    if len(dataframe) > 0:
        all_rows.append(dataframe.iloc[-1])
    
    # Create a new DataFrame from all rows
    result_df = pd.DataFrame(all_rows)

    # Remove duplicates based on 'Timestamp'
    result_df = result_df.drop_duplicates(subset='Timestamp')
    
    # Sort again to ensure proper order
    result_df = result_df.sort_values(by='Timestamp')
    
    # Reset index to ensure it is sequential
    result_df = result_df.reset_index(drop=True)

    # Convert 'Timestamp' back to string format HH:MM:SS
    result_df['Timestamp'] = result_df['Timestamp'].dt.strftime('%H:%M:%S')
    # result_df.drop(columns=['Unnamed: 294'], inplace=True, errors='ignore')

    # # ensure 'relativeTime' is correctly crescent
    # for i in range(0, len(result_df)-1, 1):
    #     new_time = i
    #     new_mins = new_time // 60
    #     new_secs = new_time % 60
    #     result_df.at[i, 'relativeTime'] = f"{new_mins:02d}:{new_secs:02d}"


    # Use a public approach to deduplicate column names
    # def deduplicate_columns(cols):
    #     seen = {}
    #     new_cols = []
    #     for col in cols:
    #         if col not in new_cols:
    #             seen[col] = 0
    #             new_cols.append(col)
    #             # print(f"Column name {col} is unique.")
    #         else:
    #             seen[col] += 1
    #             new_cols.append(f"{col}_{seen[col]}")
    #             print(f"Duplicate column name found: {col}. Renaming to {new_cols[-1]}")
    #     return new_cols
    # result_df.columns = deduplicate_columns(result_df.columns)

    return result_df


    
# Example usage
# result = join_csv_files('data/base_manual.csv', 'data/rpm_base_manual.csv', 'data/merged_data.csv')
# print(f"Joined data has {len(result)} rows")


