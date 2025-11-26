
import streamlit as st
import plotly.express as px
from pipeline.etl import load_orders, aggregate_hourly, top_delay_drivers
from pathlib import Path
st.set_page_config(page_title='Instamart Ops Dashboard', layout='wide')
PALETTE = px.colors.sequential.Reds
DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'real_sample_orders.csv'
@st.cache_data
def load_data():
    df = load_orders(DATA_PATH)
    return df
df = load_data()
st.title('Instamart Dark Store — Ops Dashboard (v2)')
with st.sidebar:
    st.header('Filters')
    hours = st.multiselect('Hour(s)', options=sorted(df.hour.unique()), default=sorted(df.hour.unique()))
    item_search = st.text_input('Item contains (regex supported)')
    min_orders = st.slider('Min orders per hour (filter aggregated)', 0, 50, 0)
    download = st.button('Prepare CSV for download')
if item_search:
    df = df[df.item_id.str.contains(item_search, regex=True)]
if hours:
    df = df[df.hour.isin(hours)]
agg = aggregate_hourly(df)
agg_filtered = agg[agg.orders >= min_orders]
col1, col2, col3, col4 = st.columns(4)
col1.metric('Avg SLA Adherence (%)', f"{agg_filtered.sla_adherence_pct.mean():.2f}")
col2.metric('Avg Orders / hour', f"{agg_filtered.orders.mean():.1f}")
col3.metric('Avg Processing (min)', f"{agg_filtered.avg_processing_min.mean():.2f}")
col4.metric('Stock-out rate (%)', f"{(agg_filtered.stock_out_rate.mean()*100):.2f}")
if download:
    to_download = df.copy()
    st.download_button('Download filtered raw CSV', to_download.to_csv(index=False), file_name='filtered_orders_v2.csv', mime='text/csv')
st.markdown('### Orders by hour (aggregated)')
fig = px.bar(agg_filtered.groupby('hour').orders.mean().reset_index().sort_values('hour'), x='hour', y='orders', color='orders', color_continuous_scale=PALETTE)
st.plotly_chart(fig, use_container_width=True)
st.markdown('### SLA adherence over time')
fig2 = px.line(agg_filtered.sort_values('timestamp'), x='timestamp', y='sla_adherence_pct', line_shape='spline')
st.plotly_chart(fig2, use_container_width=True)
st.markdown('### Top delay drivers')
items, hours_top = top_delay_drivers(df)
st.dataframe(items.reset_index().rename(columns={'item_id':'item','processing_time_min':'avg_proc_min'}).head(10))
st.markdown('### Forecasting comparison (Prophet vs GBR)')
from models.forecast_and_ab_test import compare_models
with st.spinner('Running forecasting comparison...'):
    res = compare_models()
st.json(res)
