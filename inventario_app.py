import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils.dataframe import dataframe_to_rows

st.title("Sistema de Inventário - Relatório Inventário")

# Upload do inventário do sistema
uploaded_file = st.file_uploader("Faça upload do arquivo de inventário do sistema (formato .xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Planilha1", engine="openpyxl")

    df["IdentProduto"] = df["IdentProduto"].astype(str)
    df["Descriçao"] = df["Descriçao"].astype(str)
    df["Prateleira"] = df["Prateleira"].astype(str)

    df_sistema = df[["IdentProduto", "Descriçao", "Quantidade", "ClassificABC", "Prateleira"]].copy()

    # Inicializar saldos acumulados
    if "saldos_acumulados" not in st.session_state:
        st.session_state.saldos_acumulados = {produto: 0 for produto in df_sistema["IdentProduto"]}

    # Interface para inserir saldo físico
    df_sistema["opcao"] = df_sistema["IdentProduto"] + " - " + df_sistema["Descriçao"] + " - " + df_sistema["Prateleira"]
    mapa_opcao_para_codigo = dict(zip(df_sistema["opcao"], df_sistema["IdentProduto"]))

    opcao_selecionada = st.selectbox("Selecione o produto", df_sistema["opcao"])
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
                st.success(f"Saldo atualizado para {produto_selecionado}: {st.session_state.saldos_acumulados[produto_selecionado]}")

    # Gerar relatório inventário
    df_relatorio = df_sistema.copy()
    df_relatorio["SaldoFisico"] = df_relatorio["IdentProduto"].map(st.session_state.saldos_acumulados)
    df_relatorio["Divergencia"] = df_relatorio["SaldoFisico"] - df_relatorio["Quantidade"]

    st.subheader("Relatório Inventário")
    st.dataframe(df_relatorio)

    # Criar planilha Excel com cor da fonte na coluna Divergencia
    wb = Workbook()
    ws = wb.active
    ws.title = "RelatorioInventario"

    for r_idx, row in enumerate(dataframe_to_rows(df_relatorio, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            if r_idx > 1 and ws.cell(row=1, column=c_idx).value == "Divergencia":
                if value != 0:
                    cell.font = Font(color="FF0000")  # vermelho
                else:
                    cell.font = Font(color="008000")  # verde

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    st.download_button(
        label="Baixar Relatório Inventário em Excel",
        data=output.getvalue(),
        file_name="relatorio_inventario.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
