import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.graph.binary_mask_plot import *


# Sample data
x = pd.Series(range(100))
y = pd.Series(np.sin(np.linspace(0, 20, 100)))
mask = y > 0  # Just as an example condition



plt.figure(figsize=(12, 4))
plot_colored_by_binary_mask(x, y, mask, label_true='Positive', label_false='Negative')
plt.title("Line colored by sign")
plt.xlabel("Time")
plt.ylabel("Signal")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()