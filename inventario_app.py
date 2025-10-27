import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

st.title("Sistema de Inventário - Acuracidade e Divergências")

uploaded_file = st.file_uploader("Faça upload do arquivo de inventário do sistema (formato .xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Planilha1", engine="openpyxl")
    df_sistema = df[["IdentProduto", "Descriçao", "Quantidade", "ClassificABC"]].copy()

    st.subheader("Dados do Sistema")
    st.dataframe(df_sistema)

    st.subheader("Inserir Saldo Físico")
    saldo_fisico = {}
    for produto in df_sistema["IdentProduto"].unique():
        saldo = st.number_input(f"Saldo físico para {produto}", min_value=0, step=1, key=produto)
        saldo_fisico[produto] = saldo

    if st.button("Gerar Relatório"):
        df_sistema["SaldoFisico"] = df_sistema["IdentProduto"].map(saldo_fisico)
        df_sistema.dropna(subset=["SaldoFisico"], inplace=True)
        df_sistema["Divergencia"] = df_sistema["SaldoFisico"] - df_sistema["Quantidade"]

        df_divergente = df_sistema[df_sistema["Divergencia"] != 0][[
            "IdentProduto", "Descriçao", "Quantidade", "SaldoFisico", "Divergencia", "ClassificABC"
        ]]

        st.subheader("Relatório de Divergências")
        st.dataframe(df_divergente)

        df_sistema["Acuracidade"] = df_sistema.apply(
            lambda row: 100 if row["Quantidade"] == row["SaldoFisico"] else round(100 * min(row["Quantidade"], row["SaldoFisico"]) / max(row["Quantidade"], row["SaldoFisico"]), 2),
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

        fig.write_image("grafico_acuracidade_temp.png")

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_divergente.to_excel(writer, index=False, sheet_name='Divergencias')

        output.seek(0)
        wb = load_workbook(output)
        ws = wb["Divergencias"]
        img = Image("grafico_acuracidade_temp.png")
        ws.add_image(img, "A10")

        final_output = BytesIO()
        wb.save(final_output)

        st.download_button(
            label="Baixar Relatório de Divergências em Excel",
            data=final_output.getvalue(),
            file_name="relatorio_divergencias_com_grafico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
