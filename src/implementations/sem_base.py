import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.columns import *
from src.entries.csv_split import *
from src.graph.simple_plot import *
from src.entries import *



intervals = [
    #Interval.from_range_string("1:21 - 3:02"),
    Interval.from_range_string("3:29 - 5:01"),
    #Interval.from_range_string("6:29 - 7:01"), INVALIDO
    Interval.from_range_string("7:33 - 9:05"),
    Interval.from_range_string("9:40 - 11:12"),
    Interval.from_range_string("11:58 - 13:30")
]


class SemBase:
    input_csv_path = 'data/sem_base.csv'
    image_path = 'example/output.png'
    output_prefix = 'data/sem_base/test'
    
    _frames:list[pd.DataFrame] | None = None
    
    @staticmethod
    def get_frames() -> list[pd.DataFrame]:
        if SemBase._frames is None:
            SemBase._frames = get_cases_from_csv(
                input_csv=SemBase.input_csv_path, 
                output_prefix=SemBase.output_prefix, 
                intervals=intervals, 
                save_as_csv=True
            )
        
        return SemBase._frames
    
    @staticmethod
    def get_series_mean(col: Col) -> pd.Series:
        return mean_of_dataframe_list(SemBase.get_frames())
    
    

    @staticmethod
    def plot_cpu_percentage():
        frames = SemBase.get_frames()
        y_series_list = get_series_from_frames(frames, Col.CPU_PERCENTAGE)
        x_series = pd.Series(range(len(y_series_list[0])))
        
        plot_multiple_std(
            y_series_list= y_series_list,
            x_series = x_series,
            labels=['caso 1', 'caso 2', 'caso 3', 'caso 4'],
            output=SemBase.output_prefix,
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo',
            y_min=0,
            y_max=100
        )
        
    def test_plot_with_color():
        frames = SemBase.get_frames()
        y_series_list = get_series_from_frames(frames, Col.CPU_PERCENTAGE)
        x_series = pd.Series(range(len(y_series_list[0])))
        
        y = pd.Series(np.sin(np.linspace(0, 20, len(y_series_list[0]))))
        mask = y > 0  # Just as an example condition
        
        plot_multiple_binary_mask(
            y_series_list=y_series_list,
            x_series=x_series,
            mask=mask,
            output=SemBase.output_prefix+"_color",
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo',
            y_min=0,
            y_max=100
        )
if __name__ == '__main__':  
    SemBase.plot_cpu_percentage()
    SemBase.test_plot_with_color()

    

    
    
    
    
    
