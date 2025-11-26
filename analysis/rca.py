
from pipeline.etl import load_orders, aggregate_hourly, top_delay_drivers
if __name__ == '__main__':
    df = load_orders()
    hourly = aggregate_hourly(df)
    worst = hourly.sort_values('sla_adherence_pct').head(10)
    print('Worst hours by SLA:')
    print(worst[['timestamp','orders','sla_adherence_pct']])
    items, hours = top_delay_drivers(df)
    print('\nTop items by avg processing time:')
    print(items.head(10))
