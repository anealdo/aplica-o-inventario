# Sistema de Inventário Web com Streamlit

Esta aplicação permite comparar os saldos de estoque registrados no sistema com os saldos físicos contados manualmente. Desenvolvida com [Streamlit](https://streamlit.io), pode ser executada localmente ou hospedada na nuvem.

## Funcionalidades

- Upload de arquivo Excel com dados do sistema
- Visualização dos produtos e seus saldos registrados
- Entrada manual do saldo físico por produto
- Comparação automática entre os saldos
- Relatório de divergências com as colunas:
  - `IdentProduto`
  - `Descriçao` (ao lado de IdentProduto)
  - `Quantidade` (saldo do sistema)
  - `SaldoFisico` (contagem física)
  - `Divergencia` (diferença entre os saldos)
  - `ClassificABC` (classificação ABC do produto)
- Exibição de gráfico de acuracidade geral diretamente na interface web
- Exportação do relatório de divergências em formato Excel

## Funcionalidades Adicionadas

- Seleção de produto com exibição de código e descrição (ex: `A001 - Produto A`)
- Inserção acumulativa de saldo físico por produto
- Exibição dos saldos físicos acumulados em formato de tabela com descrição
- Geração de relatório de divergências e gráfico de acuracidade com base nos saldos acumulados

## Requisitos

- Python 3.8+
- Pacotes:
  - streamlit
  - pandas
  - openpyxl
  - plotly

## Instalação

```bash
pip install streamlit pandas openpyxl plotly
```

## Como executar

```bash
streamlit run inventario_app.py
```

Acesse a aplicação no navegador em `http://localhost:8501`

## Estrutura esperada do arquivo Excel

A planilha deve conter pelo menos as seguintes colunas:

- `IdentProduto`
- `Quantidade`
- `Descriçao`
- `ClassificABC`

## Hospedagem na Web

Você pode hospedar esta aplicação gratuitamente usando:

- [Streamlit Cloud](https://streamlit.io/cloud)
- [Replit](https://replit.com)
- [Hugging Face Spaces](https://huggingface.co/spaces)

## Licença

Este projeto é livre para uso e modificação.

  
