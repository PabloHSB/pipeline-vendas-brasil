
from .extract import executar_extracao
from .database import criar_engine, testar_conexao, inserir_dados


def main():
    # 1. Criar conexão com o banco
    engine = criar_engine()

    try:    
        # 2. Extrair e transformar os dados
        df_cliente, df_produto, df_pedido, df_item_pedido = executar_extracao()

        # 3. Testar conexão
        testar_conexao(engine)

        # 4. Inserir dados no PostgreSQL
        inserir_dados(
        engine,
        df_cliente,
        df_produto,
        df_pedido,
        df_item_pedido
    )

        print("\nPipeline executado com sucesso!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
