import unittest
import pandas as pd
from io import StringIO
from src.pre_processing.merge import *
from src.columns import BASE_TIMESTAMP, RPM_TIMESTAMP
import pytest
import textwrap


@pytest.mark.parametrize("base_csv,rpm_csv,expected_len", [
    (
        f"""
{BASE_TIMESTAMP},RPM
2024-01-01 10:00:00, A
2024-01-01 10:00:01, B
2024-01-01 10:00:02, C
        """,
        
        f"""
{RPM_TIMESTAMP},RPM
2024-01-01 10:00:00, 1000
2024-01-01 10:00:01, 1010
2024-01-01 10:00:02, 1020
        """,
        
        3
    ),
    
    (
        f"""
{BASE_TIMESTAMP},RPM
2024-01-01 10:00:00.123, A
2024-01-01 10:00:01.456, B
2024-01-01 10:00:02.789, C
        """,
        
        f"""
{RPM_TIMESTAMP},RPM
2024-01-01 10:00:00.30, 1000
2024-01-01 10:00:01.23, 1010
2024-01-01 10:00:02.01, 1020
        """,
        
        3
    ),
    

    
], ids=["exact_match", "one_match"])



def test_join_csv_variants(tmp_path, base_csv, rpm_csv, expected_len):
    
    base_path = tmp_path / base_csv
    rpm_path = tmp_path / rpm_csv

    base_path.write_text(textwrap.dedent(base_csv))
    rpm_path.write_text(textwrap.dedent(rpm_csv))

    result = join_csv_files(str(base_path), str(rpm_path))
    assert len(result.df) == expected_len
    
    
