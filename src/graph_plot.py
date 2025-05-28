import pandas as pd
import matplotlib.pyplot as plt
# from columns import *
from src.columns import *


def plot_multiple_std(
    x_series: pd.Series,
    y_series_list: list[pd.Series],
    labels: list[str] | None,
    output: str, 
    x_label: str, 
    y_label: str, 
    title: str
):
    """
    Plots time series data.
    If group_col is specified, plots one line per group.
    """
    plot_multiple_std(x_series, y_series_list, labels, output, x_label, y_label, title)


def plot_multiple_std(
    x_series: pd.Series,
    y_series_list: list[pd.Series],
    labels: list[str] | None,
    output: str, 
    x_label: str, 
    y_label: str, 
    title: str
):
    """
    Plots time series data.
    If group_col is specified, plots one line per group.
    """

    plt.figure(figsize=(15, 5))
    
    for i, y_series in enumerate(y_series_list):
        if labels is None:
            plt.plot(x_series, y_series)
        else:
            plt.plot(x_series, y_series, label=labels[i])

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    if labels is not None:
        plt.legend(loc='upper right')  # simple, top right inside
    plt.tight_layout()
    print(output)
    plt.savefig(output)




def plot_std(
    x_series: pd.Series,
    y_series: pd.Series,
    label: None,
    output: str, 
    x_label: str, 
    y_label: str, 
    title: str
):
    plot_multiple_std(
        x_series= x_series,
        y_series_list=[y_series],
        labels=[label],
        output=output,
        x_label=x_label,
        y_label=y_label,
        title=title
    )
    
    

#-------------------------------------------------------------


def plot_all_cases(
    frames: list[pd.DataFrame], 
    col: Col, 
    labels:list[str], 
    output:str, 
    x_label:str, 
    y_label:str, 
    title:str
):
    print(f"Plotting {len(frames)} cases for column {col.standard}")

    print(f"lines: {frames[0]}")

    y_series:list[pd.Series] = []
    for frame in frames:
        y_series.append(frame[col.standard])
    
    
    x_series = pd.Series(range(len(y_series[0])))
    plot_multiple_std(
        x_series=x_series, 
        y_series_list=y_series, 
        labels=labels, 
        output=output, 
        x_label=x_label, 
        y_label=y_label, 
        title=title
    )
        