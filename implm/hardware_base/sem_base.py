import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.graph.simple_plot import *

from src.entries.interval import *
from src.reader.hardware_base.read_base_pipeline import *
from implm.hardware_base.single_test import SingleTest

intervals = [
    #Interval.from_range_string("1:21 - 3:02"),
    Interval.from_range_string("3:29 - 5:01"),
    #Interval.from_range_string("6:29 - 7:01"), INVALIDO
    Interval.from_range_string("7:33 - 9:05"),
    Interval.from_range_string("9:40 - 11:12"),
    Interval.from_range_string("11:58 - 13:30")
]

input_csv_path = 'data/sem_base.csv'
output_prefix = 'example/sem_base/case'




        
if __name__ == '__main__':  
    test = SingleTest(input_csv_path, intervals, output_prefix)
    test.plot_cpu_percentage('example/graph_sem_base.png')
    test.test_plot_with_color('example/graph_sem_base_cor.png')

    

    
    
    
    
    
