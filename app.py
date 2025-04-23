import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

engine = f.criar_conexao(connection= 'relatorios_azure',database= 'piperun_clean')

sql = '''select data_venda, mrr, vendedor from datasales.vendas_base where year(data_venda) = 2025 and equipe in ('Inbound','Outbound') '''

df = f.select_para_df(engine=engine,sql=sql)

df['data_venda'] = pd.to_datetime(df['data_venda'])

df['mes'] = df['data_venda'].apply(lambda x: x.strftime('%Y-%m'))

#month = st.sidebar.selectbox('Mês', df['mes'].unique())
#df_filtered = df[df['mes'] == month]
#df_filtered

col1, col2 = st.columns(2)

fig_date = px.bar(df, x='mes', y='mrr', title='MRR')

col1.plotly_chart(fig_date)
