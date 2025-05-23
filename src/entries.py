import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from columns import *
from src.entry_interval import *
from src.graph_plot import *


def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV with predefined dtypes and datetime parsing.
    Modify `dtype_map` and `parse_dates` as per your CSV structure.
    """

    df = pd.read_csv(file_path, usecols=Col.original_names())
    df = df.rename(columns=Col.rename_map())
    
    return df



def convert_to_datetime(time_obj):
    return datetime.combine(datetime.today(), time_obj)


def manipulate_whole_df(df: pd.DataFrame):
    df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(lambda x: datetime.strptime(x, "%H:%M:%S.%f").time())
    df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(convert_to_datetime)


    

def split_df_by_intervals(df: pd.DataFrame, intervals: list[Interval]) -> list[pd.DataFrame]:
    """
    Splits the dataframe into parts based on a list of Interval(start, end).
    Throws ValueError if there are rows in df[time_col] not covered by any interval.
    """
    chunks = []
    covered_indices = set()
    time_col: str = Col.TIMESTAMP.standard
    
    # print(df[time_col].dtype) 
    # print(type(df[time_col].iloc[0]))
    # print(type(intervals[0].start))
    # print(df[time_col].head(10)) 
    
    for interval in intervals:
        print(f"Interval from {interval.start} to {interval.end}")
        
        mask = (df[time_col] >= interval.start) & (df[time_col] <= interval.end)
        chunk = df[mask].copy()
        covered_indices.update(df[mask].index)
        chunks.append(chunk)

    # Check if all rows are covered
    
    row_counts = [chunk.shape[0] for chunk in chunks]
    if len(set(row_counts)) != 1:
        for i, count in enumerate(row_counts):
            print(f"Chunk {i} size: {count} rows")
        raise ValueError("Not all chunks have the same number of rows.")

    return chunks



# def time_to_seconds(df: pd.DateFrame):
#     # Set the first time as the reference
#     start_time = df[Col.TIMESTAMP.standard].iloc[0]
    
#     # Interval 
#     df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(
#         lambda dt: int((dt - start_time).total_seconds())
#     )
    


def get_cases_from_csv(input_csv: str, output_prefix: str, intervals: list[str], save_as_csv: bool) -> list[pd.DataFrame]:


    df = read_csv(input_csv)
    manipulate_whole_df(df)
    
    results:list[pd.DataFrame] = split_df_by_intervals(df, intervals)
    
    updated:list[pd.DataFrame] = []
    for i, chunk in enumerate(results):
        output_path = f"{output_prefix}{i+1}.csv"
        chunk = chunk.drop(columns=[Col.TIMESTAMP.standard])
        
        if (save_as_csv):
            chunk.to_csv(output_path, index=False)

        updated.append(chunk)

        
    return updated

        
    
    
    
    
    
    
