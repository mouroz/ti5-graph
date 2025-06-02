import pandas as pd

class RawMergeFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    
class MergedColumnEnsuredFrame:
    def __init__(self, df: RawMergeFrame):
        self.df = df

class MergedCleanFrame:
    def __init__(self, df: MergedColumnEnsuredFrame):
        self.df = df
        
class MergedRenamedFrame:
    def __init__(self, df: MergedCleanFrame):
        self.df = df
