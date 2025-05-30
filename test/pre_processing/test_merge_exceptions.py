import unittest
import pandas as pd
from io import StringIO
from src.pre_processing.merge import join_csv_files, InvalidTimestampError
from src.columns import BASE_TIMESTAMP, RPM_TIMESTAMP
import pytest
import textwrap


@pytest.mark.parametrize("base_csv,rpm_csv,expect_exception", [
    (
        f"""
{BASE_TIMESTAMP},OtherData
2024-01-01 10:00:00, A
2024-01-01 10:00:01, B
2024-01-01 10:00:02, C 
        """,
        
        f"""
{RPM_TIMESTAMP},RPM
2024-01-01 10:00:00, 1000
2024-01-01 10:00:0123, 1010
2024-01-01 10:00:02, 1020
        """,
        
        True
    ),
    
    (
        f"""
{BASE_TIMESTAMP},OtherData
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
        
        False
    ),
    

    
], ids=["exact_match", "one_match"])



def test_join_csv_exceptions(tmp_path, base_csv, rpm_csv, expect_exception):
    
    base_path = tmp_path / base_csv
    rpm_path = tmp_path / rpm_csv

    base_path.write_text(textwrap.dedent(base_csv))
    rpm_path.write_text(textwrap.dedent(rpm_csv))

    if expect_exception:
        with pytest.raises(InvalidTimestampError):
            join_csv_files(str(base_path), str(rpm_path))
    else:
        # Fail is exception is thrown
        result = join_csv_files(str(base_path), str(rpm_path))

    
