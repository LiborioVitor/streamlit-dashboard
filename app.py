import _functions as f
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import holidays

# Configuração da página
st.set_page_config(layout='wide', page_title="Painel de Reunião", page_icon="📊")

# Autoatualização a cada 5 minutos
st_autorefresh(interval=60 * 1000, key="refresh")

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
st.title("📊 Painel de Reunião")
st.markdown(f"**⏰ Atualizado em:** `{datetime.now().strftime('%H:%M:%S')}`")

# Função para carregar e preparar os dados
def obter_dados():
    engine = f.criar_conexao(database='teste')
    sql = '''SELECT oportunidade, pre_venda, vendedor, data_reuniao FROM streamlit.reuniao'''
    df = f.select_para_df(engine=engine, sql=sql)
    engine.dispose()

    df['data_reuniao'] = pd.to_datetime(df['data_reuniao'])
    return df

def criar_grafico_reunioes_por_dia(df):
    # Parâmetros
    meta = 20
    hoje = pd.Timestamp.now().normalize()
    dez_dias_atras = hoje - pd.Timedelta(days=9)
    dias = pd.date_range(start=dez_dias_atras, end=hoje)

    # Feriados no Brasil (pode ajustar o estado se quiser)
    feriados_br = holidays.Brazil()

    # Contagem de reuniões por dia
    df_dia = df.groupby('data_reuniao').size().reset_index(name='qtd_reunioes')
    df_dia = df_dia.set_index('data_reuniao').reindex(dias, fill_value=0).reset_index()
    df_dia = df_dia.rename(columns={'index': 'data_reuniao'})

    # Formatação
    df_dia['qtd_formatada'] = df_dia['qtd_reunioes'].map('{:,.0f}'.format).str.replace(',', '.')

    # Verificar se é dia útil
    df_dia['dia_util'] = df_dia['data_reuniao'].apply(
        lambda x: x.weekday() < 5 and x not in feriados_br
    )

    # Cores com base na meta (aplica vermelho só em dia útil)
    df_dia['cor'] = df_dia.apply(
        lambda row: '#2813AD' if row['qtd_reunioes'] >= meta or not row['dia_util'] else 'red',
        axis=1
    )

    # Gráfico
    fig = px.bar(
        df_dia,
        x='data_reuniao',
        y='qtd_reunioes',
        title='Reuniões por Dia (Últimos 10 dias)',
        text='qtd_formatada',
        color='cor',
        color_discrete_map={'#2813AD': '#2813AD', 'red': 'red'}
    )

    fig.update_traces(textposition='outside')

    # Linha de meta
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
        text=f'Meta: {meta} reuniões',
        showarrow=False,
        font=dict(color='orange', size=12),
        bgcolor='white'
    )

    # Eixo Y
    y_max = max(df_dia['qtd_reunioes'].max(), meta)
    fig.update_yaxes(range=[0, y_max * 1.1])

    # Eixo X com datas formatadas
    fig.update_xaxes(
        tickmode='array',
        tickvals=df_dia['data_reuniao'],
        ticktext=df_dia['data_reuniao'].dt.strftime('%d/%m/%Y'),
        title='Data'
    )

    # Layout final
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2813AD', size=14),
        yaxis_title='Qtd. de Reuniões',
        title=dict(
            text='Reuniões por Dia (Últimos 10 dias)',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        margin=dict(t=80),
        showlegend=False
    )

    return fig

def criar_grafico_por_pre_venda(df):
    # Filtrar apenas reuniões do mês atual
    hoje = pd.Timestamp.now()
    primeiro_dia = hoje.replace(day=1)
    df_mes = df[df['data_reuniao'] >= primeiro_dia]

    # Agrupar por pre_venda e contar
    df_pre = df_mes.groupby('pre_venda').size().reset_index(name='qtd_reunioes')

    # Ordenar do maior para o menor
    df_pre = df_pre.sort_values(by='qtd_reunioes', ascending=True)

    # Garantir ordenação correta no eixo y
    df_pre['pre_venda'] = pd.Categorical(df_pre['pre_venda'], categories=df_pre['pre_venda'], ordered=True)

    # Formatar quantidade
    df_pre['qtd_formatada'] = df_pre['qtd_reunioes'].map('{:,.0f}'.format).str.replace(',', '.')

    # Gráfico de barras horizontal
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
        font=dict(color='#2813AD', size=14),
        xaxis_title='Qtd. de Reuniões',
        yaxis_title='Pré-Venda',
        title=dict(
            text='Reuniões por Pré-Venda (Mês Atual)',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        margin=dict(t=80),
        showlegend=False
    )

    return fig


# Obter dados
df = obter_dados()

# Criar e exibir gráfico
fig_reunioes_dia = criar_grafico_reunioes_por_dia(df)
fig_pre_venda = criar_grafico_por_pre_venda(df)

# Exibir os dois gráficos lado a lado
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_reunioes_dia, use_container_width=True)
with col2:
    st.plotly_chart(fig_pre_venda, use_container_width=True)
