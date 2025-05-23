import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.columns import *
from src.graph_plot import *
from src.entries.reader import *

def time_str_to_seconds(s: str) -> int:
    minutes, seconds = map(int, s.strip().split(":"))
    return minutes * 60 + seconds

class Interval:
    def __init__(self, start: int, end: int):
        if start > end:
            raise ValueError("Start time must be before end time.")
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Interval(start={self.start}, end={self.end})"
    
    def len(self) -> int:
        return self.end-self.start+1
     
    @staticmethod
    def from_time_strings(start_str: str, end_str: str) -> "Interval":
        def time_str_to_seconds(s: str) -> int:
            minutes, seconds = map(int, s.strip().split(":"))
            return minutes * 60 + seconds

        start_sec = time_str_to_seconds(start_str)
        end_sec = time_str_to_seconds(end_str)
        return Interval(start_sec, end_sec)

    @staticmethod
    def from_range_string(s: str) -> "Interval":
        parts = s.strip().split("-")
        if len(parts) != 2:
            raise ValueError("Expected format 'MM:SS - MM:SS'")
        start_str, end_str = parts[0].strip(), parts[1].strip()
        return Interval.from_time_strings(start_str, end_str)


def interval_matching_length(intervals: list[Interval]) -> bool:
    return all(i.len() == intervals[0].len() for i in intervals)





def split_df_by_intervals(df: pd.DataFrame, intervals: list[Interval]) -> list[pd.DataFrame]:
    """
    Splits the dataframe into parts based on a list of Interval(start, end).
    Throws ValueError if there are rows in df[time_col] not covered by any interval.
    """
    chunks = []
    covered_indices = set()
    time_col: str = Col.TIMESTAMP.standard
    
    if not interval_matching_length(intervals):
        details = ", ".join(
            f"#{i}:len={interval.len()}" for i, interval in enumerate(intervals)
        )
        raise ValueError(f"Not all chunks have the same number of rows. Intervals: [{details}]")
    
    
    for interval in intervals:
        print(f"Interval from {interval.start} to {interval.end}")
        
        chunk = df.iloc[interval.start : interval.end + 1].copy()
        covered_indices.update(range(interval.start, interval.end + 1))
        chunks.append(chunk)

    return chunks




def get_cases_from_csv(input_csv: str, output_prefix: str, intervals: list[Interval], save_as_csv: bool) -> list[pd.DataFrame]:
    df = read_csv(input_csv)
    manipulate_whole_df(df)
    
    results:list[pd.DataFrame] = split_df_by_intervals(df, intervals)
    
    updated:list[pd.DataFrame] = []
    for i, chunk in enumerate(results):
        chunk = manipulate_cases_df(chunk)
        
        if (save_as_csv):
            output_path = f"{output_prefix}{i+1}.csv"
            chunk.to_csv(output_path, index=False)

        updated.append(chunk)

    if (save_as_csv):
        output_path = f"{output_prefix}_all.csv"
        df.to_csv(output_path, index=False)
    return updated

