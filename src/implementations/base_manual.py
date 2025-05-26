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
from src.graph_plot import *
from src.entries import *



intervals = [
    #Interval.from_range_string("1:21 - 3:02"),
    Interval.from_range_string("3:29 - 5:01"),
    #Interval.from_range_string("6:29 - 7:01"), INVALIDO
    Interval.from_range_string("7:33 - 9:05"),
    Interval.from_range_string("9:40 - 11:12"),
    Interval.from_range_string("11:58 - 13:30")
]


class Manual:
    input_csv_path = 'data/base_manual.csv'
    image_path = 'example/output.png'
    output_prefix = 'data/base_manual/test'
    
    _frames:list[pd.DataFrame] | None = None
    

    @staticmethod
    def get_frames() -> list[pd.DataFrame]:
        if Manual._frames is None:
            Manual._frames = get_cases_from_csv(
                input_csv=Manual.input_csv_path, 
                output_prefix=Manual.output_prefix, 
                intervals=intervals, 
                save_as_csv=True
            )
        
        return Manual._frames
    
    @staticmethod
    def get_series_mean(col: Col) -> pd.Series:
        return mean_of_dataframe_list(Manual.get_frames())
    

    @staticmethod
    def plot_cpu_percentage():
        frames = Manual.get_frames()
        plot_all_cases(
            frames=frames, 
            col=Col.CPU_PERCENTAGE,
            labels=['caso 1', 'caso 2', 'caso 3', 'caso 4', 'caso 5'],
            output=Manual.output_prefix,
            x_label='Segundos',
            y_label='Cpu %',
            title='Cpu % por segundo'
        )
        


    
if __name__ == '__main__':  
    Manual.plot_cpu_percentage()

    
    
    
    
