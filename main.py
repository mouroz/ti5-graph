import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from src.columns import *
from src.entries.csv_split import *
from src.graph_plot import *
from src.entries import *
from src.pre_processing.base_csv_merge import *
from src.pre_processing.db_math_regression import *

dataFolder = os.path.join(os.path.dirname(__file__), 'data')
input_csv_folder = os.path.join(dataFolder, 'input')
output_csv_folder = os.path.join(dataFolder, 'output')
choice_output_folder = ''
tmp_folder = os.path.join(dataFolder, 'tmp')

hardwareInfo_csv_path = ''
java_csv_path = ''
merged_csv_path = os.path.join(tmp_folder, 'merged_data.csv')

_frames:list[pd.DataFrame] | None = None


# class Manual:
#     input_csv_path = 'data/base_manual.csv'
#     image_path = 'example/output.png'
#     output_prefix = 'data/base_manual/test'
    
#     _frames:list[pd.DataFrame] | None = None
    

#     @staticmethod
#     def get_frames() -> list[pd.DataFrame]:
#         if Manual._frames is None:
#             Manual._frames = get_cases_from_csv(
#                 input_csv=Manual.input_csv_path, 
#                 output_prefix=Manual.output_prefix, 
#                 intervals=intervals, 
#                 save_as_csv=True
#             )
        
#         return Manual._frames
    
#     @staticmethod
#     def get_series_mean(col: Col) -> pd.Series:
#         return mean_of_dataframe_list(Manual.get_frames())
    

#     @staticmethod
#     def plot_cpu_percentage():
#         frames = Manual.get_frames()
#         plot_all_cases(
#             frames=frames, 
#             col=Col.CPU_PERCENTAGE,
#             labels=['caso 1', 'caso 2', 'caso 3', 'caso 4', 'caso 5'],
#             output=Manual.output_prefix,
#             x_label='Segundos',
#             y_label='Cpu %',
#             title='Cpu % por segundo'
#         )
    
#     @staticmethod
#     def plot_cpu_temperature():
#         frames = Manual.get_frames()
#         plot_all_cases(
#             frames=frames, 
#             col=Col.CPU_TEMPERATURE_ENHANCED,
#             labels=['caso 1', 'caso 2', 'caso 3', 'caso 4', 'caso 5'],
#             output=Manual.output_prefix,
#             x_label='Segundos',
#             y_label='Temperatura CPU',
#             title='Temperatura CPU por segundo'
#         )
    

def initialize_folder(folder: str):
    """
    Initializes a folder by creating it if it does not exist.
    """
    os.makedirs(folder, exist_ok=True)

def initialize_default_folders():
    """
    Initializes the necessary folders for input, output, and temporary files.
    Creates them if they do not exist.
    """
    initialize_folder(input_csv_folder)
    initialize_folder(output_csv_folder)
    initialize_folder(tmp_folder)

def remove_tmp_files():
    """
    Removes all files in the temporary folder.
    """
    for file in os.listdir(tmp_folder):
        file_path = os.path.join(tmp_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

def get_csv_path(folder:str, file:str) -> str:
    path = os.path.join(folder, file)
    if not os.path.exists(path):
        print(f"CSV file not found at {path}. Exiting.")
        sys.exit(1)
    return path

def mainMenu() -> tuple[str, str]:
    """
    Displays a menu to select input CSV files from the folders in data/input.
    Returns:
        tuple[str, str]: Paths to the selected hardware info and Java CSV files.
    """
    list_of_files = os.listdir(input_csv_folder)
    if not list_of_files:
        print("No folders found in the input directory. Exiting.")
        sys.exit(1)

    print("Chose an input CSV file from the following list:")
    for i, file in enumerate(list_of_files):
        print(f"{i + 1}: {file}")

    choice = int(input("Enter the number of the file you want to use: ")) - 1
    if choice < 0 or choice >= len(list_of_files):
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    hardwareInfo_csv_path = get_csv_path(os.path.join(input_csv_folder, list_of_files[choice]), 'hw_info.csv')
    java_csv_path = get_csv_path(os.path.join(input_csv_folder, list_of_files[choice]), 'java.csv')
    choice_output_folder = os.path.join(output_csv_folder, list_of_files[choice])
    initialize_folder(choice_output_folder)

    return hardwareInfo_csv_path, java_csv_path, list_of_files[choice]


from implm.sem_base import *
from implm.base_automatica import *
from implm.base_manual import *




# def old():  
#     SemBase.plot_cpu_percentage()
#     SemBase.test_plot_with_color()
    
#     BaseAutomatica.plot_cpu_percentage()
    
#     BaseManual.plot_cpu_percentage()
 
def get_intervals_from_df(df: pd.DataFrame) -> list[Interval]:
    """
    Extracts the sequential intervals from the 'relativeTime' column of the DataFrame that IsTestRunning is true.
    Returns a list of Interval objects.
    """
    intervals = []
    start_time = None

    def to_seconds(t):
        mins, secs = map(int, t.split(':'))
        return mins * 60 + secs

    for i, row in df.iterrows():
        is_test_running = row['IsTestRunning']
        relative_time = row['relativeTime']

        # If IsTestRunning is True and we don't have a start time, mark the start
        if is_test_running and start_time is None:
            start_time = relative_time

        # If IsTestRunning is False and we have a start time, mark the end and create interval
        elif not is_test_running and start_time is not None:
            if i > 0:
                end_time = df.iloc[i]['relativeTime']
                intervals.append(Interval.from_range_string(f"{start_time} - {end_time}"))
                time_diff = to_seconds(end_time) - to_seconds(start_time)
                print(f"Interval added: {start_time} - {end_time} Time difference: {time_diff} seconds")
            start_time = None
    # Handle case where the DataFrame ends with IsTestRunning = True
    if start_time is not None:
        end_time = df.iloc[-1]['relativeTime']
        intervals.append(Interval.from_range_string(f"{start_time} - {end_time}"))
        time_diff = to_seconds(end_time) - to_seconds(start_time)
        print(f"Final interval added: {start_time} - {end_time} Time difference: {time_diff} seconds")

    return intervals

if __name__ == '__main__':  
    initialize_default_folders()
    create_polinomial_regression_from_csv()

    hardwareInfo_csv_path, java_csv_path, choice_folder_name = mainMenu()

    choice_output_folder = os.path.join(output_csv_folder, choice_folder_name)

    merged_df = join_csv_files(hardwareInfo_csv_path, java_csv_path)

    intervals = get_intervals_from_df(merged_df)

    
    predict_with_model(merged_df, output_path=os.path.join(choice_output_folder, 'merged_data_with_predictions.csv'))


    # df_test = predict_with_csv(
    #     csv_path=os.path.join(dataFolder, 'pc_fan_db_tests.csv'),
    # )

    # print_comparison_table(
    #     df=df_test,
    #     title="Teste de Ventoinha PC",
    #     metrics=calculate_metrics(df_test)
    # )

    
    
    # _frames = get_cases_from_csv(input_csv = merged_csv_path, output_prefix = choice_output_folder, intervals=intervals, save_as_csv=True)
                                 

    # # remove_tmp_files()
    # print(f"Joined data has {len(result)} rows")
    # print(result)
    # Manual.plot_cpu_percentage()

