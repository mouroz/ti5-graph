import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.interval.split_frame import split_df_by_intervals_as_relative_time
from src.interval.interval import Interval
from src.implm.merged.columns import MergedCol
from src.implm.merged.db_math_regression import predict_with_model


dataFolder = os.path.join(os.path.dirname(__file__), 'data')
input_csv_folder = os.path.join(dataFolder, 'input')
output_csv_folder = os.path.join(dataFolder, 'output')
choice_output_folder = ''
tmp_folder = os.path.join(dataFolder, 'tmp')

hardwareInfo_csv_path = ''
java_csv_path = ''
merged_csv_path = os.path.join(tmp_folder, 'merged_data.csv')

_frames:list[pd.DataFrame] | None = None

def merge_csv_files(base_csv_path:str, java_csv_path:str) -> pd.DataFrame:
    # Read both CSV files
    base_df = pd.read_csv(base_csv_path, usecols=MergedCol.hardware_columns(), index_col=False)
    rpm_df = pd.read_csv(java_csv_path, usecols=MergedCol.fan_columns(), index_col=False)

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
    
    merged_df = MergedCol.rename_df(df=merged_df)
    return merged_df

def pc_rpm_columns_merge(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge PC RPM columns into a single column.
    """
    # Cria a coluna Velocidade fan pc como média dos valores de CPU [RPM] e GPU [RPM]
    if 'CPU [RPM]' in df.columns and 'GPU [RPM]' in df.columns:
        CPU_RPM = MergedCol.CPU_RPM.standard
        GPU_RPM = MergedCol.GPU_RPM.standard
        
        df[MergedCol.AVG_RPM.standard] = df[[CPU_RPM, GPU_RPM]].mean(axis=1)
        # Calcula a diferença absoluta entre CPU e GPU RPM
        df[MergedCol.ABS_RPM_DIFFERENCE.standard] = (df[CPU_RPM] - df[GPU_RPM]).abs()
        # Exibe estatísticas básicas da diferença
        print("Diferença média entre CPU e GPU fan (RPM):", df['Diferença fan (abs)'].mean())
        print("Diferença máxima:", df['Diferença fan (abs)'].max())
        print("Diferença mínima:", df['Diferença fan (abs)'].min())
    else:
        print("Colunas 'CPU [RPM]' e/ou 'GPU [RPM]' não encontradas no DataFrame.")

    return df

def fix_dataframe_inconsistencies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Fix gaps in the CSV file by:
    1. Converting timestamps to datetime format
    2. Filling in missing timestamps (when gap > 1 second) with interpolated rows
    3. Removing duplicates
    """
    # Ensure 'Timestamp' is in datetime format
    TIMESTAMP = MergedCol.TIMESTAMP.standard
    dataframe[TIMESTAMP] = pd.to_datetime(dataframe[TIMESTAMP], errors='coerce', format="%H:%M:%S")
    
    # Sort by 'Timestamp'
    dataframe = dataframe.sort_values(by=TIMESTAMP)
    
    # Create a list to hold the original and interpolated rows
    all_rows = []
    
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
                
                
                RELATIVE_TIME = MergedCol.RELATIVE_TIME.standard
                # Update relativeTime if it exists (format: MM:SS)
                if RELATIVE_TIME in dataframe.columns:
                    # Parse the relative time
                    if isinstance(current_row[RELATIVE_TIME], str) and ':' in current_row[RELATIVE_TIME]:
                        mins, secs = map(int, current_row[RELATIVE_TIME].split(':'))
                        total_secs = mins * 60 + secs + sec
                        new_mins = total_secs // 60
                        new_secs = total_secs % 60
                        new_row[RELATIVE_TIME] = f"{new_mins:02d}:{new_secs:02d}"
                
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
    result_df = result_df.drop_duplicates(subset=TIMESTAMP)
    
    # Sort again to ensure proper order
    result_df = result_df.sort_values(by=TIMESTAMP)
    
    # Reset index to ensure it is sequential
    result_df = result_df.reset_index(drop=True)

    # Convert 'Timestamp' back to string format HH:MM:SS
    result_df[TIMESTAMP] = result_df[TIMESTAMP].dt.strftime('%H:%M:%S')
    # result_df.drop(columns=['Unnamed: 294'], inplace=True, errors='ignore')

    # result_df.rename(columns={'RPM': 'Velocidade Fan Base'}, inplace=True)
    

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

def get_intervals_from_df(df: pd.DataFrame) -> list[Interval]:
    """
    Extracts the sequential intervals from the 'relativeTime' column of the DataFrame that IsTestRunning is true.
    Returns a list of Interval objects.
    """
    intervals = []
    
    start_time = None
    
    for i, row in df.iterrows():
        is_test_running = row[MergedCol.IS_TEST_RUNNING.standard]
        
        COL_RELATIVE_TIME = MergedCol.RELATIVE_TIME.standard
        relative_time = row[COL_RELATIVE_TIME]
        

        # If IsTestRunning is True and we don't have a start time, mark the start
        if is_test_running and start_time is None:
            start_time = relative_time
        
        # If IsTestRunning is False and we have a start time, mark the end and create interval
        elif not is_test_running and start_time is not None:
            # The end time is the previous row's time (last True value)
            if i > 0:
                end_time = df.iloc[i][COL_RELATIVE_TIME]
                intervals.append(Interval.from_range_string(f"{start_time} - {end_time}"))
                print(f"Interval added: {start_time} - {end_time}")
            start_time = None
    # Handle case where the DataFrame ends with IsTestRunning = True
    if start_time is not None:
        end_time = df.iloc[-1][COL_RELATIVE_TIME]
        intervals.append(Interval.from_range_string(f"{start_time} - {end_time}"))
        print(f"Final interval added: {start_time} - {end_time}")
    
    return intervals

def get_merged_frame(HW_info_csv:str, java_csv_path:str, output_final_file:str = None) -> pd.DataFrame:
    """
    Get the merged DataFrame from base and RPM CSV files.
    
    Parameters:
    - HW_info_csv: Path to the base CSV file.
    - java_csv_path: Path to the RPM CSV file.
    - interpolate: Whether to fill gaps in the data.
    
    Returns:
    - Merged DataFrame with fixed inconsistencies.
    """
    df = merge_csv_files(HW_info_csv, java_csv_path)
    df = pc_rpm_columns_merge(df)
    df = fix_dataframe_inconsistencies(df)
    df = predict_with_model(df)
    
    if output_final_file:
        df.to_csv(output_final_file, index=False)
        print(f"Merged DataFrame saved to {output_final_file}")
    
    return df

def get_splitted_frames(df: pd.DataFrame) -> list[pd.DataFrame]:
    """
    Split the DataFrame into smaller DataFrames based on intervals.
    Returns a list of DataFrames.
    """
 
    intervals = get_intervals_from_df(df)
    frames = split_df_by_intervals_as_relative_time(df, intervals, time_col=MergedCol.RELATIVE_TIME.standard)
    print(frames)
    # frames = []
    # for interval in intervals:
    #     start_time = interval.start
    #     end_time = interval.end
        
    #     print(df['relativeTime'].dtype)
        
        # # Filter the DataFrame for the current interval
        # mask = (df['relativeTime'] >= start_time) & (df['relativeTime'] <= end_time)
        # filtered_df = df[mask].copy()
        
        # if not filtered_df.empty:
        #     filtered_df.reset_index(drop=True, inplace=True)
        #     _frames.append(filtered_df)
        #     print(f"Frame created for interval: {start_time} - {end_time}")
    
    return frames


def get_splitted_frames_from_csv(Base_csv:str, java_csv_path:str = None, output_path:str = None) -> list[pd.DataFrame]:
    """
    Get the splitted DataFrames from base and RPM CSV files.
    
    Parameters:
    - Base_csv: Path to the base CSV file.
    - java_csv_path: Path to the RPM CSV file.
    
    Returns:
    - List of DataFrames split by intervals.
    """
    if java_csv_path is not None:
        df = get_merged_frame(Base_csv, java_csv_path, output_final_file=os.path.join(output_path, 'merged_data.csv'))
    else:
        df = pd.read_csv(Base_csv)
        
    
    return get_splitted_frames(df)