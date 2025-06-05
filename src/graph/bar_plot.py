import matplotlib.pyplot as plt
import pandas as pd

def plot_avg_bars(
    y_series_list: list[pd.Series],
    labels: list[str] | None,
    output: str,
    y_label: str,
    title: str
):
    """
    Plots the average of each series in y_series_list as a bar graph.
    """
    averages = [y.mean() for y in y_series_list]
    
    if labels is None:
        labels = [f"Series {i+1}" for i in range(len(y_series_list))]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, averages, color='skyblue')
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(axis='y')
    plt.tight_layout()
    print(output)
    plt.savefig(output)
