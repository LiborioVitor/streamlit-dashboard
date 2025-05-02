import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# Configuração da página (deve ser primeiro comando Streamlit)
st.set_page_config(layout='wide', page_title="Painel de Vendas", page_icon="📈")

# Autoatualização padrão
st_autorefresh(interval=30 * 1000, key="refresh")

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 0

# Alternar entre 0 e 1
st.session_state.pagina_atual = (st.session_state.pagina_atual + 1) % 2

# Cabeçalho visual
st.markdown("""
    <style>
        html, body, .main, .block-container, .stApp {
            background-color: white !important;
            color: #000000 !important;
        }
        .block-container {
            padding-top: 0.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        h1 {
            color: #2813AD !important;
            font-size: 2.6em !important;
            text-align: center;
            margin-bottom: 0.2rem !important;
            margin-top: 0 !important;
        }
        h6 {
            text-align: center;
            color: #666666 !important;
            font-size: 1.1em !important;
            margin-top: 0 !important;
        }
        .stMarkdown, .stText, .stPlotlyChart {
            font-size: 1.3em !important;
            color: #000000 !important;
        }
        .js-plotly-plot .plotly .modebar {
            display: none !important;
        }
        .plot-container .main-svg {
            color: #000000 !important;
        }
        #MainMenu, footer, header {
            visibility: hidden;
        }
        .viewerBadge_container__1QSob {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style="text-align: center;">
        📈 Painel de Vendas
    </h1>
    <h6>Atualizado em: {}</h6>
""".format((datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)

# Função para obter os dados
def obter_dados():
    engine = f.criar_conexao(database='streamlit')
    sql = '''
        SELECT data_venda, vendedor, mrr, id_venda
        FROM streamlit.vendas
    '''
    df = f.select_para_df(engine=engine, sql=sql)
    engine.dispose()
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    return df

# Gráfico 1 - MRR por dia
def criar_grafico_mrr_por_dia(df):
    hoje = pd.Timestamp.now().normalize()
    dez_dias_atras = hoje - pd.Timedelta(days=9)
    dias = pd.date_range(start=dez_dias_atras, end=hoje)

    df_dia = df.groupby('data_venda')['mrr'].sum().reset_index()
    df_dia = df_dia.set_index('data_venda').reindex(dias, fill_value=0).reset_index()
    df_dia = df_dia.rename(columns={'index': 'data_venda'})

    df_dia['mrr_formatado'] = df_dia['mrr'].map('{:,.0f}'.format).str.replace(',', '.')

    fig = px.bar(
        df_dia,
        x='data_venda',
        y='mrr',
        title='MRR por Dia (10 dias)',
        text='mrr_formatado',
        color_discrete_sequence=['#2813AD']
    )
    fig.update_traces(textposition='outside')

    y_max = df_dia['mrr'].max()
    fig.update_yaxes(range=[0, y_max * 1.1])

    fig.update_xaxes(
        tickmode='array',
        tickvals=df_dia['data_venda'],
        ticktext=df_dia['data_venda'].dt.strftime('%d/%m'),
        title='Data'
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#000000', size=16),
        xaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=16)),
        yaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=16)),
        yaxis_title='MRR (R$)',
        title=dict(x=0.5, xanchor='center', font=dict(color='#000000', size=22)),
        margin=dict(t=70, b=40),
        showlegend=False
    )
    return fig

# Gráfico 2 - MRR por vendedor
def criar_grafico_mrr_por_vendedor(df):
    hoje = pd.Timestamp.now()
    primeiro_dia = hoje.replace(day=1)
    df_mes = df[df['data_venda'] >= primeiro_dia]

    df_vendedor = df_mes.groupby('vendedor')['mrr'].sum().reset_index()
    df_vendedor = df_vendedor.sort_values(by='mrr', ascending=True)
    df_vendedor['vendedor'] = pd.Categorical(df_vendedor['vendedor'], categories=df_vendedor['vendedor'], ordered=True)
    df_vendedor['mrr_formatado'] = df_vendedor['mrr'].map('{:,.0f}'.format).str.replace(',', '.')

    fig = px.bar(
        df_vendedor,
        x='mrr',
        y='vendedor',
        title='MRR por Vendedor (Mês Atual)',
        text='mrr_formatado',
        color_discrete_sequence=['#2813AD'],
        orientation='h'
    )
    fig.update_traces(textposition='outside')

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#000000', size=16),
        xaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=16)),
        yaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=18)),
        xaxis_title='MRR (R$)',
        yaxis_title='Vendedor',
        title=dict(x=0.5, xanchor='center', font=dict(color='#000000', size=22)),
        margin=dict(t=70, b=40),
        showlegend=False
    )
    return fig

# Executar
df = obter_dados()
fig_mrr_dia = criar_grafico_mrr_por_dia(df)
fig_mrr_vendedor = criar_grafico_mrr_por_vendedor(df)

# col1, col2 = st.columns(2)
# with col1:
#     st.plotly_chart(fig_mrr_dia, use_container_width=True, config={'displayModeBar': False})
# with col2:
#     st.plotly_chart(fig_mrr_vendedor, use_container_width=True, config={'displayModeBar': False})

if st.session_state.pagina_atual == 0:
    st.subheader("📊 MRR por Dia (Últimos 10 dias)")
    st.plotly_chart(fig_mrr_dia, use_container_width=True, config={"displayModeBar": False})
else:
    st.subheader("📊 MRR por Vendedor (Mês Atual)")
    st.plotly_chart(fig_mrr_vendedor, use_container_width=True, config={"displayModeBar": False})
