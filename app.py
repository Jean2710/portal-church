import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portal da Ala", page_icon="⛪", layout="wide")

# --- CONEXÃO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    """
    Lê dados da planilha com cache de 10 minutos (600s) para performance.
    O cache é limpo automaticamente em funções de escrita (update).
    """
    try:
        # ttl="600" mantém os dados rápidos; st.cache_data.clear() limpa quando necessário
        return conn.read(worksheet=aba, ttl="600")
    except Exception as e:
        st.error(f"Erro ao conectar com a aba '{aba}': {e}")
        return pd.DataFrame()

def adicionar_comunicado(t, m, a, l, img_url):
    """
    Adiciona comunicado salvando a URL da imagem (indicado para nuvem).
    """
    df_atual = ler_dados("comunicados")
    nova_linha = pd.DataFrame([{
        "data_postagem": datetime.now().strftime("%Y-%m-%d"),
        "titulo": t, 
        "mensagem": m, 
        "autor": a, 
        "link": l, 
        "imagem": img_url  # Recomendação: Use URLs de imagem (Drive/ImgBB)
    }])
    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
    conn.update(worksheet="comunicados", data=df_final)
    st.cache_data.clear() # Limpa o cache para mostrar o novo post imediatamente
    st.success("Comunicado adicionado com sucesso!")

# --- FUNÇÃO DE INDICADORES DINÂMICOS ---
def exibir_indicadores_profeticos():
    st.header("📊 Prioridades Proféticas - Brasil")
    
    # Carregando dados dinâmicos da aba 'metas'
    df_metas = ler_dados("metas")
    
    if not df_metas.empty:
        # 1. KPIs no topo (pegando os 4 primeiros indicadores da planilha)
        cols = st.columns(4)
        for i, row in df_metas.head(4).iterrows():
            diferenca = row['Atual'] - row['Meta']
            delta_msg = f"{diferenca} p/ Meta" if diferenca < 0 else "Meta Atingida"
            cols[i].metric(row['Indicador'].upper(), str(row['Atual']), delta_msg)

        # 2. Gráfico Plotly Dinâmico
        fig = go.Figure(data=[
            go.Bar(name='Atual', x=df_metas['Indicador'], y=df_metas['Atual'], marker_color='#1e3a8a'),
            go.Bar(name='Meta', x=df_metas['Indicador'], y=df_metas['Meta'], marker_color='#93c5fd')
        ])
        fig.update_layout(barmode='group', margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. Expander com a Tabela Completa (conforme sua solicitação)
        with st.expander("📋 Visualizar Tabela Detalhada de Metas"):
            st.table(df_metas)
    else:
        st.warning("Crie uma aba chamada 'metas' na sua planilha com as colunas: Categoria, Indicador, Atual, Meta.")

# --- INTERFACE PRINCIPAL ---
def main():
    # Aqui você chamaria suas funções de navegação
    exibir_indicadores_profeticos()

if __name__ == "__main__":
    main()