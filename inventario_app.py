import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO

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

    st.subheader("Dados do Sistema")
    st.dataframe(df_sistema)

    st.subheader("Inserir Saldo Físico Acumulativo")

    if "saldos_acumulados" not in st.session_state:
        st.session_state.saldos_acumulados = {produto: 0 for produto in df_sistema["IdentProduto"]}

    df_sistema["opcao"] = (
        df_sistema["IdentProduto"] + " - " +
        df_sistema["Descriçao"] + " - " +
        df_sistema["Prateleira"]
    )

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
            st.session_state.saldos_acumulados[produto_selecionado] -= quantidade_inserida
            st.success(f"Saldo atualizado para {produto_selecionado}: {st.session_state.saldos_acumulados[produto_selecionado]}")

    st.subheader("Saldos Físicos Acumulados")
    df_saldos = pd.DataFrame(list(st.session_state.saldos_acumulados.items()), columns=["IdentProduto", "SaldoFisico"])
    df_saldos = df_saldos.merge(df_sistema[["IdentProduto", "Descriçao"]], on="IdentProduto", how="left")
    df_saldos = df_saldos[["IdentProduto", "Descriçao", "SaldoFisico"]]
    st.dataframe(df_saldos)

    if st.button("Gerar Relatório"):
        df_sistema["SaldoFisico"] = df_sistema["IdentProduto"].map(st.session_state.saldos_acumulados)
        df_sistema.dropna(subset=["SaldoFisico"], inplace=True)
        df_sistema["Divergencia"] = df_sistema["SaldoFisico"] - df_sistema["Quantidade"]

        df_divergente = df_sistema[df_sistema["Divergencia"] != 0][[
            "IdentProduto", "Descriçao", "Quantidade", "SaldoFisico", "Divergencia", "ClassificABC"
        ]]

        st.subheader("Relatório de Divergências")
        st.dataframe(df_divergente)

        df_sistema["Acuracidade"] = df_sistema.apply(
            lambda row: 100 if row["Quantidade"] == row["SaldoFisico"]
            else round(100 * min(row["Quantidade"], row["SaldoFisico"]) / max(row["Quantidade"], row["SaldoFisico"]), 2),
            axis=1
        )
        acuracidade_geral = round(df_sistema["Acuracidade"].mean(), 2)

        fig = px.pie(
            names=["Acurado", "Divergente"],
            values=[acuracidade_geral, 100 - acuracidade_geral],
            title="Acuracidade Geral do Estoque",
            hole=0.4
        )
        st.subheader("Acuracidade Geral do Estoque")
        st.plotly_chart(fig, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_divergente.to_excel(writer, index=False, sheet_name='Divergencias')
        st.download_button(
            label="Baixar Relatório de Divergências em Excel",
            data=output.getvalue(),
            file_name="relatorio_divergencias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


