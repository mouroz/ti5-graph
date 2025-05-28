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


def joint_csv(hw_input_csv: str, rpm_input_csv: str) -> pd.DataFrame:
    hw_df = pd.read_csv(hw_input_csv, usecols=Col.original_names(), index_col=False)
    rpm_df = pd.read_csv(rpm_input_csv, usecols=Col.original_names(), index_col=False)
    rpm_df.head()
    return pd.concat([hw_df, rpm_df], ignore_index=True)

def join_csv_files(base_csv_path, rpm_csv_path, output_path=None):
    # Read both CSV files
    base_df = pd.read_csv(base_csv_path)
    rpm_df = pd.read_csv(rpm_csv_path)
    
    # Convert 'Time' to string first, then create join key by removing milliseconds
    base_df['join_time'] = base_df['Date'].astype(str).str.split('.').str[0]
    
    # Create corresponding join key from rpm_base_manual.csv Timestamp column
    rpm_df['join_time'] = rpm_df['Timestamp']
    
    # Perform the join operation
    merged_df = pd.merge(base_df, rpm_df, on='join_time', how='inner')
    
    # Remove the temporary join column
    merged_df = merged_df.drop('join_time', axis=1)
    
    # Save the result if output path is provided
    if output_path:
        merged_df.to_csv(output_path, index=False)
        
    return fix_dataframe_inconsistencies(merged_df)

def fix_dataframe_inconsistencies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Fix gaps in the CSV file by:
    1. Converting timestamps to datetime format
    2. Filling in missing timestamps (when gap > 1 second) with interpolated rows
    3. Removing duplicates
    """
    # Ensure 'Timestamp' is in datetime format
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'], errors='coerce')
    
    # Also convert Date to datetime if it exists
    if 'Date' in dataframe.columns:
        dataframe['Date'] = pd.to_datetime(dataframe['Date'], errors='coerce')
    
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
            for sec in range(1, int(time_diff)):
                # Create a new row by copying the current row
                new_row = current_row.copy()
                
                # Update Timestamp
                new_row['Timestamp'] = current_row['Timestamp'] + pd.Timedelta(seconds=sec)
                
                # Update Date if it exists
                if 'Date' in dataframe.columns:
                    new_row['Date'] = current_row['Date'] + pd.Timedelta(seconds=sec)
                
                # Update relativeTime if it exists (format: MM:SS)
                if 'relativeTime' in dataframe.columns:
                    # Parse the relative time
                    if isinstance(current_row['relativeTime'], str) and ':' in current_row['relativeTime']:
                        mins, secs = map(int, current_row['relativeTime'].split(':'))
                        total_secs = mins * 60 + secs + sec
                        new_mins = total_secs // 60
                        new_secs = total_secs % 60
                        new_row['relativeTime'] = f"{new_mins:02d}:{new_secs:02d}"
                
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
    
    return result_df


    
# Example usage
# result = join_csv_files('data/base_manual.csv', 'data/rpm_base_manual.csv', 'data/merged_data.csv')
# print(f"Joined data has {len(result)} rows")


