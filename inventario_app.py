import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

st.title("Sistema de Inventário - Acuracidade e Divergências")

st.subheader("Restaurar Saldos Físicos de Arquivo")
arquivo_saldos = st.file_uploader("Carregar arquivo de saldos salvos (.xlsx)", type=["xlsx"], key="saldos")
if arquivo_saldos:
    df_saldos_restaurado = pd.read_excel(arquivo_saldos, sheet_name="SaldosAcumulados", engine="openpyxl")
    st.session_state.saldos_acumulados = dict(zip(df_saldos_restaurado["IdentProduto"], df_saldos_restaurado["SaldoFisico"]))
    st.success("Saldos restaurados com sucesso!")

uploaded_file = st.file_uploader("Faça upload do arquivo de inventário do sistema (formato .xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Planilha1", engine="openpyxl")

    df["IdentProduto"] = df["IdentProduto"].astype(str)
    df["Descriçao"] = df["Descriçao"].astype(str)
    df["Prateleira"] = df["Prateleira"].astype(str)

    df_sistema = df[["IdentProduto", "Descriçao", "Quantidade", "ClassificABC", "Prateleira"]].copy()

    st.subheader("Filtrar por Prateleira")
    prateleiras = st.multiselect("Selecione uma ou mais prateleiras", df_sistema["Prateleira"].unique())
    if prateleiras:
        df_sistema = df_sistema[df_sistema["Prateleira"].isin(prateleiras)]

    st.subheader("Dados do Sistema")
    st.dataframe(df_sistema)

    st.subheader("Inserir Saldo Físico Acumulativo")
    if "saldos_acumulados" not in st.session_state:
        st.session_state.saldos_acumulados = {produto: 0 for produto in df_sistema["IdentProduto"]}

    df_sistema["opcao"] = df_sistema["IdentProduto"] + " - " + df_sistema["Descriçao"] + " - " + df_sistema["Prateleira"]
    mapa_opcao_para_codigo = dict(zip(df_sistema["opcao"], df_sistema["IdentProduto"]))

    ultima_opcao = st.session_state.get("ultima_opcao_selecionada", df_sistema["opcao"].iloc[0])
    if ultima_opcao not in df_sistema["opcao"].values:
        ultima_opcao = df_sistema["opcao"].iloc[0]

    opcao_selecionada = st.selectbox("Selecione o produto", df_sistema["opcao"], index=df_sistema["opcao"].tolist().index(ultima_opcao))
    st.session_state.ultima_opcao_selecionada = opcao_selecionada

    produto_selecionado = mapa_opcao_para_codigo[opcao_selecionada]
    quantidade_inserida = st.number_input("Quantidade a adicionar ou retirar", min_value=0, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar ao saldo"):
            st.session_state.saldos_acumulados[produto_selecionado] += quantidade_inserida
            st.success(f"Saldo atualizado para {produto_selecionado}: {st.session_state.saldos_acumulados[produto_selecionado]}")
    with col2:
        if st.button("Retirar do saldo"):
            saldo_atual = st.session_state.saldos_acumulados[produto_selecionado]
            if quantidade_inserida > saldo_atual:
                st.warning(f"Não é possível retirar {quantidade_inserida}. Saldo atual é {saldo_atual}.")
            else:
                st.session_state.saldos_acumulados[produto_selecionado] = saldo_atual - quantidade_inserida
                st.success(f"Saldo atualizado para {produto_selecionado}: {st.session_state.saldos_acumulados[produto_selecionado]}" )

    st.subheader("Saldos Físicos Acumulados")
    df_saldos = pd.DataFrame(list(st.session_state.saldos_acumulados.items()), columns=["IdentProduto", "SaldoFisico"])
    df_saldos = df_saldos.merge(df_sistema[["IdentProduto", "Descriçao"]], on="IdentProduto", how="left")
    df_saldos = df_saldos[["IdentProduto", "Descriçao", "SaldoFisico"]]
    st.dataframe(df_saldos)

    output_saldos = BytesIO()
    df_saldos.to_excel(output_saldos, index=False, sheet_name='SaldosAcumulados', engine='openpyxl')
    st.download_button("Baixar Saldos Físicos em Excel", data=output_saldos.getvalue(), file_name="saldos_atualizados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("Gerar Relatório de Divergências"):
        df_relatorio = df_sistema.copy()
        df_relatorio["SaldoFisico"] = df_relatorio["IdentProduto"].map(st.session_state.saldos_acumulados)
        df_relatorio.dropna(subset=["SaldoFisico"], inplace=True)
        df_relatorio["Divergencia"] = df_relatorio["SaldoFisico"] - df_relatorio["Quantidade"]

        wb = Workbook()
        ws = wb.active
        ws.title = "RelatorioDivergencias"

        for r_idx, row in enumerate(dataframe_to_rows(df_relatorio, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                if r_idx > 1:
                    divergencia = df_relatorio.iloc[r_idx - 2]["Divergencia"]
                    if divergencia != 0:
                        cell.fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")
                    else:
                        cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")

        output_relatorio = BytesIO()
        wb.save(output_relatorio)
        output_relatorio.seek(0)

        st.download_button("Baixar Relatório de Divergências Colorido", data=output_relatorio.getvalue(), file_name="relatorio_divergencias_colorido.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
