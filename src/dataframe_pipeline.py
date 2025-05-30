import pandas as pd

class RawMergeFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    
class ColumnEnsuredFrame:
    def __init__(self, df: RawMergeFrame):
        self.df = df

class CleanedFrame:
    def __init__(self, df: ColumnEnsuredFrame):
        self.df = df
        
class RenamedFrame:
    def __init__(self, df: CleanedFrame):
        self.df = df
