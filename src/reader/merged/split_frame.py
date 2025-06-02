
from src.reader.merged.columns import *
from src.reader.merged.pipeline import MergedFrame
from src.interval.entries_frame import *
import numpy as np

class MergedSplitFrames:
    """
    A class representing a constant frame of data, providing operations for retrieving and analyzing the data.
    """

    def __init__(self, data: EntriesFrame):
        """
        Initialize the BaseFrame with a RenamedBaseFrame instance.

        :param data: An instance of RenamedBaseFrame containing the data.
        """
        self._frames = data
        

    def get_series(self, column: MergedCol) -> list[pd.Series]:
        return self._frames.get_series(column.standard)


    def get_means(self, column: MergedCol) -> list[float]:
        return self._frames.get_means(column.standard)

    def get_global_mean(self, column: MergedCol) -> float:
        return self._frames.get_global_mean(column.standard)
    
    def get_duration_in_seconds(self, column: MergedCol) -> int:
        return self._frames.get_total_row_length()
    
    def get_series_mean(self, column: MergedCol) -> pd.Series:
        return self._frames.get_mean_series(column.standard)