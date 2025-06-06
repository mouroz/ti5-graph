import argparse

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from src.interval.interval import *

def interval_matching_length(intervals: list[Interval]) -> bool:
    return all(i.len() == intervals[0].len() for i in intervals)

def split_df_by_intervals_as_index(df: pd.DataFrame, intervals: list[Interval]) -> list[pd.DataFrame]:
    """
    Assumes each line on the tabble is divided by exactly one second
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


def parse_time_strings_to_seconds(series: pd.Series) -> pd.Series:
    """
    Converts a Series of time strings in 'M:SS' format to total seconds (as integers).
    """
    def convert(time_str):
        minutes, seconds = time_str.split(":")
        return int(minutes) * 60 + int(seconds)

    return series.apply(convert)


def split_df_by_intervals_as_relative_time(df: pd.DataFrame, intervals: list[Interval], time_col:str) -> list[pd.DataFrame]:
    """
    Splits the dataframe into parts based on a list of Interval(start, end).
    Throws ValueError if there are rows in df[time_col] not covered by any interval.
    """
    time_in_seconds = parse_time_strings_to_seconds(df[time_col])
    time_values = time_in_seconds.values

    chunks = []

    for interval in intervals:
        start_idx = time_values.searchsorted(interval.start, side='left')
        end_idx = time_values.searchsorted(interval.end, side='right') - 1

        if start_idx > end_idx:
            raise ValueError(f"No rows found in interval {interval.start}-{interval.end} seconds.")

        print(f"Interval {interval.start}s to {interval.end}s → rows {start_idx} to {end_idx}")
        chunks.append(df.iloc[start_idx:end_idx + 1].copy())

    return chunks
