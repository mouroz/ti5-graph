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
    #Interval.from_range_string("1:23 - 3:05"),
    Interval.from_range_string("3:35 - 5:07"),
    Interval.from_range_string("5:50 - 7:22"), 
    Interval.from_range_string("8:00 - 9:32"),
    Interval.from_range_string("9:56 - 11:28"),
    Interval.from_range_string("12:02 - 13:34")
]



class BaseAutomatica:
    input_csv_path = 'data/base_automatica.csv'
    image_path = 'example/output.png'
    output_prefix = 'data/base_automatica/test'
    
    _frames:list[pd.DataFrame] | None = None
    
    @staticmethod
    def get_frames():
        if BaseAutomatica._frames is None:
            BaseAutomatica._frames = get_cases_from_csv(
                input_csv=BaseAutomatica.input_csv_path, 
                output_prefix=BaseAutomatica.output_prefix, 
                intervals=intervals, 
                save_as_csv=True
            )
        
        return BaseAutomatica._frames
    
    @staticmethod
    def get_series_mean(col: Col) -> pd.Series:
        return mean_of_dataframe_list(BaseAutomatica.get_frames())
    
    

    @staticmethod
    def plot_cpu_percentage():
        frames = BaseAutomatica.get_frames()
        y_series_list = get_series_from_frames(frames, Col.CPU_PERCENTAGE)
        x_series = pd.Series(range(len(y_series_list[0])))
        
        plot_multiple_std(
            y_series_list= y_series_list,
            x_series = x_series,
            labels=['caso 1', 'caso 2', 'caso 3', 'caso 4', 'caso 5'],
            output=BaseAutomatica.image_path,
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo',
            y_min=0,
            y_max=100
        )
        
    
if __name__ == '__main__':  
    BaseAutomatica.plot_cpu_percentage()

    

    
    
    
    
    
