BEGIN TRANSACTION;

CREATE INDEX IF NOT EXISTS idx_Produto_Categoria ON Produto (Categoria_idCategoria);
CREATE INDEX IF NOT EXISTS idx_Cliente_TipoCliente ON Cliente (TipoCliente_idTipoCliente);
CREATE INDEX IF NOT EXISTS idx_Endereco_TipoEndereco ON Endereco (TipoEndereco_idTipoEndereco);
CREATE INDEX IF NOT EXISTS idx_Endereco_Cliente ON Endereco (Cliente_idCliente);
CREATE INDEX IF NOT EXISTS idx_Telefone_Cliente ON Telefone (Cliente_idCliente);
CREATE INDEX IF NOT EXISTS idx_Pedido_Status ON Pedido (Status_idStatus);
CREATE INDEX IF NOT EXISTS idx_Pedido_Cliente ON Pedido (Cliente_idCliente);
CREATE INDEX IF NOT EXISTS idx_Pedido_has_Produto_Pedido ON Pedido_has_Produto (Pedido_idPedido);
CREATE INDEX IF NOT EXISTS idx_Pedido_has_Produto_Produto ON Pedido_has_Produto (Produto_idProduto);

COMMIT;