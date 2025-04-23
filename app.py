import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import numpy as np

# Função para carregar e preparar os dados
def obter_dados():
    # Obter dados
    engine = f.criar_conexao(database='teste')
    sql = '''SELECT * FROM aux_comercial_agendamentos.metricas_pbi mp WHERE equipe IN ('Inbound','Outbound')'''
    df = f.select_para_df(engine=engine, sql=sql)
    engine.dispose()

    # Preparar dados
    df['data_venda'] = pd.to_datetime(df['data_venda'])

    # Filtrar últimos 12 meses fechados
    fim_mes_passado = pd.Timestamp.now().replace(day=1) - pd.Timedelta(days=1)
    inicio_12_meses = fim_mes_passado - pd.DateOffset(months=11)
    inicio_12_meses = inicio_12_meses.replace(day=1)

    df = df[(df['data_venda'] >= inicio_12_meses) & (df['data_venda'] <= fim_mes_passado)]
    
    df['mes_ordenada'] = df['data_venda'].dt.to_period('M')
    df_mensal = df.groupby('mes_ordenada', as_index=False)['mrr'].sum()
    df_mensal['mes'] = df_mensal['mes_ordenada'].dt.strftime('%m/%Y')

    return df, df_mensal

# Função para criar gráfico de MRR por mês
def criar_grafico_mrr(df_mensal):
    # Adicionar coluna numérica para linha de tendência
    df_mensal['x'] = range(len(df_mensal))
    z = np.polyfit(df_mensal['x'], df_mensal['mrr'], 1)
    p = np.poly1d(z)
    df_mensal['tendencia'] = p(df_mensal['x'])

    # Gráfico de barras
    fig = px.bar(
        df_mensal,
        x='mes',
        y='mrr',
        title='MRR (últimos 12 meses)',
        text_auto='.2s',
        color_discrete_sequence=['#2813AD']
    )
    fig.update_traces(textposition='outside')

    # Adicionar linha de tendência
    fig.add_trace(go.Scatter(
        x=df_mensal['mes'],
        y=df_mensal['tendencia'],
        mode='lines',
        name='Tendência',
        line=dict(color='orange', width=3, dash='dash')
    ))

    # Layout com título centralizado
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2813AD', size=14),
        yaxis_tickformat=',.2f',
        xaxis_title='',
        yaxis_title='MRR (R$)',
        title=dict(
            text='MRR (últimos 12 meses)',
            x=0.5,  # Centraliza o título
            xanchor='center',  # Garante que o título esteja centralizado
            font=dict(size=20)
        )
    )

    return fig

# Função para criar gráfico de MRR por vendedor (barra lateral)
def criar_grafico_vendedores(df):
    # Filtrar dados para o mês atual
    mes_atual = pd.Timestamp.now().replace(day=1) - pd.Timedelta(days=1)
    df_mes_atual = df[df['data_venda'].dt.month == mes_atual.month]

    # Agrupar por vendedor e somar MRR
    df_vendedores = df_mes_atual.groupby('vendedor', as_index=False)['mrr'].sum()

    # Ordenar do maior para o menor
    df_vendedores = df_vendedores.sort_values(by='mrr', ascending=True)

    # Reordenar os nomes dos vendedores explicitamente para o eixo y
    df_vendedores['vendedor'] = pd.Categorical(df_vendedores['vendedor'], categories=df_vendedores['vendedor'], ordered=True)

    # Definir cor com base no valor do MRR
    df_vendedores['cor'] = df_vendedores['mrr'].apply(lambda x: '#2813AD' if x > 5000 else 'red')

    # Gráfico de barras horizontal
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

    # Forçar o eixo y a seguir a ordem da categoria
    fig.update_yaxes(categoryorder='array', categoryarray=df_vendedores['vendedor'].tolist())

    # Layout final
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

# Configuração da página
st.set_page_config(layout='wide', page_title="Painel de Vendas", page_icon="📊")
st_autorefresh(interval=300 * 1000, key="refresh")

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

# Data de atualização
st.markdown(f"**⏰ Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Título
st.title("📊 Painel de Vendas")

# Obter dados
df, df_mensal = obter_dados()

# Gráfico 1: MRR por Mês
fig_mrr = criar_grafico_mrr(df_mensal)

# Gráfico 2: MRR por Vendedor
fig_vendedores = criar_grafico_vendedores(df)

# Exibir gráficos em colunas (lado a lado)
col1, col2 = st.columns(2)

# Gráfico de MRR por Mês
with col1:
    st.plotly_chart(fig_mrr, use_container_width=True)

# Gráfico de MRR por Vendedor (barra lateral)
with col2:
    st.plotly_chart(fig_vendedores, use_container_width=True)
