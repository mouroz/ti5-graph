import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

# from src.implm.merged.columns import *
# from src.interval.split_frame import *
# from src.graph.line_plot import *
# from src.interval import *
from src.implm.merged.db_math_regression import *
from src.implm.merged.pipeline import *
# from src.pre_processing.db_math_regression import *

dataFolder = os.path.join(os.path.dirname(__file__), 'data')
input_csv_folder = os.path.join(dataFolder, 'input')
output_csv_folder = os.path.join(dataFolder, 'output')
choice_output_folder = ''
tmp_folder = os.path.join(dataFolder, 'tmp')

hardwareInfo_csv_path = ''
java_csv_path = ''
merged_csv_path = os.path.join(tmp_folder, 'merged_data.csv')

_frames:list[pd.DataFrame] | None = None


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

    return hardwareInfo_csv_path, java_csv_path, choice_output_folder




if __name__ == '__main__':  
    initialize_default_folders()
    create_polinomial_regression_from_csv()

    hardwareInfo_csv_path, java_csv_path, choice_output_folder = mainMenu()

    print(f"{output_csv_folder}")

    initialize_folder(choice_output_folder)
    print(f"choise_output_folder: {choice_output_folder}")

    # merged_df = get_merged_frame(
    #     HW_info_csv=hardwareInfo_csv_path, 
    #     java_csv_path=java_csv_path, 
    #     output_final_file=os.path.join(choice_output_folder, 'merged_data.csv')
    # )
    
    df_list = get_splitted_frames_from_csv(
        Base_csv=hardwareInfo_csv_path,
        java_csv_path=java_csv_path,
        # output_path=merged_csv_path,
        output_path=choice_output_folder
    )
    
    print(f"Data merged and saved to {choice_output_folder}")
    

    
    

    # create_polinomial_regression_from_csv(grau=3, csv_path=os.path.join(dataFolder, 'fans_db_tests.csv'), log_in_terminal=False)


    # df_test = predict_with_csv(
    #     csv_path=os.path.join(dataFolder, 'pc_fan_db_tests.csv'),
    # )

    # print_comparison_table(
    #     df=df_test,
    #     title="Teste de Ventoinha PC",
    #     metrics=calculate_metrics(df_test)
    # )

    
    
    # # _frames = get_cases_from_csv(input_csv = merged_csv_path, output_prefix = choice_output_folder, intervals=intervals, save_as_csv=True)
                                 

    # # remove_tmp_files()
    # print(f"Joined data has {len(result)} rows")
    # print(result)
    # Manual.plot_cpu_percentage()

