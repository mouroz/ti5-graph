import pandas as pd
import numpy as np
from src.color import *
from src.graph.mask_plot import *

# Dummy data
x = pd.Series(range(100))
y1 = pd.Series(np.random.randn(100).cumsum())
y2 = pd.Series(np.random.randn(100).cumsum())
mask = pd.Series(['low', 'high', 'medium'] * 33 + ['low'])

# Mapping
def mask_color(value):
    return {
        'low': Color.GREEN,
        'medium': Color.ORANGE,
        'high': Color.RED
    }.get(value, Color.GRAY)

def mask_label(value):
    return f"Status: {value.capitalize()}"


plot_multiple_masked_segments(
    x_series=x,
    y_series_list=[y1, y2],
    mask=mask,
    output="example/mask_plot.png",
    x_label="Time",
    y_label="Value",
    title="Categorical Masked Plot",
    mask_color_fn=mask_color,
    mask_label_fn=mask_label
)
