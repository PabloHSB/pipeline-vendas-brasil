# ==========================================
# 1. IMPORTAÇÕES E CONFIGURAÇÕES
# ==========================================

import pandas as pd
import numpy as np
from pathlib import Path

pasta_src = Path(__file__).parent

pasta_raiz = pasta_src.parent

caminho_arquivo = pasta_raiz / "data" / "vendas_brasil_sinteticas.csv"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

# ==========================================
# 2. EXTRAÇÃO DOS DADOS
# ==========================================

df = pd.read_csv(caminho_arquivo)

df_tratado = df.drop_duplicates().copy()

# ==========================================
# 3. INVESTIGAÇÃO DA QUALIDADE
# ==========================================

linhas_com_ausentes = df[df['uf'].isna()]

pedidos_cancelados = ['Cancelado']
pedidos = len(df[df['status_pedido'].isin(pedidos_cancelados) & df['prazo_entrega_dias'].notna()])

#Ivestigando prazo de entrega ausentes com pedidos 
df_desejado = ['pedido_id', 'regiao', 'cliente_id', 'uf', 'prazo_entrega_dias']
df_reduzido = df.loc[df['uf'].isna(), df_desejado]

clientes_s = ['C0027', 'C0094', 'C0163', 'C0191', 'C0229', 'C0245', 'C0361', 'C0400']
df_clientes_s = df[df['cliente_id'].isin(clientes_s)]
pedidos_por_cliente = df_clientes_s.groupby('cliente_id')
print(pedidos_por_cliente)


# Quantidade de linhas duplicadas no DF 7 linhas
# iremos fazer a remoção das duplicadas pois o pedido não sofreu alteração nos dados
linhas_dupli = df[df.duplicated(keep=False)]
linhas_dupli_j = len(linhas_dupli.sort_values(by='pedido_id'))
print(linhas_dupli_j)


#Investigando quantidade negativa
df_ins_q = ['pedido_id', 'regiao', 'cliente_id', 'produto', 'quantidade', 'status_pedido', 'canal_venda']
valores_N = df_tratado[df_tratado['quantidade'] <= 0 ][df_ins_q]
print(valores_N)
print('---------------------------------------------------')

#Investigando preço negativo
df_ins_preco = ['pedido_id', 'regiao', 'cliente_id', 'produto_id', 'quantidade', 'preco_unitario', 'status_pedido', 'canal_venda']
preco_negativo = df_tratado[df_tratado['preco_unitario'] <= 0][df_ins_preco]
print(preco_negativo)
print('---------------------------------------------------')

# #Verificando se os produtos com preço negativo são os mesmos que os produtos com preço positivo
inv_p = ['P008', 'P011', 'P006', 'P011', 'P005']
filtro = df_tratado['produto_id'].isin(inv_p) & (df_tratado['preco_unitario'] > 0)
preco_positivo = df_tratado[filtro]
preco_positivo_unicos = preco_positivo.drop_duplicates(subset=['produto_id'])
print(preco_positivo_unicos.head(5))
print('---------------------------------------------------')

# #Investigando data dos pedidos negativos
df_tratado['data_pedido'] = pd.to_datetime(df_tratado['data_pedido'])
df_ins_data = ['pedido_id', 'regiao', 'cliente_id', 'produto', 'status_pedido', 'canal_venda', 'data_pedido']
data_negativa = df_tratado['data_pedido'] < '2025-01-01'
print(df_tratado[data_negativa][df_ins_data])
print('---------------------------------------------------')

##Investigando prazo de entrega negativo
df_ins_entrega = ['pedido_id', 'regiao', 'cliente_id', 'produto', 'status_pedido', 'canal_venda', 'prazo_entrega_dias']
entrega_negativa = df_tratado['prazo_entrega_dias'] < 0
print(df_tratado[entrega_negativa][df_ins_entrega])
print('---------------------------------------------------')

print('Investigando valores unicos em pedido')
df_unicos = df_tratado['pedido_id'].nunique()
print('Quantidade de pedidos únicos:', df_unicos)


# ==========================================
# 4. TRANSFORMAÇÃO INICIAL
# ==========================================
# Converter datas
df_tratado['data_pedido'] = pd.to_datetime(df_tratado['data_pedido'],errors='coerce')

# ==========================================
# 5. CLASSIFICAÇÃO DA QUALIDADE
# ==========================================

# 1. Define as regras em linhas separadas
regra_quantidade_ruim = df_tratado['quantidade'] <= 0
regra_preco_ruim = df_tratado['preco_unitario'] <= 0
regra_uf_aus = df_tratado['uf'].isna()

# 2. Junta tudo no np.where de forma limpa
df_tratado['qualidade_dados'] = np.select([regra_quantidade_ruim | regra_preco_ruim,regra_uf_aus],['Suspeito','OK, com ressalva'],default='OK')

