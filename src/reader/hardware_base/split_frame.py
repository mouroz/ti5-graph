
from src.reader.hardware_base.base_columns import *
from src.reader.hardware_base.read_base_pipeline import BaseFrame
from src.entries.entries_frame import *
import numpy as np

class BaseSplitFrames:
    """
    A class representing a constant frame of data, providing operations for retrieving and analyzing the data.
    """

    def __init__(self, data: EntriesFrame):
        """
        Initialize the BaseFrame with a RenamedBaseFrame instance.

        :param data: An instance of RenamedBaseFrame containing the data.
        """
        self._frames = data
        

    def get_series(self, column: BaseCol) -> list[pd.Series]:
        return self._frames.get_series(column.standard)


    def get_means(self, column: BaseCol) -> list[float]:
        return self._frames.get_means(column.standard)

    def get_global_mean(self, column: BaseCol) -> float:
        return self._frames.get_global_mean(column.standard)
    
    def get_duration_in_seconds(self, column: BaseCol) -> int:
        return self._frames.get_total_row_length()
    
    def get_series_mean(self, column: BaseCol) -> pd.Series:
        return self._frames.get_mean_series(column.standard)