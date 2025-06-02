import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.reader.merged.merged_columns import *
from src.entries.create_entries import *
from src.entries import *
from src.reader.merged.merged_columns import BASE_TIMESTAMP, RPM_TIMESTAMP
from src.reader.merged.read_merged_pipeline import *
    
class InvalidTimestampError(ValueError):
    pass






    
def join_csv_files(base_csv_path:str, rpm_csv_path:str) -> RawMergeFrame:
    """
    Merges two CSV files based on their timestamps.
    The join criterion is based on equal timestamp between the frames by seconds floor aproximation
    
    Raises:
        ValueError: If columns Timestamp and Time does not exist for their respective
        dataframes base, rpm, and if they do not contain valid timestamps.
    
    Returns:
        Dataframe with merged values. If no values are merged, return an empty dataframe
    """
    # Read both CSV files
    try:
        base_df = pd.read_csv(base_csv_path)
        rpm_df = pd.read_csv(rpm_csv_path)
        
    except pd.errors.ParserError as e:  
        raise ValueError(f"Error parsing the CSV file: {e}")
    
    except KeyError as e:
        raise ValueError(f"Missing required columns in the CSV file: {e}")
    
    except FileNotFoundError:
        raise ValueError(f"The file {base_csv_path} does not exist.")
    
    
    
    # Remove last line of base_df
    if not base_df.empty and base_df.iloc[-1].isnull().all():
        base_df = base_df[:-1]
    
    if BASE_TIMESTAMP not in base_df.columns or RPM_TIMESTAMP not in rpm_df.columns:
        raise KeyError("Missing required columns in input DataFrame.")    
    
    try:
        timestamp_format = "%H:%M:%S"  # Adjust as needed
        
        # Parse and strip milliseconds from timestamps
        base_df['join_time'] = pd.to_datetime(
            base_df[BASE_TIMESTAMP], format='mixed', errors='raise'
        ).dt.strftime('%H:%M:%S')
        
        rpm_df['join_time'] = pd.to_datetime(
            rpm_df[RPM_TIMESTAMP], format='mixed', errors='raise'
        ).dt.strftime('%H:%M:%S')

            
    except Exception as e:
        raise InvalidTimestampError(f"Invalid timestamp encountered: {e}")

    
    # Perform the join operation
    merged_df = pd.merge(base_df, rpm_df, on='join_time', how='inner')
    
    # Remove the temporary join column
    merged_df = merged_df.drop('join_time', axis=1)
    
    
    
    if RPM_TIMESTAMP == MergedCol.TIMESTAMP.standard:
        merged_df = merged_df.drop(BASE_TIMESTAMP, axis=1, errors='ignore') 
        
    elif BASE_TIMESTAMP == MergedCol.TIMESTAMP.standard:
        merged_df = merged_df.drop(RPM_TIMESTAMP, axis=1, errors='ignore')
        
    else:
        raise ValueError(f"Unexpected timestamp columns: {BASE_TIMESTAMP} and {RPM_TIMESTAMP}.")
    
    
    return RawMergeFrame(merged_df)



def verify_join_csv_files(wrapper: RawMergeFrame) -> MergedColumnEnsuredFrame:
    """
    Ensures that the panda result contain all the columns defined in the Col class,
    and if needed if their types match
    
    Raises:
        ValueError: If the DataFrame does not contain all required columns or if the columns
        contain invalid types as specificed in the Col class.
    """
    
    MergedCol.validate_columns(df=wrapper.df)
    wrapper = MergedCol.drop_unlisted_columns(wrapper)
    return MergedColumnEnsuredFrame(wrapper.df)
    



def fix_dataframe_inconsistencies(wrapper: MergedColumnEnsuredFrame) -> MergedCleanFrame:
    """
    Fix gaps in the CSV file by:
    1. Converting timestamps to datetime format
    2. Filling in missing timestamps (when gap > 1 second) with interpolated rows
    3. Removing duplicates
    """
    
    dataframe = wrapper.df
    TIMESTAMP = MergedCol.TIMESTAMP.original
    
    
    # Remove duplicates based on 'Timestamp'
    dataframe = dataframe.drop_duplicates(subset=TIMESTAMP)
    
    # Sort 
    dataframe = dataframe.sort_values(by=TIMESTAMP)
    
    # Reset index to ensure it is sequential
    dataframe = dataframe.reset_index(drop=True)


    return MergedCleanFrame(dataframe)



