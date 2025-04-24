-- Ativar o suporte a chaves estrangeiras
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Excluir registros das tabelas dependentes primeiro
DELETE FROM Pedido_has_Produto;
DELETE FROM Telefone;
DELETE FROM Endereco;
DELETE FROM Pedido;

-- Em seguida, das tabelas que são referenciadas
DELETE FROM Produto;
DELETE FROM Cliente;

-- Por fim, das tabelas principais
DELETE FROM Categoria;
DELETE FROM TipoCliente;
DELETE FROM TipoEndereco;
DELETE FROM Status;

COMMIT;