import pandas as pd

def load_csv(path):
    return pd.read_csv(path, low_memory=False)
