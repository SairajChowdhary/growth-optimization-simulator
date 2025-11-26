
import pandas as pd
from pathlib import Path
DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'real_sample_orders.csv'
def check_replenish(path=None, threshold=0.05):
    p = path or DATA_PATH
    df = pd.read_csv(p, parse_dates=['timestamp'])
    item_stats = df.groupby('item_id').stock_out.mean().reset_index().rename(columns={'stock_out':'stock_out_rate'})
    to_replenish = item_stats[item_stats.stock_out_rate > threshold].sort_values('stock_out_rate', ascending=False)
    return to_replenish
if __name__ == '__main__':
    print(check_replenish().head(10))
