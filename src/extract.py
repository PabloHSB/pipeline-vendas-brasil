
import pandas as pd
import numpy as np
from pathlib import Path


def executar_extracao():

    # ==========================================
    # 1. CONFIGURAÇÕES E EXTRAÇÃO
    # ==========================================

    pasta_src = Path(__file__).parent
    pasta_raiz = pasta_src.parent
    caminho_arquivo = pasta_raiz / "data" / "vendas_brasil_sinteticas.csv"

    df = pd.read_csv(caminho_arquivo)

    # ==========================================
    # 2. REMOÇÃO DE DUPLICADAS
    # ==========================================

    df_tratado = df.drop_duplicates().copy()

    # ==========================================
    # 3. TRANSFORMAÇÃO
    # ==========================================

    df_tratado['data_pedido'] = pd.to_datetime(
        df_tratado['data_pedido'], errors='coerce'
    )

    # ==========================================
    # 4. CLASSIFICAÇÃO DA QUALIDADE
    # ==========================================

    regra_quantidade_ruim = df_tratado['quantidade'] <= 0
    regra_preco_ruim = df_tratado['preco_unitario'] <= 0
    regra_uf_aus = df_tratado['uf'].isna()

    df_tratado['qualidade_dados'] = np.select(
        [
            regra_quantidade_ruim | regra_preco_ruim,
            regra_uf_aus
        ],
        [
            'Suspeito',
            'OK, com ressalva'
        ],
        default='OK'
    )

    # ==========================================
    # 5. REGISTRO DOS MOTIVOS
    # ==========================================

    df_tratado['motivo_problema'] = ''

    df_tratado.loc[regra_quantidade_ruim, 'motivo_problema'] += 'Quantidade inválida; '
    df_tratado.loc[regra_preco_ruim, 'motivo_problema'] += 'Preço inválido; '
    df_tratado.loc[regra_uf_aus, 'motivo_problema'] += 'UF ausente; '

    df_tratado.loc[
        df_tratado['motivo_problema'] == '',
        'motivo_problema'
    ] = 'Nenhum'

    # ==========================================
    # 6. SEPARAÇÃO DOS DATAFRAMES
    # ==========================================

    df_cliente = df_tratado[['cliente_id']].copy()

    df_produto = df_tratado[
        ['produto_id', 'produto', 'categoria']
    ].copy()

    df_pedido = df_tratado[
        [
            'pedido_id', 'data_pedido', 'cliente_id', 'uf',
            'regiao', 'canal_venda', 'forma_pagamento',
            'status_pedido', 'prazo_entrega_dias'
        ]
    ].copy()

    df_item_pedido = df_tratado[
        ['pedido_id', 'produto_id', 'quantidade', 'preco_unitario']
    ].copy()

    colunas_pedido = [
        'data_pedido', 'cliente_id', 'uf', 'regiao',
        'canal_venda', 'forma_pagamento', 'status_pedido',
        'prazo_entrega_dias'
    ]

    inconsistencias = (
        df_pedido.groupby('pedido_id')[colunas_pedido]
        .nunique(dropna=False)
    )

    inconsistencias = inconsistencias[
        inconsistencias.gt(1).any(axis=1)
    ]

    if not inconsistencias.empty:
        raise ValueError("Existem pedidos com informações divergentes.")

    # Remover duplicadas das dimensões
    df_cliente = df_cliente.drop_duplicates()
    df_produto = df_produto.drop_duplicates()

    # Remover duplicadas de pedidos
    df_pedido = df_pedido.drop_duplicates(subset=['pedido_id'])

    # ==========================================
    # 7. VALIDAÇÃO DOS RELACIONAMENTOS
    # ==========================================

    erros_cliente = df_pedido[
        ~df_pedido['cliente_id'].isin(df_cliente['cliente_id'])
    ]

    erros_produto = df_item_pedido[
        ~df_item_pedido['produto_id'].isin(df_produto['produto_id'])
    ]

    erros_pedido = df_item_pedido[
        ~df_item_pedido['pedido_id'].isin(df_pedido['pedido_id'])
    ]

    if not erros_cliente.empty:
        raise ValueError("Existem pedidos com clientes não cadastrados.")

    if not erros_produto.empty:
        raise ValueError("Existem itens com produtos não cadastrados.")

    if not erros_pedido.empty:
        raise ValueError("Existem itens associados a pedidos inexistentes.")

    # ==========================================
    # 8. RESUMO DA EXTRAÇÃO
    # ==========================================

    print("Extração e transformação concluídas!")
    print("Linhas originais:", len(df))
    print("Linhas tratadas:", len(df_tratado))
    print("Duplicadas removidas:", len(df) - len(df_tratado))
    print("Clientes:", len(df_cliente))
    print("Produtos:", len(df_produto))
    print("Pedidos:", len(df_pedido))
    print("Itens de pedidos:", len(df_item_pedido))

    print("\nClassificação da qualidade:")
    print(df_tratado['qualidade_dados'].value_counts())

    return df_cliente, df_produto, df_pedido, df_item_pedido
