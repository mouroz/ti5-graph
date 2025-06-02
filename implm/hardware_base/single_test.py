import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.graph.simple_plot import *

from src.entries.interval import *
from src.reader.hardware_base.read_base_pipeline import *
from src.reader.hardware_base.base_columns import BaseCol
from src.reader.hardware_base.split_frame import BaseSplitFrames
import implm.hardware_base.get_entries as get_entries
from src.entries.entries_frame import *
from src.entries.create_entries import *



class SingleTest:
    
    _frames:BaseSplitFrames | None = None
    
    def __init__(self, input_csv: str, intervals:list[Interval], output_prefix: str|None = None):
        frames = get_entries.get_frames(
            input_csv=input_csv, 
            intervals=intervals, 
            output_prefix=output_prefix                                          
        )
        
        self._frames = frames
    
    @staticmethod
    def get_frames(
        input_csv:str, 
        intervals:list[Interval], 
        output_prefix:str|None, 
    ) -> BaseSplitFrames:
    
        base:BaseFrame = BaseFrame.get_base_frame(base_csv_path=input_csv)
        df:pd.DataFrame = base.df
        
        frames:list[pd.DataFrame] = split_df_by_intervals(df, intervals)
        entries:EntriesFrame = EntriesFrame(frames)
        
        if (output_prefix is not None):
            for i, chunk in enumerate(frames):
                output_path = f"{output_prefix}{i+1}.csv"
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
                chunk.to_csv(output_path, index=False)
            
            output_path = f"{output_prefix}_original.csv"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
            df.to_csv(output_path, index=False)

        
        return BaseSplitFrames(entries)

    
    def plot_cpu_percentage(self, img_path:str):
        y_series_list = self._frames.get_series(BaseCol.CPU_PERCENTAGE)
        x_series = pd.Series(range(len(y_series_list[0])))
        
        plot_multiple_std(
            y_series_list= y_series_list,
            x_series = x_series,
            labels=['caso 1', 'caso 2', 'caso 3', 'caso 4'],
            output=img_path,
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo',
            y_min=0,
            y_max=100
        )
        
    def test_plot_with_color(self, img_path:str):
        y_series_list = self._frames.get_series(BaseCol.CPU_PERCENTAGE)
        x_series = pd.Series(range(len(y_series_list[0])))
        
        y = pd.Series(np.sin(np.linspace(0, 20, len(y_series_list[0]))))
        mask = y > 0  # Just as an example condition
        
        plot_multiple_binary_mask(
            y_series_list=y_series_list,
            x_series=x_series,
            mask=mask,
            output=img_path,
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo',
            y_min=0,
            y_max=100
        )

    
    
    
    
    
