import pandas as pd
from src.interval.interval import Interval
from src.interval.split_frame import split_df_by_intervals_as_index

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
        
        if not data:
            raise ValueError("EntriesFrame cannot be initialized with an empty list of DataFrames.")

        row_counts = [len(df) for df in data]
        assert all(count == row_counts[0] for count in row_counts), \
            f"Inconsistent row counts: {row_counts}"
            
        self.frames = data
            
            
    @staticmethod
    def from_intervals(df: pd.DataFrame, intervals: list[Interval]) -> 'EntriesFrame':
        split_df_by_intervals_as_index(df, intervals)
    
    
    @staticmethod 
    def frame_get_series(frames: list[pd.DataFrame], column: str) -> list[pd.Series]:
        """
        Extract a list of Series for the specified column from each DataFrame in the list.

        :param frames: List of pandas DataFrames.
        :param column: Name of the column to extract.
        :return: List of pandas Series for the specified column.
        """
        return [df[column] for df in frames if column in df]
    
    
    @staticmethod
    def series_get_mean_series(series: list[pd.Series]) -> pd.Series:
        """
        Compute the element-wise mean of a list of Series.

        :param list: List of pandas Series.
        :return: A Series representing the mean at each index.
        """
        if not series:
            return pd.Series(dtype=float)
        df = pd.concat(series, axis=1)
        return df.mean(axis=1)
    
    @staticmethod
    def frame_get_mean_series(frames: list[pd.DataFrame], col:str) -> pd.Series:
        """
        Compute the element-wise mean of a list of Series.

        :param list: List of pandas Series.
        :return: A Series representing the mean at each index.
        """
        if not frames:
            return pd.Series(dtype=float)
        
        series = EntriesFrame.frame_get_series(frames, col)
        df = pd.concat(series, axis=1)
        return df.mean(axis=1)
    
    
    
    

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
        return EntriesFrame.series_get_mean_series(self.get_series(column))


    def get_total_row_length(self) -> int:
        return len(self.frames[0])
    
    