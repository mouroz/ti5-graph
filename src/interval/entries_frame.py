import pandas as pd
from src.interval.interval import Interval
from src.interval.split_frame import split_df_by_intervals

class EntriesFrame:
    """
    A class representing a constant frame of data, providing operations for retrieving and analyzing the data.
    All of them must contain equal size in row length and same columns
    """


    def __init__(self, data: list[pd.DataFrame]):
        """
        Initialize the BaseSplitFrames with a list of DataFrames.

        :param data: A list of pandas DataFrames.
        """
        self.frames = data
    
    
    @staticmethod
    def from_intervals(df: pd.DataFrame, intervals: list[Interval]) -> 'EntriesFrame':
        split_df_by_intervals(df, intervals)
        

    def get_series(self, column: str) -> list[pd.Series]:
        """
        Return a list of Series for the given column from each frame.

        :param column: Name of the column to extract.
        :return: List of pandas Series.
        """
        return [df[column] for df in self.frames if column in df]


    def get_means(self, column: str) -> list[float]:
        """
        Return a list of means for the given column across all frames.

        :param column: Name of the column to analyze.
        :return: List of means.
        """
        return [df[column].mean() for df in self.frames if column in df]


    def get_global_mean(self, column: str) -> float:
        """
        Return the global mean of the column across all frames combined.

        :param column: Name of the column to analyze.
        :return: Global mean value.
        """
        series = self.get_series(column)
        if not series:
            return float('nan')
        combined = pd.concat(series, ignore_index=True)
        return combined.mean()

    
    def get_mean_series(self, column: str) -> pd.Series:
        """
        Return the element-wise mean of a specific column across all frames.

        Assumes:
            - Each DataFrame has the specified column.
            - All DataFrames have the same number of rows (aligned by time).
        
        :param column: Name of the column to compute element-wise mean on.
        :return: A Series representing the mean at each time point.
        """
        series_list = self.get_series(column)
        if not series_list:
            return pd.Series(dtype=float)
        df = pd.concat(series_list, axis=1)
        return df.mean(axis=1)


    def get_total_row_length(self) -> int:
        return len(self.frames[0])
    
    