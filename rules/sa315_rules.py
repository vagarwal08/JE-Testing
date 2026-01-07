def apply_sa315_rules(df):
    df["SA315_SCORE"] = 0

    df.loc[df["IS_MANUAL"] == 1, "SA315_SCORE"] += 3
    df.loc[df["CPUTM"] > 20, "SA315_SCORE"] += 2
    df.loc[df["BUDAT"].dt.weekday >= 5, "SA315_SCORE"] += 2

    high_value = df["DMBTR"].quantile(0.99)
    df.loc[df["DMBTR"] > high_value, "SA315_SCORE"] += 3

    df.loc[
        (df["HKONT"].astype(str).str.startswith("5")) &
        (df["KOSTL"].isna()),
        "SA315_SCORE"
    ] += 2

    return df
