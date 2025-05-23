import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from columns import *
from plot import *



def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV with predefined dtypes and datetime parsing.
    Modify `dtype_map` and `parse_dates` as per your CSV structure.
    """

    df = pd.read_csv(file_path, usecols=Col.original_names())
    df = df.rename(columns=Col.rename_map())
    print(Col.rename_map())
    
    return df



def convert_to_datetime(time_obj):
    return datetime.combine(datetime.today(), time_obj)


def manipulate_df(df: pd.DataFrame):
    df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(lambda x: datetime.strptime(x, "%H:%M:%S.%f").time())
    df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(convert_to_datetime)
    # Set the first time as the reference
    start_time = df[Col.TIMESTAMP.standard].iloc[0]

    # Replace with seconds since start_time
    df[Col.TIMESTAMP.standard] = df[Col.TIMESTAMP.standard].apply(
        lambda dt: int((dt - start_time).total_seconds())
    )
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot CPU usage from CSV.')
    parser.add_argument('input_csv', help='Path to input CSV file')
    parser.add_argument('output_image', help='Path to save output plot (e.g., output.png)')
    args = parser.parse_args()

    df = read_csv(args.input_csv)
    manipulate_df(df)
    
    plot_time_test(df, args.output_image)
    
    
    
    
