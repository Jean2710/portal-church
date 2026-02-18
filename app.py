import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, time
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portal da Ala", page_icon="⛪", layout="wide")

# --- CONEXÃO GOOGLE SHEETS ---
# Garante que os dados sejam salvos na nuvem para sempre
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    return conn.read(worksheet=aba, ttl="0")

def adicionar_comunicado(t, m, a, l, img_path):
    df_atual = ler_dados("comunicados")
    nova_linha = pd.DataFrame([{
        "data_postagem": datetime.now().strftime("%Y-%m-%d"),
        "titulo": t, "mensagem": m, "autor": a, "link": l, "imagem": img_path
    }])
    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
    conn.update(worksheet="comunicados", data=df_final)
    st.cache_data.clear()

# --- FUNÇÃO DE INDICADORES (MANTENDO SEUS EXPANDERS) ---
def exibir_indicadores_profeticos():
    st.header("📊 Prioridades Proféticas - Brasil")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("FREQUÊNCIA SACRAMENTAL", "109", "-1 p/ Meta")
    col2.metric("MEMBROS PARTICIPANTES", "102", "-13 p/ Meta")
    col3.metric("BATISMOS", "4", "-16 p/ Meta")
    col4.metric("MISSIONÁRIOS", "1", "-1 p/ Meta")
    
    meta_data_grafico = {"Indicador": ["Frequência", "Templo", "Retorno", "Jejum", "Batismos", "Missionários"], "Atual": [109, 102, 0, 20, 4, 1], "Meta": [110, 115, 10, 34, 20, 2]}
    fig = go.Figure(data=[
        go.Bar(name='Atual', x=meta_data_grafico['Indicador'], y=meta_data_grafico['Atual'], marker_color='#1e3a8a'),
        go.Bar(name='Meta', x=meta_data_grafico['Indicador'], y=meta_data_grafico['Meta'], marker_color='#93c5fd')
    ])
    st.plotly_chart(fig, use_container_width=True)
    
    # --- O EXPANDER E TABELA QUE VOCÊ PEDIU ---
    with st.expander("📋 Visualizar Tabela Detalhada de Metas"):
        df_pdf = pd.DataFrame({
            "Categoria": ["VIVER", "VIVER", "CUIDAR NECESSITADOS", "CUIDAR NECESSITADOS", "CONVIDAR TODOS", "CONVIDAR TODOS", "UNIR FAMÍLIAS", "UNIR FAMÍLIAS"],
            "Indicador": ["Frequência Sacramental", "Membros Participantes", "Membros Retornando", "Membros Jejuando", "Batismos de Conversos", "Missionários Servindo no Brasil", "Membros com Investidura", "Membros sem Investidura"],
            "Atual": [109, 102, 0, 20, 4, 1, 49, 26],
            "Meta": [110, 115, 10, 34, 20, 2, 50, 30]
        })
        st.table(df_pdf)

# --- Exemplo de como fica o Bispado com Expander ---
# def painel_bispado():
#    ... outras funções ...
#    with st.expander("⚙️ Gerenciar Tarefas"):
#        df_t = ler_dados("tarefas_bispado")
#        st.dataframe(df_t)