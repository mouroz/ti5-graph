import argparse

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from src.columns import *
from src.graph.simple_plot import *
from src.entries.reader import *
from src.entries.interval import *


def split_df_by_intervals(df: pd.DataFrame, intervals: list[Interval]) -> list[pd.DataFrame]:
    """
    Splits the dataframe into parts based on a list of Interval(start, end).
    Throws ValueError if there are rows in df[time_col] not covered by any interval.
    """
    chunks = []
    
    if not interval_matching_length(intervals):
        details = ", ".join(
            f"#{i}:len={interval.len()}" for i, interval in enumerate(intervals)
        )
        raise ValueError(f"Not all chunks have the same number of rows. Intervals: [{details}]")
    
    
    for interval in intervals:
        print(f"Interval from {interval.start} to {interval.end}")
        
        chunk = df.iloc[interval.start : interval.end + 1].copy()
        chunks.append(chunk)

    return chunks




def get_cases_from_csv(input_csv: str, output_prefix: str, intervals: list[Interval], save_as_csv: bool) -> list[pd.DataFrame]:
    df = read_csv(input_csv)
    # print(df.head())
    # print(df.columns)
    # print(df.info())

    
    results:list[pd.DataFrame] = split_df_by_intervals(df, intervals)
    
    updated:list[pd.DataFrame] = []
    for i, chunk in enumerate(results):
        chunk = manipulate_cases_df(chunk)
        
        if (save_as_csv):
            output_path = f"{output_prefix}{i+1}.csv"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
            chunk.to_csv(output_path, index=False)

        updated.append(chunk)

    if (save_as_csv):
        output_path = f"{output_prefix}_original.csv"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
        df.to_csv(output_path, index=False)
    return updated

