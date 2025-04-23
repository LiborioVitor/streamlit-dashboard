import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import requests

# Configuração da página
st.set_page_config(layout='wide', page_title="Dashboard MRR", page_icon="📊")
st_autorefresh(interval=30 * 1000, key="refresh")

# Estilização
st.markdown("""
    <style>
        .main {
            background-color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3, h4 {
            color: #2813AD;
        }
    </style>
""", unsafe_allow_html=True)

# Título e atualização
st.title("📈 Acompanhamento de MRR")
st.write("Última atualização:", datetime.now().strftime("%H:%M:%S"))

# Descobrir IP
try:
    ip = requests.get('https://api.ipify.org').text
    st.info(f"🌐 IP público da máquina: {ip}")
except:
    st.warning("⚠️ Não foi possível descobrir o IP público.")

# Obter dados
engine = f.criar_conexao(connection='relatorios_azure', database='piperun_clean')
sql = '''SELECT data_venda, mrr, vendedor FROM teste.streamlit'''
df = f.select_para_df(engine=engine, sql=sql)

# Preparar dados
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['mes'] = df['data_venda'].dt.strftime('%Y-%m')

# Filtro por vendedor
vendedores = df['vendedor'].dropna().unique()
vendedor_selecionado = st.selectbox("👤 Selecione o vendedor", options=['Todos'] + list(vendedores))

if vendedor_selecionado != 'Todos':
    df = df[df['vendedor'] == vendedor_selecionado]

# Gráfico MRR por mês
fig_date = px.bar(
    df.groupby('mes', as_index=False).sum(numeric_only=True),
    x='mes',
    y='mrr',
    title='MRR por Mês',
    color_discrete_sequence=['#2813AD']
)
fig_date.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#2813AD', size=14)
)

# Gráfico MRR acumulado
df_agg = df.groupby('mes', as_index=True).sum(numeric_only=True).sort_index()
df_agg['MRR acumulado'] = df_agg['mrr'].cumsum()
fig_cumsum = px.line(
    df_agg,
    x=df_agg.index,
    y='MRR acumulado',
    title='MRR Acumulado',
    markers=True,
    line_shape='spline',
    color_discrete_sequence=['#13AD7C']
)
fig_cumsum.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#2813AD', size=14)
)

# Layout em colunas
col1, col2 = st.columns(2)
col1.plotly_chart(fig_date, use_container_width=True)
col2.plotly_chart(fig_cumsum, use_container_width=True)

# Download dos dados
st.markdown("---")
st.download_button("📥 Baixar dados filtrados", df.to_csv(index=False).encode('utf-8'), "mrr.csv", "text/csv")
