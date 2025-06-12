import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.interval.split_frame import split_df_by_intervals_as_relative_time
from src.interval.interval import Interval
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
    base_df = pd.read_csv(base_csv_path)
    rpm_df = pd.read_csv(java_csv_path)

    # Função para normalizar o tempo para HH:MM:SS
    def normalize_time_str(t):
        parts = t.split(':')
        # Garante que temos 3 partes (HH, MM, SS)
        parts = [p.zfill(2) for p in parts]
        while len(parts) < 3:
            parts.insert(0, '00')
        return ':'.join(parts)
    
    # Convert 'Time' to string first, then create join key by removing milliseconds
    base_df['join_time'] = base_df['Time'].astype(str).str.split('.').str[0]
    
    # Normalize the time strings to HH:MM:SS format
    base_df['join_time'] = base_df['join_time'].apply(normalize_time_str)

    # Create corresponding join key from rpm_base_manual.csv Timestamp column
    rpm_df['join_time'] = rpm_df['Timestamp']
    
    # Perform the join operation
    merged_df = pd.merge(base_df, rpm_df, on='join_time', how='inner')
    
    # Remove the temporary join column
    merged_df = merged_df.drop('join_time', axis=1)
    merged_df = merged_df.drop('Time', axis=1, errors='ignore') 
    return merged_df

def pc_rpm_columns_merge(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge PC RPM columns into a single column.
    """
    # Cria a coluna Velocidade fan pc como média dos valores de CPU [RPM] e GPU [RPM]
    if 'CPU [RPM]' in df.columns and 'GPU [RPM]' in df.columns:
        df['Velocidade Fan PC'] = df[['CPU [RPM]', 'GPU [RPM]']].mean(axis=1)
        # Calcula a diferença absoluta entre CPU e GPU RPM
        df['Diferença fan (abs)'] = (df['CPU [RPM]'] - df['GPU [RPM]']).abs()
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
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'], errors='coerce', format="%H:%M:%S")
    
    # Sort by 'Timestamp'
    dataframe = dataframe.sort_values(by='Timestamp')

    # Remove duplicates based on 'Timestamp'
    dataframe = dataframe.drop_duplicates(subset='Timestamp')
    
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
    
    # Sort again to ensure proper order
    result_df = result_df.sort_values(by='Timestamp')
    
    # Reset index to ensure it is sequential
    result_df = result_df.reset_index(drop=True)

    # Convert 'Timestamp' back to string format HH:MM:SS
    result_df['Timestamp'] = result_df['Timestamp'].dt.strftime('%H:%M:%S')
    # result_df.drop(columns=['Unnamed: 294'], inplace=True, errors='ignore')

    result_df.rename(columns={'RPM': 'Velocidade Fan Base'}, inplace=True)

    return result_df

def get_intervals_from_df(df: pd.DataFrame) -> list[Interval]:
    """
    Extracts the sequential intervals from the 'relativeTime' column of the DataFrame that IsTestRunning is true.
    Returns a list of Interval objects.
    """
    intervals = []
    
    start_time = None
    
    for i, row in df.iterrows():
        is_test_running = row['IsTestRunning']
        relative_time = row['relativeTime']
        

        # If IsTestRunning is True and we don't have a start time, mark the start
        if is_test_running and start_time is None:
            start_time = relative_time
        
        # If IsTestRunning is False and we have a start time, mark the end and create interval
        elif not is_test_running and start_time is not None:
            # The end time is the previous row's time (last True value)
            if i > 0:
                end_time = df.iloc[i]['relativeTime']
                intervals.append(Interval.from_range_string(f"{start_time} - {end_time}"))
                print(f"Interval added: {start_time} - {end_time}")
            start_time = None
    # Handle case where the DataFrame ends with IsTestRunning = True
    if start_time is not None:
        end_time = df.iloc[-1]['relativeTime']
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
    frames = split_df_by_intervals_as_relative_time(df, intervals, time_col='relativeTime')
    #print(frames)
    
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