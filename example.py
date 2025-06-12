from main import *

from enum import Enum
import pandas as pd

from src.interval.entries_frame import EntriesFrame
from src.implm.merged.columns import MergedCol


from src.graph.bar_plot import plot_avg_bars
from src.graph.line_plot import *
from src.graph.line_binary_mask_plot import *

class Folders(Enum):
    FH4_AUTOMATICO = 'FH4_automatico'
    PASSMARK_AUTOMATICO = 'PassMark_automatico'
    SEM_BASE_4K = '4k_semBase'
    PASSMARK_SEM_BASE = 'PassMark_semBase'
    PASSMARK_MANUAL = 'PassMark_manual'
    MANUAL_4K = '4k_manual'
    FH4_SEM_BASE = 'FH4_semBase'
    AUTOMATICO_4K = '4k_automatico'
    FH4_MANUAL = 'FH4_manual'
    
    @property 
    def folder(self):
        return self.value

    def get_frames(self) -> list[pd.DataFrame]:
        print(self.value)
        hardwareInfo_csv_path, java_csv_path, choice_output_folder = get_paths(self.folder)
        
        df_list = get_splitted_frames_from_csv(
            Base_csv=hardwareInfo_csv_path,
            java_csv_path=java_csv_path,
            output_path=choice_output_folder
        )
        
        return df_list
        
    
    
        
if __name__ == '__main__':
    ensure_start()
   
    fh4_automatico = Folders.FH4_AUTOMATICO.get_frames()
    fh4_manual = Folders.FH4_MANUAL.get_frames()
    fh4_sem_base = Folders.FH4_SEM_BASE.get_frames()
    
    avg_cpu_series = [
        EntriesFrame.frame_get_mean_series(fh4_automatico, MergedCol.CPU_PERCENTAGE.original),
        EntriesFrame.frame_get_mean_series(fh4_manual, MergedCol.CPU_PERCENTAGE.original),
        EntriesFrame.frame_get_mean_series(fh4_sem_base, MergedCol.CPU_PERCENTAGE.original)
    ]
    
    plot_avg_bars (
        y_series_list=avg_cpu_series,
        labels= None,
        output=os.path.join(choice_output_folder, 'avg_cpu_usage.png'),
        y_label='Average CPU Usage [%]',
        title='Average CPU Usage Over Time',
        y_min=0.0,
        y_max=100.0
    )
    