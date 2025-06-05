import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.columns import *
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