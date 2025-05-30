import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.columns import *

import chardet



def mean_of_series_list(series_list: list[pd.Series]) -> pd.Series:
    # Combine all series into a DataFrame (each series is one column)
    df = pd.concat(series_list, axis=1)
    # Calculate mean along the rows (axis=1)
    return df.mean(axis=1)
        
    
def mean_of_dataframe_list(df_list: list[pd.DataFrame], col: Col) -> pd.Series:
    series:list[pd.Series] = []
    
    for frame in df_list:
        series.append(frame[col.standard]) 
    
    return mean_of_series_list(series)
    

def get_series_from_frames(frames: list[pd.DataFrame], col: Col):
    y_series:list[pd.Series] = []
    for frame in frames:
        y_series.append(frame[col.standard])
    return y_series


            
    
