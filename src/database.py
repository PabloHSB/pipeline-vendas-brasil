from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import text
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
    tabelas = {
        "cliente": df_cliente,
        "produto": df_produto,
        "pedido": df_pedido,
        "item_pedido": df_item_pedido
    }
    with engine.begin() as conn:
        for tabela, df in tabelas.items():
            df.to_sql(tabela, conn, if_exists='append', index=False)



def testar_conexao(engine):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("Conexão com PostgreSQL realizada com sucesso!")

if __name__ == "__main__":
    engine = criar_engine()
    testar_conexao(engine)