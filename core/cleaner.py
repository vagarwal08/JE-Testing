def clean_columns(df):
    df.columns = (
        df.columns.str.upper()
        .str.strip()
        .str.replace(" ", "_")
    )
    return df
