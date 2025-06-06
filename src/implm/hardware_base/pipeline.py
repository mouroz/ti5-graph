import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

import sys
import os


from src.implm.hardware_base.columns import BaseCol
from src.interval.split_frame import split_df_by_intervals_as_index
from src.interval.entries_frame import EntriesFrame
from src.interval.interval import Interval


def read_csv(base_csv_path:str) -> pd.DataFrame:
    print(base_csv_path)
    # Read both CSV files
    try:
        dataframe = pd.read_csv(base_csv_path, index_col=False, usecols=BaseCol.original_names())
        
    except pd.errors.EmptyDataError:
        raise ValueError("The provided CSV file is empty")
    
    except pd.errors.ParserError as e:  
        raise ValueError(f"Error parsing the CSV file: {e}")
    
    except KeyError as e:
        raise ValueError(f"Missing required columns in the CSV file: {e}")
    
    except FileNotFoundError:
        raise ValueError(f"The file {base_csv_path} does not exist.")
    
    
    # Remove duplicates based on 'Timestamp'
    dataframe = dataframe.drop_duplicates(subset=BaseCol.TIMESTAMP.value, keep='first')
    
    # Reset index to ensure it is sequential
    dataframe = dataframe.reset_index(drop=True)


    rename_map = BaseCol.rename_map()
    dataframe.rename(columns=rename_map, inplace=True)
    return dataframe




def get_entries_frame(base_csv_path:str, intervals:list[Interval], output_prefix:str|None) -> EntriesFrame:
    df:pd.DataFrame = read_csv(base_csv_path)
    frames:list[pd.DataFrame] = split_df_by_intervals_as_index(df, intervals)
    
    if (output_prefix is not None):
        for i, chunk in enumerate(frames):
            output_path = f"{output_prefix}{i+1}.csv"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
            chunk.to_csv(output_path, index=False)
        
        output_path = f"{output_prefix}_original.csv"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
        df.to_csv(output_path, index=False)

    return EntriesFrame(frames)



    