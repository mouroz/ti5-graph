import argparse

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from src.reader.merged.columns import *
from src.graph.simple_plot import *
from src.interval.interval import *


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
