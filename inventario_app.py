import streamlit as st
import pandas as pd

st.title("Sistema de Inventário - Comparação de Saldos")

# Inicializar estado da sessão
if "df_sistema" not in st.session_state:
    st.session_state.df_sistema = None

# Botão para iniciar novo inventário
if st.button("Novo Inventário"):
    st.session_state.df_sistema = None
    st.experimental_rerun()

# Upload do arquivo Excel
if st.session_state.df_sistema is None:
    uploaded_file = st.file_uploader("Faça upload do arquivo de inventário do sistema (formato .xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name="Planilha1", engine="openpyxl")
        st.session_state.df_sistema = df[["IdentProduto", "Quantidade"]].copy()

# Se os dados do sistema estiverem carregados
if st.session_state.df_sistema is not None:
    df_sistema = st.session_state.df_sistema.copy()

    st.subheader("Dados do Sistema")
    st.dataframe(df_sistema)

    st.subheader("Inserir Saldo Físico")
    saldo_fisico = {}

    with st.form("form_saldo_fisico"):
        for produto in df_sistema["IdentProduto"].unique():
            saldo = st.number_input(f"Saldo físico para {produto}", min_value=0, step=1, key=produto)
            saldo_fisico[produto] = saldo
        submitted = st.form_submit_button("Comparar Saldos")

    if submitted:
        df_sistema["SaldoFisico"] = df_sistema["IdentProduto"].map(saldo_fisico)
        df_sistema["Divergencia"] = df_sistema["SaldoFisico"] - df_sistema["Quantidade"]

        st.subheader("Relatório de Divergências")
        df_divergente = df_sistema[df_sistema["Divergencia"] != 0]
        st.dataframe(df_divergente)

    
