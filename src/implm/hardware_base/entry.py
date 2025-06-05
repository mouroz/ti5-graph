
import src.implm.hardware_base.pipeline as pipeline
import src.implm.hardware_base.graph_implm as graph_implm
import pandas as pd

from src.interval.interval import Interval
from src.interval.entries_frame import EntriesFrame




intervals = [
    #Interval.from_range_string("1:21 - 3:02"),
    Interval.from_range_string("3:29 - 5:01"),
    #Interval.from_range_string("6:29 - 7:01"), INVALIDO
    Interval.from_range_string("7:33 - 9:05"),
    Interval.from_range_string("9:40 - 11:12"),
    Interval.from_range_string("11:58 - 13:30")
]

input_csv_path = 'data_sem_base/sem_base.csv'
output_prefix = 'example/sem_base/case'

        
if __name__ == '__main__':  
    frame:EntriesFrame = pipeline.get_entries_frame(input_csv_path, intervals, output_prefix)
    print(frame.frames)
    graph_implm.plot_cpu_percentage(frame, 'example/graph_sem_base.png')
    graph_implm.test_plot_with_color(frame, 'example/graph_sem_base_cor.png')
    graph_implm.test_bar_avg(frame, 'example/graph_sem_base_bar.png')
    graph_implm.test_plot_all_cases(frame, 'example/graph_sem_base_all_cases.png')

    