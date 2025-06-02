from enum import Enum
import pandas as pd
from src.reader.merged.pipeline import *
from src.reader.merged.columns import BASE_TIMESTAMP, RPM_TIMESTAMP, MergedCol

    
class InvalidTimestampError(ValueError):
    pass






class MergedColumnEnsuredFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def join_csv_files(base_csv_path:str, rpm_csv_path:str) -> "MergedColumnEnsuredFrame":
        """
        Merges two CSV files based on their timestamps.
        The join criterion is based on equal timestamp between the frames by seconds floor aproximation
        
        Raises:
            ValueError: If columns Timestamp and Time does not exist for their respective
            dataframes base, rpm, and if they do not contain valid timestamps.
        
        Returns:
            Dataframe with merged values. If no values are merged, return an empty dataframe
        """
        # Read both CSV files
        try:
            base_df = pd.read_csv(base_csv_path, usecols=MergedCol.hardware_columns())
            rpm_df = pd.read_csv(rpm_csv_path, usecols=MergedCol.fan_columns())
            
        except pd.errors.ParserError as e:  
            raise ValueError(f"Error parsing the CSV file: {e}")
        
        except KeyError as e:
            raise ValueError(f"Missing required columns in the CSV file: {e}")
        
        except FileNotFoundError:
            raise ValueError(f"The file {base_csv_path} does not exist.")
        
        
        
        # Remove last line of base_df
        if not base_df.empty and base_df.iloc[-1].isnull().all():
            base_df = base_df[:-1]
        
        if BASE_TIMESTAMP not in base_df.columns or RPM_TIMESTAMP not in rpm_df.columns:
            raise KeyError("Missing required columns in input DataFrame.")    
        
        try:
            timestamp_format = "%H:%M:%S"  # Adjust as needed
            
            # Parse and strip milliseconds from timestamps
            base_df['join_time'] = pd.to_datetime(
                base_df[BASE_TIMESTAMP], format='mixed', errors='raise'
            ).dt.strftime('%H:%M:%S')
            
            rpm_df['join_time'] = pd.to_datetime(
                rpm_df[RPM_TIMESTAMP], format='mixed', errors='raise'
            ).dt.strftime('%H:%M:%S')

                
        except Exception as e:
            raise InvalidTimestampError(f"Invalid timestamp encountered: {e}")

        
        # Perform the join operation
        merged_df = pd.merge(base_df, rpm_df, on='join_time', how='inner')
        
        # Remove the temporary join column
        merged_df = merged_df.drop('join_time', axis=1)
        
        
        merged_df = merged_df.drop(RPM_TIMESTAMP, axis=1, errors='raise')
        
        
        MergedCol.validate_columns(merged_df)
        return MergedColumnEnsuredFrame(merged_df)

    
    def clean_dataframe(self) -> "MergedColumnEnsuredFrame":
        """
        Cleans the DataFrame by dropping columns not defined in MergedCol.
        """
        return MergedCleanFrame(self)
   

class MergedCleanFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def fix_dataframe_inconsistencies(wrapper: MergedColumnEnsuredFrame) -> "MergedCleanFrame":
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


        return MergedCleanFrame(dataframe)
    
    

    # Optional step for cleaned frame. Not required for the next steps
    def _interpolate_missing_timestamps(self):
        
        dataframe = self.df
        
        # Create a list to hold the original and interpolated rows
        all_rows = []
        
        TIMESTAMP = MergedCol.TIMESTAMP.original
        RELATIVETIME = MergedCol.RELATIVE_TIME.original
        
        # Process rows to fill gaps
        for i in range(len(dataframe) - 1):
            current_row = dataframe.iloc[i].copy()
            next_row = dataframe.iloc[i+1]
            
            all_rows.append(current_row)
            
            # Calculate the time difference in seconds
            time_diff = (next_row[TIMESTAMP] - current_row[TIMESTAMP]).total_seconds()
            
            # If gap is more than 1 second, create interpolated rows
            if time_diff > 1.0:
                print(f"Filling gap of {time_diff} seconds between {current_row[TIMESTAMP]} and {next_row[TIMESTAMP]}")
                for sec in range(1, int(time_diff)):
                    # Create a new row by copying the current row
                    new_row = current_row.copy()
                    
                    # Update Timestamp
                    new_row[TIMESTAMP] = current_row[TIMESTAMP] + pd.Timedelta(seconds=sec)
                    

                    # Parse the relative time
                    if isinstance(current_row[RELATIVETIME], str) and ':' in current_row[RELATIVETIME]:
                        mins, secs = map(int, current_row[RELATIVETIME].split(':'))
                        total_secs = mins * 60 + secs + sec
                        new_mins = total_secs // 60
                        new_secs = total_secs % 60
                        new_row[RELATIVETIME] = f"{new_mins:02d}:{new_secs:02d}"
                    
                    # Reset the index so the new row does not keep the original index
                    new_row = new_row.copy()
                    new_row.name = None  # Remove the index name
                    
                    all_rows.append(new_row)
                    
                    
        # Add the last row
        if len(dataframe) > 0:
            all_rows.append(dataframe.iloc[-1])
        
        # Create a new DataFrame from all rows
        result_df = pd.DataFrame(all_rows)
        
        self.df = result_df

    def rename_columns(self) -> "MergedFrame":
        """
        Rename columns of the DataFrame in-place using the enum's original-to-standard mapping.
        """
        dataframe = self.df
        rename_map = MergedCol.rename_map()
        dataframe.rename(columns=rename_map, inplace=True)
        return MergedFrame(dataframe)

    def interpolate_then_rename(self) -> "MergedFrame":
        """
        Interpolates missing timestamps and renames columns.
        """
        self._interpolate_missing_timestamps()
        return self.rename_columns()
    
class MergedFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
     
    @staticmethod   
    def get_merged_frame(base_csv_path:str, rpm_csv_path:str, interpolate:bool) -> "MergedFrame":
        """
        Merges two CSV files and returns a cleaned DataFrame.
        Expected errors from join_csv_files and verify_join_csv_files are thrown here
        """
        safe_wrapper: MergedColumnEnsuredFrame = MergedColumnEnsuredFrame.join_csv_files(base_csv_path, rpm_csv_path)
        cleaned_wrapper: MergedCleanFrame = safe_wrapper.clean_dataframe()
        if interpolate:
            renamed_wrapper = safe_wrapper.interpolate_then_rename()
        else:
            renamed_wrapper = safe_wrapper.rename_columns()
        
        
        return renamed_wrapper


