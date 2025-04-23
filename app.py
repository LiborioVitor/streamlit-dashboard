import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(layout='wide', page_title="Painel de Vendas", page_icon="📊")

# Autoatualização a cada 30 segundos
st_autorefresh(interval=30 * 1000, key="refresh")

# Estilização visual
st.markdown("""
    <style>
        .main {
            background-color: white;
        }
        .block-container {
            padding-top: 3rem;
        }
        h1 {
            color: #2813AD;
        }
    </style>
""", unsafe_allow_html=True)

# Console log no navegador para debug
st.markdown("""
    <script>
        console.log("🕒 Página recarregada em", new Date().toLocaleTimeString());
    </script>
""", unsafe_allow_html=True)

# Título e horário de atualização
st.title("📊 Painel de Vendas")
st.markdown(f"**⏰ Atualizado em:** `{datetime.now().strftime('%H:%M:%S')}`")

# Função para carregar e preparar os dados
def obter_dados():
    engine = f.criar_conexao(database='teste')
    sql = '''SELECT * FROM aux_comercial_agendamentos.metricas_pbi mp WHERE equipe IN ('Inbound','Outbound')'''
    df = f.select_para_df(engine=engine, sql=sql)
    engine.dispose()

    df['data_venda'] = pd.to_datetime(df['data_venda'])

    fim_mes_passado = pd.Timestamp.now().replace(day=1) - pd.Timedelta(days=1)
    inicio_12_meses = fim_mes_passado - pd.DateOffset(months=11)
    inicio_12_meses = inicio_12_meses.replace(day=1)

    df = df[(df['data_venda'] >= inicio_12_meses) & (df['data_venda'] <= fim_mes_passado)]

    df['mes_ordenada'] = df['data_venda'].dt.to_period('M')
    df_mensal = df.groupby('mes_ordenada', as_index=False)['mrr'].sum()
    df_mensal['mes'] = df_mensal['mes_ordenada'].dt.strftime('%m/%Y')

    return df, df_mensal

# Gráfico MRR por mês
def criar_grafico_mrr(df_mensal):
    df_mensal['x'] = range(len(df_mensal))
    z = np.polyfit(df_mensal['x'], df_mensal['mrr'], 1)
    p = np.poly1d(z)
    df_mensal['tendencia'] = p(df_mensal['x'])

    fig = px.bar(
        df_mensal,
        x='mes',
        y='mrr',
        title='MRR (últimos 12 meses)',
        text_auto='.2s',
        color_discrete_sequence=['#2813AD']
    )
    fig.update_traces(textposition='outside')

    fig.add_trace(go.Scatter(
        x=df_mensal['mes'],
        y=df_mensal['tendencia'],
        mode='lines',
        name='Tendência',
        line=dict(color='orange', width=3, dash='dash')
    ))

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2813AD', size=14),
        yaxis_tickformat=',.2f',
        xaxis_title='',
        yaxis_title='MRR (R$)',
        title=dict(
            text='MRR (últimos 12 meses)',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        )
    )
    return fig

# Gráfico MRR por vendedor
def criar_grafico_vendedores(df):
    mes_atual = pd.Timestamp.now().replace(day=1) - pd.Timedelta(days=1)
    df_mes_atual = df[df['data_venda'].dt.month == mes_atual.month]

    df_vendedores = df_mes_atual.groupby('vendedor', as_index=False)['mrr'].sum()
    df_vendedores = df_vendedores.sort_values(by='mrr', ascending=True)
    df_vendedores['vendedor'] = pd.Categorical(df_vendedores['vendedor'], categories=df_vendedores['vendedor'], ordered=True)
    df_vendedores['cor'] = df_vendedores['mrr'].apply(lambda x: '#2813AD' if x > 5000 else 'red')

    fig = px.bar(
        df_vendedores,
        x='mrr',
        y='vendedor',
        title='MRR por Vendedor (Mês Atual)',
        text_auto='.2s',
        color='cor',
        color_discrete_map={'#2813AD': '#2813AD', 'red': 'red'},
        orientation='h'
    )
    fig.update_yaxes(categoryorder='array', categoryarray=df_vendedores['vendedor'].tolist())

    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2813AD', size=14),
        xaxis_tickformat=',.2f',
        xaxis_title='MRR (R$)',
        yaxis_title='Vendedor',
        title=dict(
            text='MRR por Vendedor (Mês Atual)',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        )
    )
    return fig

# Obter dados
df, df_mensal = obter_dados()

# Criar gráficos
fig_mrr = criar_grafico_mrr(df_mensal)
fig_vendedores = criar_grafico_vendedores(df)

# Layout em colunas
col1, col2 = st.columns(2)
col1.plotly_chart(fig_mrr, use_container_width=True)
col2.plotly_chart(fig_vendedores, use_container_width=True)
