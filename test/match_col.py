import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def match_col_test():
    df1 = pd.read_csv('data/base_manual.csv')
    df2 = pd.read_csv('data/sem_base.csv')

    headers1 = df1.columns.tolist()
    headers2 = df2.columns.tolist()

    if headers1 == headers2:
        print("✅ Headers match exactly.")
    else:
        print("❌ Headers do NOT match.")
        print("\nHeaders in base_manual.csv:")
        print(headers1)
        print("\nHeaders in sem_base.csv:")
        print(headers2)

        # Optional: show which are different
        only_in_1 = [h for h in headers1 if h not in headers2]
        only_in_2 = [h for h in headers2 if h not in headers1]

        print("\nOnly in base_manual.csv:", only_in_1)
        print("Only in sem_base.csv:", only_in_2)

    print(df1['Total CPU Usage [%]'])
    print(df2['Total CPU Usage [%]'])

