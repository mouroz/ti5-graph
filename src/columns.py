from enum import Enum
import pandas as pd
from src.dataframe_pipeline import *


# Columns for merged and prepared for graph
class Col(Enum):
    TIMESTAMP = ('Time', 'Time')
    RELATIVE_TIME = ('relativeTime', 'Relative Time')
    
    # CPU Data
    CPU_PERCENTAGE = ('Total CPU Usage [%]', 'Total CPU %')
    # CPU_TEMPERATURE_ENHANCED = ('CPU Package [�C]_1', 'Cpu Temperature')
    CPU_PACKAGE_ENHANCED = ('CPU Package Power [W]', 'Cpu Package')

    # GPU Fata
    
    GPU_POWER = ('GPU Power [W]', 'GPU Power W')
    GPU_TEMPERATURE = ('GPU Temperature [�C]', 'GPU Temperature')
    GPU_HOT_SPOT = ('GPU Hot Spot Temperature [�C]', 'GPU Hot Spot')
    
    RPM = ('RPM', 'RPM')
    IS_TEST_RUNNING = ('IsTestRunning', 'Is Test Running')
    # Disk Data

    # SSD_Temperature = ('Drive Temperature [�C]_2', 'SSD Temperature')
    # HDD_Temperature = ('Drive Temperature [�C]_1', 'HDD Temperature')

    @property
    def original(self):
        return self.value[0]

    @property
    def standard(self):
        return self.value[1]

    @staticmethod
    def rename_map():
        """Returns dict to rename original column names to standard names."""
        return {col.original: col.standard for col in Col}

    @staticmethod
    def original_names():
        """Returns a list of all original (raw) column names."""
        return [col.original for col in Col]

    @staticmethod
    def standard_names():
        """Returns a list of all standardized column names."""
        return [col.standard for col in Col]
    
    @staticmethod
    def validate_columns(df: pd.DataFrame): 
        missing = [col.original for col in Col if col.original not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
    @staticmethod
    def drop_unlisted_columns(frame: ColumnEnsuredFrame):
        """Drops all columns from the DataFrame that are not defined in the enum (by original names)."""
        df=frame.df
        allowed_columns = set(Col.original_names())
        to_drop = [col for col in df.columns if col not in allowed_columns]
        df.drop(columns=to_drop, inplace=True)
        return ColumnEnsuredFrame(df)
    
    def rename_columns(frame: CleanedFrame) -> RenamedFrame:
        """Rename columns of the DataFrame in-place using the enum's original-to-standard mapping."""
        df=frame.df
        rename_map = Col.rename_map()
        df.rename(columns=rename_map, inplace=True)
        return RenamedFrame(df)


BASE_TIMESTAMP = Col.TIMESTAMP.original
RPM_TIMESTAMP = 'Timestamp'



        
# MIGHT CONSIDER LATER
# def normalize_string(name):
#     """Normalize a column name by removing whitespace and replacing special characters (excluding hyphen and comma) with underscores"""
#     name = str(name).strip().lower()  # Convert to string, strip whitespace, and lowercase
#     name = re.sub(r'[^\w\s/,-]', '_', name)  # Replace non-word/non-space/non-hyphen/non-comma chars with _
#     name = re.sub(r'\s+', '_', name)      # Replace spaces with _
#     name = re.sub(r'_+', '_', name)        # Collapse multiple _ into one
#     name = name.strip('_')  # Remove any _ at the start or end of the string

#     return name