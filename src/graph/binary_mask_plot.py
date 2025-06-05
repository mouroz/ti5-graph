import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_multiple_binary_mask(
    x_series: pd.Series,
    y_series_list: list[pd.Series],
    mask: pd.Series, # Where pd.Series is a binary series
    output: str, 
    x_label: str, 
    y_label: str, 
    title: str,
    y_min: float | None = None,
    y_max: float | None = None,
    mask_label_true: str = 'Active',
    mask_label_false: str = 'Inactive',
    color_true: str = 'green',
    color_false: str = 'red'
):
    """
    Plots time series data.
    If group_col is specified, plots one line per group.
    """

    plt.figure(figsize=(15, 5))
    
    for i, y_series in enumerate(y_series_list):
        plot_colored_by_binary_mask(
            x=x_series, 
            y=y_series, 
            mask=mask, 
            label_true=mask_label_true, 
            label_false=mask_label_false,
            color_true=color_true,
            color_false=color_false
        )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    
    
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)
        
    
    plt.legend(loc='upper right')  # simple, top right inside
    
    plt.tight_layout()
    print(output)
    plt.savefig(output)



def plot_colored_by_binary_mask(
    x: pd.Series, 
    y: pd.Series, 
    mask: pd.Series, 
    label_true='Active', 
    label_false='Inactive', 
    color_true: str = 'green',
    color_false: str = 'red',
    **kwargs # Additional _plot_segment args
):
    """
    Plots a line where the color changes based on a boolean mask.
    True → one color, False → another.
    """
    assert len(x) == len(y) == len(mask), "All series must be the same length"
    
    
    # Plot consecutive segments with same mask value
    start = 0
    current = mask.iloc[0]
    
    for i in range(1, len(mask)):
        if mask.iloc[i] != current:
            # Plot the previous segment
            _plot_segment(
                x[start:i+1], 
                y[start:i+1], 
                current, 
                label_true, 
                label_false, 
                color_true, 
                color_false, 
                **kwargs
            )
            start = i
            current = mask.iloc[i]

    # Plot the last segment
    _plot_segment(
        x[start:], 
        y[start:], 
        current, 
        label_true, 
        label_false,  
        color_true, 
        color_false, 
        **kwargs
    )
    



def _plot_segment(
    x: pd.Series, 
    y: pd.Series, 
    is_true: bool, 
    label_true: str, 
    label_false: str, 
    color_true: str, 
    color_false:str, 
    **kwargs
):
    """
    Plots a single segment of a time series with the appropriate color and legend label.
    """
    color = color_true if is_true else color_false
    label = label_true if is_true else label_false
    
    plt.plot(
        x, y, 
        color=color, 
        # Only add new labels if they dont exist yet 
        label=label if not plt.gca().get_legend_handles_labels()[1].count(label) else None, 
        **kwargs
    )
    


