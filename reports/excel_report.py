def export_excel(df, path):
    df.sort_values(
        "FINAL_RISK_SCORE",
        ascending=False
    ).to_excel(path, index=False)
