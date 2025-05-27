import pandas as pd
import matplotlib.pyplot as plt
from src.columns import *
from src.graph.binary_mask_plot import *


def plot_multiple_std(
    x_series: pd.Series,
    y_series_list: list[pd.Series],
    labels: list[str] | None,
    output: str, 
    x_label: str, 
    y_label: str, 
    title: str,
    y_min: float | None = None,
    y_max: float | None = None
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
    
    
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)
        
    if labels is not None:
        plt.legend(loc='upper right')  # simple, top right inside
    
    plt.tight_layout()
    print(output)
    plt.savefig(output)

