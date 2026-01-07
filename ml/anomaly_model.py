from sklearn.ensemble import IsolationForest

def run_ml_anomaly(df):
    features = df[
        ["DMBTR", "LINE_COUNT", "CPUTM", "IS_MANUAL"]
    ].fillna(0)

    model = IsolationForest(contamination=0.02, random_state=42)
    df["ML_FLAG"] = model.fit_predict(features)
    df["ML_ANOMALY"] = (df["ML_FLAG"] == -1).astype(int)

    return df
