import pandas as pd
import matplotlib.pyplot as plt
from columns import *


def plot_steelblue_std(
    x_series: pd.Series,
    y_series: pd.Series,
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
    plt.plot(x_series, y_series, color='steelblue')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output)
    

def plot_steelblue_multiple_std(
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
    plt.savefig(output)
    



def plot_time_cpu_percentage(df: pd.DataFrame, output: str):
    plot_steelblue_std(
        output=output, 
        x_series= df[Col.TIMESTAMP.standard], 
        y_series= df[Col.CPU_PERCENTAGE.standard], 
        x_label='Segundos', y_label='CPU % Sobre Tempo',
        title='CPU % Sobre Tempo'
    )


def plot_time_cpu_temperature_enchanced(df: pd.DataFrame, output: str):
    plot_steelblue_std(
        output=output, 
        x_series= df[Col.TIMESTAMP.standard], 
        y_series= df[Col.CPU_TEMPERATURE_ENHANCED.standard], 
        x_label='Segundos', y_label='Temperatura °C',
        title='Temperatura da CPU sobre tempo'
    )


def plot_time_test(df: pd.DataFrame, output: str):
    cpu_temp_avg = df[Col.CPU_TEMPERATURE_ENHANCED.standard].mean()
    cpu_package_avg = df[Col.GPU_TEMPERATURE.standard].mean()
    
    plot_steelblue_multiple_std(
        output=output, 
        x_series= df[Col.TIMESTAMP.standard], 
        y_series_list= [
            df[Col.CPU_TEMPERATURE_ENHANCED.standard], 
            df[Col.GPU_TEMPERATURE.standard], 
        ],
        labels= [
            f"Cpu temperature, media = {cpu_temp_avg:.2f}",
            f"Gpu temperature, media = {cpu_package_avg:.2f}"
        ],
        x_label='Segundos', y_label='Temperatura °C',
        title='Temperatura da CPU sobre tempo'
    )
