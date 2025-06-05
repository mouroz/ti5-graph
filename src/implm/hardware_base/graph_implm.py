import pandas as pd
import numpy as np


from src.implm.hardware_base.columns import BaseCol
from src.interval.entries_frame import EntriesFrame

from src.graph.line_plot import plot_multiple_std
from src.graph.line_binary_mask_plot import plot_multiple_binary_mask
from src.graph.bar_plot import plot_avg_bars

def plot_cpu_percentage(frame:EntriesFrame, img_path:str):
    y_series_list = frame.get_series(BaseCol.CPU_PERCENTAGE.standard)
    print(y_series_list)
    x_series = pd.Series(range(len(y_series_list[0])))
    
    plot_multiple_std(
        y_series_list= y_series_list,
        x_series = x_series,
        labels=['caso 1', 'caso 2', 'caso 3', 'caso 4'],
        output=img_path,
        x_label='Segundos',
        y_label='Cpu %',
        title='Cpu % por segundo',
        y_min=30,
        y_max=100
    )
    
def test_plot_with_color(frame:EntriesFrame, img_path:str):
    y_series_list = frame.get_series(BaseCol.CPU_PERCENTAGE.standard)
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
        y_min=30,
        y_max=100
    )


def test_bar_avg(frame:EntriesFrame, img_path:str):
    y_series_list = frame.get_series(BaseCol.CPU_PERCENTAGE.standard)

    y = pd.Series(np.sin(np.linspace(0, 20, len(y_series_list[0]))))
    mask = y > 0  # Just as an example condition
    
    plot_avg_bars(
        y_series_list=y_series_list, 
        labels=['caso 1', 'caso 2', 'caso 3', 'caso 4'],
        output=img_path, y_label='Cpu %',
        title='Cpu % medio por caso'
    )

