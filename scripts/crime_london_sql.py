from google.cloud import bigquery
from pathlib import Path
import pandas as pd

# ============================================================
# 1. CONFIGURAÇÕES DO PROJETO
# ============================================================

PROJECT_ID = "crimelondon-508704"
DATASET_ID = "Crime_London_amostra"
TABLE_ID = "crime_lsoa_amostra2016"

TABLE_FULL_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Caminho principal do projeto
PROJECT_PATH = Path(r"D:\Documents\Workspace\crime_london_Pratique38")

# Diretórios para armazenamento dos dados
RAW_PATH = PROJECT_PATH / "data" / "raw"
READY_PATH = PROJECT_PATH / "data" / "ready"

# Arquivo de saída
RAW_OUTPUT_PATH = RAW_PATH / "crime_london_raw.csv"
READY_OUTPUT_PATH = READY_PATH / "crime_london_ready.csv"


# ============================================================
# 2. CONEXÃO COM O BIGQUERY
# ============================================================

print("\n>>> Conectando ao BigQuery")

client = bigquery.Client(project=PROJECT_ID)

print("Conexão realizada com sucesso!")
print(f"Projeto: {PROJECT_ID}")
print(f"Tabela: {TABLE_FULL_ID}")


# ============================================================
# 3. EXTRAÇÃO DOS DADOS
# ============================================================

print("\n>>> Extraindo dados do BigQuery (RAW)")

query = f"""
SELECT *
FROM `{TABLE_FULL_ID}`
"""

df = client.query(query).to_dataframe()

print(f"Total de registros extraídos: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")


# ============================================================
# 4. SALVAMENTO DOS DADOS BRUTOS
# ============================================================

print("\n>>> Salvando dataset RAW")

RAW_PATH.mkdir(parents=True, exist_ok=True)

df.to_csv(
    RAW_OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print(f"Arquivo RAW salvo com sucesso:")
print(RAW_OUTPUT_PATH)


# ============================================================
# 5. PADRONIZAÇÃO DOS NOMES DAS COLUNAS
# ============================================================

print("\n>>> Padronizando nomes das colunas")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("Nomes das colunas padronizados.")


# ============================================================
# 6. REMOÇÃO DE COLUNAS TOTALMENTE VAZIAS
# ============================================================

print("\n>>> Removendo colunas totalmente vazias")

colunas_antes = set(df.columns)

df = df.dropna(axis=1, how="all")

colunas_depois = set(df.columns)

colunas_removidas = colunas_antes - colunas_depois

print(f"Total de colunas removidas: {len(colunas_removidas)}")

if colunas_removidas:
    print("Colunas excluídas:")
    for coluna in sorted(colunas_removidas):
        print(f"- {coluna}")
else:
    print("Nenhuma coluna totalmente vazia encontrada.")


# ============================================================
# 7. VALIDAÇÃO DE VALORES NULOS
# ============================================================

print("\n>>> Verificando valores nulos")

nulos = df.isnull().sum()

nulos = nulos[nulos > 0]

if nulos.empty:
    print("Nenhum valor nulo encontrado.")
else:
    print("Valores nulos encontrados:")
    print(nulos)


# ============================================================
# 8. TRATAMENTO DA COLUNA VALUE
# ============================================================

if "value" in df.columns:

    print("\n>>> Limpando coluna 'value'")

    # Guarda o valor original para rastreabilidade
    df["value_original"] = df["value"]

    # Converte para numérico
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Verifica valores negativos
    negativos = (df["value"] < 0).sum()

    print(f"Valores negativos encontrados: {negativos}")

else:

    print("\n>>> Coluna 'value' não encontrada.")


# ============================================================
# 9. AJUSTE DOS TIPOS DE DADOS
# ============================================================

print("\n>>> Ajustando tipos de dados")

if "year" in df.columns:
    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    ).astype("Int64")

if "month" in df.columns:
    df["month"] = pd.to_numeric(
        df["month"],
        errors="coerce"
    ).astype("Int64")

if "value" in df.columns:
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )


# ============================================================
# 10. VALIDAÇÃO DO MÊS
# ============================================================

if "month" in df.columns:

    print("\n>>> Validando valores do mês")

    meses_invalidos = df[
        (df["month"] < 1) |
        (df["month"] > 12)
    ]

    print(
        f"Meses inválidos encontrados: "
        f"{len(meses_invalidos)}"
    )


# ============================================================
# 11. VALIDAÇÃO DO ANO
# ============================================================

if "year" in df.columns:

    print("\n>>> Validando período")

    print(
        f"Ano inicial: {df['year'].min()}"
    )

    print(
        f"Ano final: {df['year'].max()}"
    )


# ============================================================
# 12. VALIDAÇÃO DE DUPLICIDADES
# ============================================================

print("\n>>> Verificando registros duplicados")

duplicados = df.duplicated().sum()

print(f"Registros duplicados encontrados: {duplicados}")


# ============================================================
# 13. SALVAMENTO DO DATASET TRATADO
# ============================================================

print("\n>>> Salvando dataset tratado")

READY_PATH.mkdir(parents=True, exist_ok=True)

df.to_csv(
    READY_OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("Arquivo tratado salvo com sucesso:")
print(READY_OUTPUT_PATH)

print(f"Linhas finais: {len(df)}")
print(f"Colunas finais: {len(df.columns)}")


# ============================================================
# 14. FINALIZAÇÃO
# ============================================================

print("\n>>> Pipeline concluído")

print("- Conexão com BigQuery realizada")
print("- Dataset extraído")
print("- Validações executadas")
print("- Dados tratados e padronizados")
print("- Dataset RAW salvo")
print("- Dataset READY salvo")
print("- Pronto para análise no Power BI")