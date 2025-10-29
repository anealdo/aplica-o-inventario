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
        st.session_state.saldos_acumulados = {produto: 0 for produto in df_sistema["IdentProduto"]}

    df_sistema["opcao"] = (
        df_sistema["IdentProduto"] + " - " +
        df_sistema["Descriçao"] + " - " +
        df_sistema["Prateleira"]
    )

    mapa_opcao_para_codigo = dict(zip(df_sistema["opcao"], df_sistema["IdentProduto"]))

    # Seleção de produto com memória da última escolha
    ultima_opcao = st.session_state.get("ultima_opcao_selecionada", df_sistema["opcao"].iloc[0])
    if ultima_opcao not in df_sistema["opcao"].values:
        ultima_opcao = df_sistema["opcao"].iloc[0]

    opcao_selecionada = st.selectbox(
        "Selecione o produto",
        df_sistema["opcao"],
        index=df_sistema["opcao"].tolist().index(ultima_opcao)
    )
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
                st.success(f"Saldo atualizado para {produto_selecionado}: {st.session_state.saldos_acumulados[produto_selecionado]}")

    st.subheader("Saldos Físicos Acumulados")
    df_saldos = pd.DataFrame(list(st.session_state.saldos_acumulados.items()), columns=["IdentProduto", "SaldoFisico"])
    df_saldos = df_saldos.merge(df_sistema[["IdentProduto", "Descriçao"]], on="IdentProduto", how="left")
    df_saldos = df_saldos[["IdentProduto", "Descriçao", "SaldoFisico"]]
    st.dataframe(df_saldos)

    # Botão para baixar os saldos físicos atuais
    output_saldos = BytesIO()
    df_saldos.to_excel(output_saldos, index=False, sheet_name='SaldosAcumulados', engine='openpyxl')
    st.download_button(
        label="Baixar Saldos Físicos em Excel",
        data=output_saldos.getvalue(),
        file_name="saldos_atualizados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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

        output_relatorio = BytesIO()
        with pd.ExcelWriter(output_relatorio, engine='openpyxl') as writer:
            df_divergente.to_excel(writer, index=False, sheet_name='Divergencias')
        st.download_button(
            label="Baixar Relatório de Divergências em Excel",
            data=output_relatorio.getvalue(),
            file_name="relatorio_divergencias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

