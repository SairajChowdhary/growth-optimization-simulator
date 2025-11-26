
from pipeline.etl import load_orders, aggregate_hourly
def test_load_and_aggregate():
    df = load_orders()
    assert len(df) == 200
    agg = aggregate_hourly(df)
    assert 'orders' in agg.columns
