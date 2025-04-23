import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(layout='wide')
st_autorefresh(interval=30 * 1000, key="refresh")

st.write("Última atualização:", datetime.now().strftime("%H:%M:%S"))

engine = f.criar_conexao(connection= 'relatorios_azure',database= 'piperun_clean')
sql = '''SELECT data_venda, mrr, vendedor FROM teste.streamlit '''
df = f.select_para_df(engine=engine,sql=sql)

# df = pd.DataFrame({
#     'data_venda': pd.date_range(start='2025-03-29', periods=10),
#     'mrr': [1000, 1200, 1500, 1700, 1600, 1800, 2100, 1900, 2200, 2000],
#     'vendedor': ['Alice', 'Bob', 'Carlos', 'Alice', 'Bob', 'Carlos', 'Alice', 'Bob', 'Carlos', 'Alice']
# })

df['data_venda'] = pd.to_datetime(df['data_venda'])

df['mes'] = df['data_venda'].apply(lambda x: x.strftime('%Y-%m'))

#month = st.sidebar.selectbox('Mês', df['mes'].unique())
#df_filtered = df[df['mes'] == month]
#df_filtered

col1, col2 = st.columns(2)

fig_date = px.bar(df, x='mes', y='mrr', title='MRR')

col1.plotly_chart(fig_date)
