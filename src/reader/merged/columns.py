from enum import Enum
import pandas as pd
from src.reader.merged.pipeline import *


BASE_TIMESTAMP = MergedCol.TIMESTAMP.original
RPM_TIMESTAMP = 'Timestamp'

# Columns for merged and prepared for graph
class MergedCol(Enum):
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
    def hardware_columns():
        """Returns a list of all hardware-related columns."""
        return [
            MergedCol.TIMESTAMP,
            MergedCol.CPU_PERCENTAGE,
            MergedCol.CPU_PACKAGE_ENHANCED,
            MergedCol.GPU_POWER,
            MergedCol.GPU_TEMPERATURE,
            MergedCol.GPU_HOT_SPOT,
            MergedCol.RPM,
        ]
        
    @staticmethod
    def fan_columns():
        return [
            RPM_TIMESTAMP,
            MergedCol.RPM,
            MergedCol.RELATIVE_TIME,
            MergedCol.IS_TEST_RUNNING
        ]
    @staticmethod
    def rename_map():
        """Returns dict to rename original column names to standard names."""
        return {col.original: col.standard for col in MergedCol}

    @staticmethod
    def original_names():
        """Returns a list of all original (raw) column names."""
        return [col.original for col in MergedCol]

    @staticmethod
    def standard_names():
        """Returns a list of all standardized column names."""
        return [col.standard for col in MergedCol]
    
    @staticmethod
    def validate_columns(df: pd.DataFrame): 
        missing = [col.original for col in MergedCol if col.original not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
    @staticmethod
    def drop_unlisted_columns(frame: MergedColumnEnsuredFrame):
        """Drops all columns from the DataFrame that are not defined in the enum (by original names)."""
        df=frame.df
        allowed_columns = set(MergedCol.original_names())
        to_drop = [col for col in df.columns if col not in allowed_columns]
        df.drop(columns=to_drop, inplace=True)
        return MergedColumnEnsuredFrame(df)
    
    def rename_columns(frame: MergedCleanFrame) -> MergedFrame:
        """Rename columns of the DataFrame in-place using the enum's original-to-standard mapping."""
        df=frame.df
        rename_map = MergedCol.rename_map()
        df.rename(columns=rename_map, inplace=True)
        return MergedFrame(df)


BASE_TIMESTAMP = MergedCol.TIMESTAMP.original
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