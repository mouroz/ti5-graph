import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.reader.hardware_base.columns import BaseCol
from src.interval.create_entries import *
from src.interval import *



class BaseColumnEnsuredFrame:
    def read_csv(base_csv_path:str) -> "BaseColumnEnsuredFrame":
        """
        Read csv as panda, and ensures they follow the required columns for the base frame.
            
        Raises:
            ValueError: If any of the expected columns are missing in the DataFrame.
        
        Returns:
            Dataframe with ensured columns.
        """
        print(base_csv_path)
        # Read both CSV files
        try:
            base_df = pd.read_csv(base_csv_path, index_col=False, usecols=BaseCol.original_names())
            
        except pd.errors.EmptyDataError:
            raise ValueError("The provided CSV file is empty")
        
        except pd.errors.ParserError as e:  
            raise ValueError(f"Error parsing the CSV file: {e}")
        
        except KeyError as e:
            raise ValueError(f"Missing required columns in the CSV file: {e}")
        
        except FileNotFoundError:
            raise ValueError(f"The file {base_csv_path} does not exist.")
        
        

        try:
            timestamp_format = "%H:%M:%S"  # Adjust as needed
            
            # Parse and strip milliseconds from timestamps
            base_df['join_time'] = pd.to_datetime(
                base_df[BASE_TIMESTAMP], format='mixed', errors='raise'
            ).dt.strftime('%H:%M:%S')

                
        except Exception as e:
            raise ValueError(f"Invalid timestamp encountered: {e}")


        return BaseColumnEnsuredFrame(base_df)

    def __init__(self, df:pd.DataFrame):
        self.df = df

    def clean_frame(self) -> "BaseCleanFrame":
        """
        Cleans the DataFrame by fixing inconsistencies such as gaps in timestamps and removing duplicates.
        """
        return BaseCleanFrame.fix_dataframe_inconsistencies(self)


class BaseCleanFrame:
    def fix_dataframe_inconsistencies(wrapper: BaseColumnEnsuredFrame) -> "BaseCleanFrame":
        """
        Fix gaps in the CSV file by:
        1. Converting timestamps to datetime format
        2. Filling in missing timestamps (when gap > 1 second) with interpolated rows
        3. Removing duplicates
        """
        
        dataframe = wrapper.df
        TIMESTAMP = MergedCol.TIMESTAMP.original
        
        
        # Remove duplicates based on 'Timestamp'
        dataframe = dataframe.drop_duplicates(subset=TIMESTAMP)
        
        # Sort 
        dataframe = dataframe.sort_values(by=TIMESTAMP)
        
        # Reset index to ensure it is sequential
        dataframe = dataframe.reset_index(drop=True)


        return BaseCleanFrame(dataframe)

    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def rename_columns(self) -> "BaseFrame":
        """
        Rename columns of the DataFrame in-place using the enum's original-to-standard mapping.
        """
        return BaseFrame.rename_columns(self)
        
        
#FINISHED
class BaseFrame:
    
    def rename_columns(wrapper: BaseCleanFrame) -> "BaseFrame": 
        """
        Rename columns of the DataFrame in-place using the enum's original-to-standard mapping.
        """
        dataframe = wrapper.df
        rename_map = BaseCol.rename_map()
        dataframe.rename(columns=rename_map, inplace=True)
        return BaseFrame(dataframe)
        
        
    @staticmethod
    def get_base_frame(base_csv_path:str) -> "BaseFrame":
        """
        Merges two CSV files and returns a cleaned DataFrame.
        Expected errors from join_csv_files and verify_join_csv_files are thrown here
        """
        wrapper: BaseColumnEnsuredFrame = BaseColumnEnsuredFrame.read_csv(base_csv_path)
        cleaned_wrapper: BaseCleanFrame = wrapper.clean_frame()
        renamed_wrapper = cleaned_wrapper.rename_columns()
        
        return renamed_wrapper



    def __init__(self, df: pd.DataFrame):
        self.df = df