# Optional step for cleaned frame. Not required for the next steps
def interpolate_missing_timestamps(wrapper: MergedCleanFrame) -> MergedCleanFrame:
    
    dataframe = wrapper.df
    
    # Create a list to hold the original and interpolated rows
    all_rows = []
    
    TIMESTAMP = MergedCol.TIMESTAMP.original
    RELATIVETIME = MergedCol.RELATIVE_TIME.original
    
    # Process rows to fill gaps
    for i in range(len(dataframe) - 1):
        current_row = dataframe.iloc[i].copy()
        next_row = dataframe.iloc[i+1]
        
        all_rows.append(current_row)
        
        # Calculate the time difference in seconds
        time_diff = (next_row[TIMESTAMP] - current_row[TIMESTAMP]).total_seconds()
        
        # If gap is more than 1 second, create interpolated rows
        if time_diff > 1.0:
            print(f"Filling gap of {time_diff} seconds between {current_row[TIMESTAMP]} and {next_row[TIMESTAMP]}")
            for sec in range(1, int(time_diff)):
                # Create a new row by copying the current row
                new_row = current_row.copy()
                
                # Update Timestamp
                new_row[TIMESTAMP] = current_row[TIMESTAMP] + pd.Timedelta(seconds=sec)
                

                # Parse the relative time
                if isinstance(current_row[RELATIVETIME], str) and ':' in current_row[RELATIVETIME]:
                    mins, secs = map(int, current_row[RELATIVETIME].split(':'))
                    total_secs = mins * 60 + secs + sec
                    new_mins = total_secs // 60
                    new_secs = total_secs % 60
                    new_row[RELATIVETIME] = f"{new_mins:02d}:{new_secs:02d}"
                
                # Reset the index so the new row does not keep the original index
                new_row = new_row.copy()
                new_row.name = None  # Remove the index name
                
                all_rows.append(new_row)
                
                
    # Add the last row
    if len(dataframe) > 0:
        all_rows.append(dataframe.iloc[-1])
    
    # Create a new DataFrame from all rows
    result_df = pd.DataFrame(all_rows)
    
    return MergedCleanFrame(result_df)



def get_merged_frame(base_csv_path:str, rpm_csv_path:str, interpolate:bool) -> MergedRenamedFrame:
    """
    Merges two CSV files and returns a cleaned DataFrame.
    Expected errors from join_csv_files and verify_join_csv_files are thrown here
    """
    raw_wrapper: RawMergeFrame = join_csv_files(base_csv_path, rpm_csv_path)
    safe_wrapper: MergedColumnEnsuredFrame = verify_join_csv_files(raw_wrapper)
    cleaned_wrapper: MergedCleanFrame = fix_dataframe_inconsistencies(safe_wrapper)
    if interpolate:
        cleaned_wrapper = interpolate_missing_timestamps(cleaned_wrapper)
    
    renamed_wrapper = MergedCol.rename_columns(cleaned_wrapper)
    return renamed_wrapper




def save_merged_csv(
    base_csv_path: str, 
    rpm_csv_path: str, 
    output_path: str, 
    interpolate: bool = False
) -> MergedRenamedFrame:
    """
    Merges two CSV files and saves the result to a new CSV file.
    
    :param base_csv_path: Path to the base manual CSV file.
    :param rpm_csv_path: Path to the RPM base manual CSV file.
    :param output_path: Path to save the merged CSV file.
    :param interpolate: Whether to fill in missing timestamps with interpolated rows.
    :return: DataFrame containing the merged data.
    :raises InvalidTimestampError: If there are invalid timestamps in the input files.
    :raises KeyError: If the required columns are missing in the input files.
    """
    
    merged_frame = get_merged_frame(base_csv_path, rpm_csv_path, interpolate)
    merged_frame.df.to_csv(output_path, index=False)
    return merged_frame.df