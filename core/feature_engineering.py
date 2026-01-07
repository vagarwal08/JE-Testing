import pandas as pd

def add_features(df):
    df["BUDAT"] = pd.to_datetime(df["BUDAT"], errors="coerce")
    df["CPUTM"] = pd.to_datetime(df["CPUTM"], errors="coerce").dt.hour
    df["IS_MANUAL"] = df["TCODE"].isin(["FB01", "FB50", "F-02"]).astype(int)

    line_count = df.groupby("BELNR")["BUZEI"].count()
    df["LINE_COUNT"] = df["BELNR"].map(line_count)

    return df
