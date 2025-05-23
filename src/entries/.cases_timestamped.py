import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.columns import *
from src.graph_plot import *
from src.entries.reader import *


# DEPRECIATED
class IntervalWithDatetime:
    def __init__(self, start: datetime, end: datetime):
        if start > end:
            raise ValueError("Start time must be before end time.")
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Interval(start={self.start}, end={self.end})"

# Function to convert string such as "15:48:15" into full timestamp
# The y/m/d are hard to predict, hence this is not a recommended approach
# Used to generate expected datetimes from strings
def t(s):
    return pd.to_datetime(f"2025-05-23 {s}", format="%Y-%m-%d %H:%M:%S")



# DEPRECIATED
def split_df_by_intervals(df: pd.DataFrame, intervals: list[IntervalWithDatetime]) -> list[pd.DataFrame]:
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



# DEPRECIATED
def get_cases_from_csv(input_csv: str, output_prefix: str, intervals: list[IntervalWithDatetime], save_as_csv: bool) -> list[pd.DataFrame]:
    df = read_csv(input_csv)
    manipulate_whole_df(df)
    
    results:list[pd.DataFrame] = split_df_by_intervals(df, intervals)
    
    updated:list[pd.DataFrame] = []
    for i, chunk in enumerate(results):
        output_path = f"{output_prefix}{i+1}.csv"
        chunk = manipulate_cases_df(chunk)
        
        if (save_as_csv):
            chunk.to_csv(output_path, index=False)

        updated.append(chunk)

        
    return updated


