from datetime import datetime
import pandas as pd 

class Interval:
    def __init__(self, start: datetime, end: datetime):
        if start > end:
            raise ValueError("Start time must be before end time.")
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Interval(start={self.start}, end={self.end})"

def t(s):
    return pd.to_datetime(f"2025-05-23 {s}", format="%Y-%m-%d %H:%M:%S")

