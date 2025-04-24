-- Ativar o suporte a chaves estrangeiras
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ==========================
-- Tabelas principais
-- ==========================

-- Table: Categoria
CREATE TABLE IF NOT EXISTS Categoria (
    idCategoria INTEGER PRIMARY KEY,
    Descricao TEXT NOT NULL
);

-- Table: Produto
CREATE TABLE IF NOT EXISTS Produto (
    idProduto INTEGER PRIMARY KEY,
    Nome TEXT NOT NULL,
    Descricao TEXT,
    Preco REAL NOT NULL DEFAULT 0,
    QuantEstoque REAL NOT NULL DEFAULT 0,
    Categoria_idCategoria INTEGER NOT NULL,
    FOREIGN KEY (Categoria_idCategoria) REFERENCES Categoria (idCategoria)
);

-- Table: TipoCliente
CREATE TABLE IF NOT EXISTS TipoCliente (
    idTipoCliente INTEGER PRIMARY KEY,
    Descricao TEXT
);

-- Table: Cliente
CREATE TABLE IF NOT EXISTS Cliente (
    idCliente INTEGER PRIMARY KEY,
    Nome TEXT NOT NULL,
    Email TEXT NOT NULL,
    Nascimento TEXT,
    Senha TEXT,
    TipoCliente_idTipoCliente INTEGER NOT NULL,
    DataRegistro TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (TipoCliente_idTipoCliente) REFERENCES TipoCliente (idTipoCliente)
);

-- Table: TipoEndereco
CREATE TABLE IF NOT EXISTS TipoEndereco (
    idTipoEndereco INTEGER PRIMARY KEY,
    Descricao TEXT NOT NULL
);

-- Table: Endereco
CREATE TABLE IF NOT EXISTS Endereco (
    idEndereco INTEGER PRIMARY KEY,
    EnderecoPadrao INTEGER NOT NULL DEFAULT 0,
    Logradouro TEXT,
    Numero TEXT,
    Complemento TEXT,
    Bairro TEXT,
    Cidade TEXT,
    UF TEXT,
    CEP TEXT,
    TipoEndereco_idTipoEndereco INTEGER NOT NULL,
    Cliente_idCliente INTEGER NOT NULL,
    FOREIGN KEY (TipoEndereco_idTipoEndereco) REFERENCES TipoEndereco (idTipoEndereco),
    FOREIGN KEY (Cliente_idCliente) REFERENCES Cliente (idCliente)
);

-- Table: Telefone
CREATE TABLE IF NOT EXISTS Telefone (
    Numero TEXT NOT NULL,
    Cliente_idCliente INTEGER NOT NULL,
    PRIMARY KEY (Numero, Cliente_idCliente),
    FOREIGN KEY (Cliente_idCliente) REFERENCES Cliente (idCliente)
);

-- Table: Status
CREATE TABLE IF NOT EXISTS Status (
    idStatus INTEGER PRIMARY KEY,
    Descricao TEXT NOT NULL
);

-- Table: Pedido
CREATE TABLE IF NOT EXISTS Pedido (
    idPedido INTEGER PRIMARY KEY,
    Status_idStatus INTEGER NOT NULL,
    DataPedido TEXT NOT NULL DEFAULT (datetime('now')),
    ValorTotalPedido REAL NOT NULL DEFAULT 0,
    Cliente_idCliente INTEGER NOT NULL,
    FOREIGN KEY (Status_idStatus) REFERENCES Status (idStatus),
    FOREIGN KEY (Cliente_idCliente) REFERENCES Cliente (idCliente)
);

-- Table: Pedido_has_Produto
CREATE TABLE IF NOT EXISTS Pedido_has_Produto (
    idPedidoProduto INTEGER PRIMARY KEY AUTOINCREMENT,
    Pedido_idPedido INTEGER NOT NULL,
    Produto_idProduto INTEGER NOT NULL,
    Quantidade REAL NOT NULL,
    PrecoUnitario REAL NOT NULL,
    FOREIGN KEY (Pedido_idPedido) REFERENCES Pedido (idPedido),
    FOREIGN KEY (Produto_idProduto) REFERENCES Produto (idProduto)
);

COMMIT;