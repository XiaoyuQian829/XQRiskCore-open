# utils/dataframe_utils.py

import pandas as pd

def with_string_index(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df.index = [str(i + 1) for i in range(len(df))]
    df.index.name = "#"
    return df
