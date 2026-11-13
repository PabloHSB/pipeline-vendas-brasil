# Pipeline de Vendas Brasil

## Sobre o projeto

Projeto de Engenharia de Dados desenvolvido com Python, Pandas e PostgreSQL, simulando o processamento de vendas de uma empresa brasileira fictícia.

O objetivo é desenvolver um pipeline ETL, aplicando técnicas de limpeza, transformação, validação e carga incremental de dados.

## Tecnologias

- Python e Pandas
- SQL e PostgreSQL
- SQLAlchemy
- Git e GitHub
- DBeaver
- diagrams.net

## Arquitetura

CSV → Python/Pandas → PostgreSQL

O projeto foi dividido em três módulos:

- `extract.py`: extração, limpeza e transformação dos dados.
- `database.py`: conexão e carga no PostgreSQL.
- `main.py`: execução do pipeline.

## Resultados

- 1.007 registros originais.
- 1.000 registros após o tratamento.
- 7 duplicatas removidas.
- 384 clientes.
- 12 produtos.
- 1.000 pedidos.
- 1.000 itens de pedidos.

A carga utiliza UPSERT para inserir novos registros e atualizar registros existentes, evitando duplicações.

## Como executar

1. Instale as dependências:

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

2. Configure as credenciais do PostgreSQL no arquivo `.env`.

3. Execute o script `Criação_Tabelas.sql` no banco de dados.

4. Execute o pipeline:

```bash
python -m src.main
```

## Status

**ETL implementado e validado.**