# ==========================================
# 6. REGISTRO DOS MOTIVOS
# ==========================================
df_tratado['motivo_problema'] = ''

df_tratado.loc[regra_quantidade_ruim, 'motivo_problema'] += 'Quantidade inválida; '

df_tratado.loc[regra_preco_ruim, 'motivo_problema'] += 'Preço inválido; '

df_tratado.loc[regra_uf_aus, 'motivo_problema'] += 'UF ausente; '

df_tratado.loc[
    df_tratado['motivo_problema'] == '',
    'motivo_problema'
] = 'Nenhum'

#==========================================
# SEPARANDO OS DATAFRAMES
# ==========================================
df_cliente = df_tratado[['cliente_id']].copy()

df_produto = df_tratado[['produto_id', 'produto', 'categoria']].copy()

df_pedido = df_tratado[['pedido_id', 'data_pedido', 'cliente_id', 'uf', 'regiao', 'canal_venda', 'forma_pagamento', 'status_pedido', 'prazo_entrega_dias']].copy()
df_pedido['prazo_entrega_dias'] = df_pedido['prazo_entrega_dias'].astype('Int64')

df_item_pedido = df_tratado[['pedido_id', 'produto_id', 'quantidade', 'preco_unitario']].copy()

df_cliente = df_cliente.drop_duplicates()
df_produto = df_produto.drop_duplicates()


# ==========================================
# REMOVENDO AS DUPLICADAS
# ==========================================
# Verificando se um mesmo pedido possui informações diferentes
colunas_pedido = [
    'data_pedido', 'cliente_id', 'uf', 'regiao',
    'canal_venda', 'forma_pagamento',
    'status_pedido', 'prazo_entrega_dias'
]

inconsistencias_pedido = (
    df_pedido.groupby('pedido_id')[colunas_pedido]
    .nunique(dropna=False)
)

print(inconsistencias_pedido[
    inconsistencias_pedido.gt(1).any(axis=1)
])

print("--- EXEMPLO DE UM REGISTRO ÚNICO POR PEDIDO ---")
df_por_pedido = df_pedido.drop_duplicates(subset=['pedido_id'], keep='first')
print(df_por_pedido[['pedido_id', 'data_pedido', 'cliente_id', 'uf', 'regiao', 'canal_venda', 'forma_pagamento', 'status_pedido', 'prazo_entrega_dias']].head())

print('---------------------------------------------------')
print('Investigando erros em cliente')
df_unicos_cliente = df_cliente['cliente_id'].unique()
erros_cliente = df_por_pedido[~df_por_pedido['cliente_id'].isin(df_unicos_cliente)]

if len(erros_cliente) == 0:
    print('Não há erros de cliente')
else:
    print('Há erros de cliente')
    print(erros_cliente)
print('---------------------------------------------------')

print('Investigando erros em produto')
df_unicos_produto = df_produto['produto_id'].unique()
erros_produto = df_item_pedido[~df_item_pedido['produto_id'].isin(df_unicos_produto)]

if len(erros_produto) == 0:
    print('Não há erros de produto')
else:
    print('Há erros de produto')
    print(erros_produto)

print('Investigando erros em pedido')
df_unicos_pedido = df_pedido['pedido_id'].unique()
erros_pedido = df_item_pedido[~df_item_pedido['pedido_id'].isin(df_unicos_pedido)]

if erros_pedido.empty:
    print('Não há erros de pedido')
else:
    print('Há erros de pedido')
    print(erros_pedido)

# ==========================================
# VALIDAÇÂO
# ==========================================
print('Linhas Originais:', len(df))
print('Linhas Tratadas:', len(df_tratado))
print('Duplicadas removidas:', len(df) - len(df_tratado))
print('---------------------------------------------------')
print('\nClassificação:')
print(df_tratado['qualidade_dados'].value_counts())
print('---------------------------------------------------')
print('\nMotivos:')
print(df_tratado['motivo_problema'].value_counts())

print('---------------------------------------------------')
print(df_tratado[['pedido_id', 'cliente_id', 'produto_id']].dtypes)
print('---------------------------------------------------')
print(df_tratado[['pedido_id', 'cliente_id', 'produto_id']].head())
print('---------------------------------------------------')
print('Quantidade de clientes:', len(df_cliente))
print('Quantidade de produtos:', len(df_produto))
print('Quantidade de pedidos:', len(df_pedido))
print('Quantidade de itens de pedidos:', len(df_item_pedido))   
print('---------------------------------------------------')
print('Tipo de dados do dataframe df_cliente:')
print(df_cliente.dtypes)   
print('Tipo de dados do dataframe df_produto:')
print(df_produto.dtypes)   
print('Tipo de dados do dataframe df_pedido:')
print(df_pedido.dtypes)   
print('Tipo de dados do dataframe df_item_pedido:')
print(df_item_pedido.dtypes)   


