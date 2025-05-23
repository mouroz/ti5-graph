import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.columns import *
from src.entry_interval import *
from src.graph_plot import *
from src.entries import *



sem_base = [
    #Interval(t("15:44:07"), t("15:45:48")),
    Interval(t("15:46:15"), t("15:47:47")),
    Interval(t("15:48:15"), t("15:49:47")), 
    Interval(t("15:50:19"), t("15:51:51")),
    Interval(t("15:52:26"), t("15:53:58")),
    Interval(t("15:54:44"), t("15:56:16"))
]

def get_sem_base_cases() -> list[pd.DataFrame]:
    input_csv_path = 'data/sem_base.csv'
    image_path = 'example/output.png'
    output_prefix = 'data/sem_base/test'
    

    frames:list[pd.DataFrame] = get_cases_from_csv(
        input_csv=input_csv_path, 
        output_prefix=output_prefix, 
        intervals=sem_base, 
        save_as_csv=True
    )
    
    return frames


def plot_cpu_percentage(frames: list[pd.DataFrame]):
    y_series:list[pd.Series] = []
    for frame in frames:
        y_series.append(frame[Col.CPU_PERCENTAGE.standard])
    
    
    x_series = pd.Series(range(len(y_series[0])))
    plot_multiple_std(
        x_series=x_series, 
        y_series_list=y_series, 
        labels=["caso 1", "caso 2", "caso 3", "caso 4", "caso 5"], 
        output='example/output.png', 
        x_label='Segundos', 
        y_label='CPU %', 
        title='CPU % sobre tempo' 
    )
        

    
if __name__ == '__main__':  
    frames:list[pd.DataFrame] = get_sem_base_cases()
    plot_cpu_percentage(frames=frames)
    
    

    
    
    
    
    
