import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import holidays

# Configuração da página
st.set_page_config(layout='wide', page_title="Painel de Reunião", page_icon="📊")

# Autoatualização a cada 10 minutos
st_autorefresh(interval=600 * 1000, key="refresh")

# Estilização profissional para TV
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

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .viewerBadge_container__1QSob {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Log de atualização + cabeçalho
st.markdown("""
    <h1>📊 Painel de Reuniões</h1>
    <h6>Atualizado em: {}</h6>
""".format((datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)

# Função para obter os dados
def obter_dados():
    engine = f.criar_conexao(database='teste')
    sql = '''
        SELECT oportunidade, 
               pre_venda,
               vendedor,
               STR_TO_DATE(data_reuniao_calculada, '%d/%m/%Y') AS data_reuniao
        FROM aux_comercial_agendamentos.reunioes_sdrs_geral rsg 
        LEFT JOIN comportamento.equipes e ON rsg.pre_venda = e.username
        WHERE STR_TO_DATE(data_reuniao_calculada, '%d/%m/%Y') >= NOW() - INTERVAL 10 DAY
          AND reuniao_ocorrida = 1
          AND e.sub_equipe = 'SDR'
          AND username <> 'Deivid Rocha'
    '''
    df = f.select_para_df(engine=engine, sql=sql)
    engine.dispose()
    df['data_reuniao'] = pd.to_datetime(df['data_reuniao'])
    return df

# Gráfico 1 - Reuniões por dia
def criar_grafico_reunioes_por_dia(df):
    meta = 25
    hoje = pd.Timestamp.now().normalize()
    dez_dias_atras = hoje - pd.Timedelta(days=9)
    dias = pd.date_range(start=dez_dias_atras, end=hoje)
    feriados_br = holidays.Brazil()

    df_dia = df.groupby('data_reuniao').size().reset_index(name='qtd_reunioes')
    df_dia = df_dia.set_index('data_reuniao').reindex(dias, fill_value=0).reset_index()
    df_dia = df_dia.rename(columns={'index': 'data_reuniao'})

    df_dia['qtd_formatada'] = df_dia['qtd_reunioes'].map('{:,.0f}'.format).str.replace(',', '.')
    df_dia['dia_util'] = df_dia['data_reuniao'].apply(lambda x: x.weekday() < 5 and x not in feriados_br)
    df_dia['cor'] = df_dia.apply(lambda row: '#2813AD' if row['qtd_reunioes'] >= meta or not row['dia_util'] else 'red', axis=1)

    fig = px.bar(
        df_dia,
        x='data_reuniao',
        y='qtd_reunioes',
        title='Reuniões por Dia (10 dias)',
        text='qtd_formatada',
        color='cor',
        color_discrete_map={'#2813AD': '#2813AD', 'red': 'red'}
    )
    fig.update_traces(textposition='outside')

    fig.add_shape(
        type="line",
        x0=df_dia['data_reuniao'].min(),
        x1=df_dia['data_reuniao'].max(),
        y0=meta,
        y1=meta,
        line=dict(color='orange', width=3, dash='dash'),
    )

    fig.add_annotation(
        x=df_dia['data_reuniao'].max(),
        y=meta,
        text='Meta: 25 reuniões',
        showarrow=False,
        font=dict(color='orange', size=12),
        bgcolor='white'
    )

    y_max = max(df_dia['qtd_reunioes'].max(), meta)
    fig.update_yaxes(range=[0, y_max * 1.1])

    fig.update_xaxes(
        tickmode='array',
        tickvals=df_dia['data_reuniao'],
        ticktext=df_dia['data_reuniao'].dt.strftime('%d/%m'),
        title='Data'
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#000000', size=16),
        xaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=16)),
        yaxis=dict(title_font=dict(color='#000000'), tickfont=dict(color='#000000', size=16)),
        yaxis_title='Qtd. de Reuniões',
        title=dict(x=0.5, xanchor='center', font=dict(size=22)),
        margin=dict(t=70, b=40),
        showlegend=False
    )
    return fig

# Gráfico 2 - Reuniões por pré-venda
def criar_grafico_por_pre_venda(df):
    hoje = pd.Timestamp.now()
    primeiro_dia = hoje.replace(day=1)
    df_mes = df[df['data_reuniao'] >= primeiro_dia]

    df_pre = df_mes.groupby('pre_venda').size().reset_index(name='qtd_reunioes')
    df_pre = df_pre.sort_values(by='qtd_reunioes', ascending=True)
    df_pre['pre_venda'] = pd.Categorical(df_pre['pre_venda'], categories=df_pre['pre_venda'], ordered=True)
    df_pre['qtd_formatada'] = df_pre['qtd_reunioes'].map('{:,.0f}'.format).str.replace(',', '.')

    fig = px.bar(
        df_pre,
        x='qtd_reunioes',
        y='pre_venda',
        title='Reuniões por Pré-Venda (Mês Atual)',
        text='qtd_formatada',
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
        xaxis_title='Qtd. de Reuniões',
        yaxis_title='Pré-Venda',
        title=dict(x=0.5, xanchor='center', font=dict(size=22)),
        margin=dict(t=70, b=40),
        showlegend=False
    )
    return fig

# Executar
df = obter_dados()
fig_reunioes_dia = criar_grafico_reunioes_por_dia(df)
fig_pre_venda = criar_grafico_por_pre_venda(df)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_reunioes_dia, use_container_width=True, config={'displayModeBar': False})
with col2:
    st.plotly_chart(fig_pre_venda, use_container_width=True, config={'displayModeBar': False})
