import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.columns import *

import chardet

def custom_time_parser(time_str):
    print(f'str: {time_str}')
    return datetime.strptime(time_str, "%H:%M:%S.%f").time()

def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV with predefined dtypes and datetime parsing.
    Modify `dtype_map` and `parse_dates` as per your CSV structure.
    """

    # Detect proper charset
    # with open(file_path, 'rb') as f:
    #     result = chardet.detect(f.read())
    #     print(result)

    df = pd.read_csv(file_path, usecols=Col.original_names(), index_col=False)
    df = df.rename(columns=Col.rename_map())
        
    # Debug info
    # print(df.head())
    # print(df.columns)
    # print(df.info())
    
    return df

#---------------------------------------------------

def convert_to_datetime(time_obj):
    return datetime.combine(datetime.today(), time_obj)

# Define general logic for updated df
def manipulate_whole_df(df: pd.DataFrame) -> pd.DataFrame:
    # print(df[Col.TIMESTAMP.standard].dtype)
    # print(df[Col.TIMESTAMP.standard].iloc[0])
    # df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(lambda x: datetime.strptime(x, "%H:%M:%S.%f").time())
    # df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(convert_to_datetime)
    return df


def manipulate_cases_df(df: pd.DataFrame) -> pd.DataFrame:
    #df = df.drop(columns=[Col.TIMESTAMP.standard])
    return df


def mean_of_series_list(series_list: list[pd.Series]) -> pd.Series:
    # Combine all series into a DataFrame (each series is one column)
    df = pd.concat(series_list, axis=1)
    # Calculate mean along the rows (axis=1)
    return df.mean(axis=1)
        
    
def mean_of_dataframe_list(df_list: list[pd.DataFrame], col: Col) -> pd.Series:
    series:list[pd.Series] = []
    
    for frame in df_list:
        series.append(frame[col.standard]) 
    
    return mean_of_series_list(series)
    

def get_series_from_frames(frames: list[pd.DataFrame], col: Col):
    y_series:list[pd.Series] = []
    for frame in frames:
        y_series.append(frame[col.standard])
    return y_series


            
    
