from typing import Callable, Any
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.color import *

def plot_multiple_masked_segments(
    x_series: pd.Series,
    y_series_list: list[pd.Series],
    mask: pd.Series,
    output: str,
    x_label: str,
    y_label: str,
    title: str,
    y_min: float | None = None,
    y_max: float | None = None,
    mask_color_fn: Callable[[Any], Color] = lambda x: Color.RED,
    mask_label_fn: Callable[[Any], str] = lambda x: str(x)
):
    """
    Plots multiple time series with segments colored by the value of a mask series.

    Parameters:
        mask_color_fn: A function that maps each mask value to a Color enum.
        mask_label_fn: A function that maps each mask value to a human-readable label.
    """
    plt.figure(figsize=(15, 5))

    print("x:", x_series.shape)
    print("First 5 x:", x_series.head())

    for i, y in enumerate(y_series_list):
        print(f"y[{i}] shape:", y.shape)
        print(f"First 5 y[{i}]:", y.head())

    print("mask:", mask.shape)
    print("Unique mask values:", mask.unique())


    for y_series in y_series_list:
        _plot_categorical_mask_segments(
            x_series, y_series, mask, mask_color_fn, mask_label_fn
        )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)

    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)

    plt.legend(loc='upper right')
    plt.tight_layout()
    print(f"Saved to {output}")
    plt.savefig(output)
    plt.close()


def _plot_categorical_mask_segments(
    x: pd.Series,
    y: pd.Series,
    mask: pd.Series,
    color_fn: Callable[[Any], Color],
    label_fn: Callable[[Any], str],
    **kwargs
):
    """
    Plot y over x, segmenting and coloring by the value in mask.
    """
    assert len(x) == len(y) == len(mask), "All series must be the same length"


    start = 0
    current_value = mask.iloc[0]

    for i in range(1, len(mask)):
        if mask.iloc[i] != current_value:
            #print(f"Segment: {start} to {i}, value: {current_value}")
            _plot_segment_by_value(
                x[start:i+1],
                y[start:i+1],
                current_value,
                color_fn,
                label_fn,
                **kwargs
            )
            start = i
            current_value = mask.iloc[i]

    _plot_segment_by_value(
        x[start:], y[start:], current_value, color_fn, label_fn, **kwargs
    )
    


def _plot_segment_by_value(
    x: pd.Series,
    y: pd.Series,
    value: Any,
    color_fn: Callable[[Any], Color],
    label_fn: Callable[[Any], str],
    **kwargs
):
    """
    Plot a single segment of the time series with appropriate color and legend label.
    """
    color = str(color_fn(value))
    label = label_fn(value)

    existing_labels = plt.gca().get_legend_handles_labels()[1]

    print(x)
    print(y)
    print(color)
    plt.plot(
        x,
        y,
        color=color,
        label=label if label not in existing_labels else None,
        **kwargs
    )
    
