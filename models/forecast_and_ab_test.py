
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from pipeline.etl import load_orders
DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'real_sample_orders.csv'
def prepare_ts(df):
    df2 = df.copy()
    df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    ts = df2.groupby(pd.Grouper(key='timestamp', freq='H')).agg(orders=('order_id','count')).reset_index()
    ts.columns = ['ds','y']
    return ts
def train_prophet(ts):
    try:
        from prophet import Prophet
    except Exception as e:
        print('Prophet import failed:', e)
        return None, None
    m = Prophet(daily_seasonality=True)
    m.fit(ts)
    future = m.make_future_dataframe(periods=24, freq='H')
    forecast = m.predict(future)
    merged = forecast[['ds','yhat']].merge(ts, on='ds', how='left')
    merged = merged.dropna(subset=['y'])
    mae = None
    if not merged.empty:
        mae = float(mean_absolute_error(merged['y'], merged['yhat']))
    return m, mae
def train_gbr(ts):
    df = ts.copy()
    df['hour'] = df['ds'].dt.hour
    for lag in range(1,25):
        df[f'lag_{lag}'] = df['y'].shift(lag)
    df = df.dropna().reset_index(drop=True)
    X = df.drop(columns=['ds','y'])
    y = df['y']
    tscv = TimeSeriesSplit(n_splits=3)
    train_idx, test_idx = list(tscv.split(X))[-1]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    return model, mae
def compare_models():
    df = load_orders(DATA_PATH)
    ts = prepare_ts(df)
    prophet_mae = None
    try:
        m, prophet_mae = train_prophet(ts)
    except Exception as e:
        print('Prophet training skipped:', e)
    gbr_model, gbr_mae = train_gbr(ts)
    return {'prophet_mae': prophet_mae, 'gbr_mae': gbr_mae}
if __name__ == '__main__':
    print(compare_models())
