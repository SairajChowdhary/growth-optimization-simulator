
import pandas as pd
from pathlib import Path
DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'real_sample_orders.csv'
def load_orders(path=None):
    p = path or DATA_PATH
    df = pd.read_csv(p, parse_dates=['timestamp'])
    return df
def aggregate_hourly(df):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    g = df.groupby(pd.Grouper(key='timestamp', freq='H')).agg(
        orders=('order_id','count'),
        fulfilled=('fulfilled','mean'),
        avg_processing_min=('processing_time_min','mean'),
        stock_out_rate=('stock_out','mean'),
        avg_cost=('cost','mean')
    ).reset_index()
    g['hour'] = g['timestamp'].dt.hour
    g['day'] = g['timestamp'].dt.date
    g['sla_adherence_pct'] = g['fulfilled']*100
    return g
def top_delay_drivers(df, top_n=10):
    item = df.groupby('item_id').processing_time_min.mean().sort_values(ascending=False).head(top_n)
    hour = df.groupby(df['timestamp'].dt.hour).processing_time_min.mean().sort_values(ascending=False).head(top_n)
    return item, hour
if __name__ == '__main__':
    df = load_orders()
    print('Loaded rows:', len(df))
    print(aggregate_hourly(df).head())
