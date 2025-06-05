import src.implm.merged.columns as columns
import src.implm.merged.pipeline as pipeline

from interval.entries_frame import EntriesFrame
from interval.interval import Interval


def get_split_frames():
    df = columns.get_merged_frame(
        base_csv_path="data/merged/base.csv", 
        rpm_csv_path="data/merged/rpm.csv", 
        interpolate=False
    )
    
    intervals:list[Interval] = ...
    
    frames:EntriesFrame = EntriesFrame.from_intervals(df=df, intervals=intervals)
    
    
    