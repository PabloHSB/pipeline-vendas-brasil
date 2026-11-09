
CREATE TABLE CLIENTE (
    cliente_id VARCHAR(10),
    PRIMARY KEY (cliente_id)
);

CREATE TABLE PRODUTO (
    produto_id VARCHAR(10),
    produto VARCHAR(100),
    categoria VARCHAR(30),
    PRIMARY KEY (produto_id)
);

CREATE TABLE PEDIDO (
    pedido_id VARCHAR(10),
    data_pedido DATE,
    cliente_id VARCHAR(10) NOT NULL,
    uf CHAR(2),
    regiao VARCHAR(30),
    canal_venda VARCHAR(30),
    forma_pagamento VARCHAR(30),
    status_pedido VARCHAR(30),
    prazo_entrega_dias INT NULL,
    PRIMARY KEY (pedido_id),
    FOREIGN KEY (cliente_id) REFERENCES CLIENTE(cliente_id)
);

CREATE TABLE ITEM_PEDIDO (
    pedido_id VARCHAR(10) NOT NULL,
    produto_id VARCHAR(10) NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (pedido_id) REFERENCES PEDIDO(pedido_id),
    FOREIGN KEY (produto_id) REFERENCES PRODUTO(produto_id)
);
