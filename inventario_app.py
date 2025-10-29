import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO

st.title("Sistema de Inventário - Acuracidade e Divergências")

# Restaurar saldos físicos de arquivo
st.subheader("Restaurar Saldos Físicos de Arquivo")
arquivo_saldos = st.file_uploader("Carregar arquivo de saldos salvos (.xlsx)", type=["xlsx"], key="saldos")
if arquivo_saldos:
    df_saldos_restaurado = pd.read_excel(arquivo_saldos, sheet_name="SaldosAcumulados", engine="openpyxl")
    st.session_state.saldos_acumulados = dict(zip(df_saldos_restaurado["IdentProduto"], df_saldos_restaurado["SaldoFisico"]))
    st.success("Saldos restaurados com sucesso!")

# Upload do inventário do sistema
uploaded_file = st.file_uploader("Faça upload do arquivo de inventário do sistema (formato .xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Planilha1", engine="openpyxl")

    df["IdentProduto"] = df["IdentProduto"].astype(str)
    df["Descriçao"] = df["Descriçao"].astype(str)
    df["Prateleira"] = df["Prateleira"].astype(str)

    df_sistema = df[["IdentProduto", "Descriçao", "Quantidade", "ClassificABC", "Prateleira"]].copy()

    # Filtro por prateleira
    st.subheader("Filtrar por Prateleira")
    prateleiras_disponiveis = df_sistema["Prateleira"].unique()
    prateleiras_selecionadas = st.multiselect("Selecione uma ou mais prateleiras", prateleiras_disponiveis)
    if prateleiras_selecionadas:
        df_sistema = df_sistema[df_sistema["Prateleira"].isin(prateleiras_selecionadas)]

    st.subheader("Dados do Sistema")
    st.dataframe(df_sistema)

    st.subheader("Inserir Saldo Físico Acumulativo")

    if "saldos_acumulados" not in st.session_state:
        st.session_state.saldos_acumulados = {produto: 0 for produto in df_sistema["Ident


