from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert
import os

load_dotenv()


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pipeline_vendas")

# ---------------------------------------------------------------------------
# Conexão e inserção de dados
# ---------------------------------------------------------------------------

def criar_engine():
    if not DB_USER or not DB_PASSWORD:
        raise EnvironmentError("Credenciais não encontradas no arquivo .env.")
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def inserir_dados(engine, df_cliente, df_produto, df_pedido, df_item_pedido):

    tabelas = [
        ("cliente", df_cliente, ["cliente_id"], []),

        ("produto", df_produto, ["produto_id"],
         ["produto", "categoria"]),

        ("pedido", df_pedido, ["pedido_id"],
         ["data_pedido", "cliente_id", "uf", "regiao",
          "canal_venda", "forma_pagamento", "status_pedido",
          "prazo_entrega_dias"]),

        ("item_pedido", df_item_pedido,
         ["pedido_id", "produto_id"],
         ["quantidade", "preco_unitario"])
    ]

    with engine.begin() as conn:

        for nome, df, chaves, colunas_atualizar in tabelas:

            if df.empty:
                continue

            tabela_db = Table(
                nome,
                MetaData(),
                autoload_with=conn
            )

            registros = (
                df.astype(object)
                .where(df.notna(), None)
                .to_dict("records")
            )

            stmt = insert(tabela_db)

            if colunas_atualizar:
                stmt = stmt.on_conflict_do_update(
                    index_elements=chaves,
                    set_={
                        coluna: getattr(stmt.excluded, coluna)
                        for coluna in colunas_atualizar
                    }
                )
            else:
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=chaves
                )

            conn.execute(stmt, registros)

            print(f"Tabela {nome}: {len(registros)} registros processados.")




def testar_conexao(engine):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("Conexão com PostgreSQL realizada com sucesso!")

if __name__ == "__main__":
    engine = criar_engine()
    testar_conexao(engine)