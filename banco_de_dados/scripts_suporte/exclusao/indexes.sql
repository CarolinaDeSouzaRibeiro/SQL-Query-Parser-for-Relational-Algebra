BEGIN TRANSACTION;

DROP INDEX IF EXISTS idx_Produto_Categoria;
DROP INDEX IF EXISTS idx_Cliente_TipoCliente;
DROP INDEX IF EXISTS idx_Endereco_TipoEndereco;
DROP INDEX IF EXISTS idx_Endereco_Cliente;
DROP INDEX IF EXISTS idx_Telefone_Cliente;
DROP INDEX IF EXISTS idx_Pedido_Status;
DROP INDEX IF EXISTS idx_Pedido_Cliente;
DROP INDEX IF EXISTS idx_Pedido_has_Produto_Pedido;
DROP INDEX IF EXISTS idx_Pedido_has_Produto_Produto;

COMMIT;