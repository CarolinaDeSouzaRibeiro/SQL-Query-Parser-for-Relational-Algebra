# Resumo do Projeto

Este documento fornece uma visão geral da estrutura e funcionalidade do projeto, explicando cada parte do código e referenciando os documentos relevantes para mais detalhes.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

- `banco_de_dados/`: Contém o banco de dados SQLite e scripts relacionados.
  - `db_vendas.db`: O banco de dados SQLite.
  - `definicao_banco/`: Scripts para definição e manipulação do banco de dados.
    - `configuracoes/`: Scripts SQL para diferentes configurações de volume de dados.
    - `criacao/`: Scripts SQL para criação de tabelas e índices.
    - `exclusao/`: Scripts SQL para exclusão de registros e índices.
    - `geracao_dados.py`: Script para geração de dados sintéticos.
    - `definicao_banco.py`: Script para gerenciamento do ciclo de vida do banco de dados.
- `docs/`: Documentação do projeto.
  - `README.md`: Este documento.
  - `definicao_banco.md`: Documentação do script `definicao_banco.py`.
  - `geracao_dados.md`: Documentação do script `geracao_dados.py`.
  - `main.md`: Documentação do script `main.py`.
  - `parser.md`: Documentação do script `parser.py`.
  - `arvore.md`: Documentação do script `arvore.py`.
  - `desmatamento.md`: Documentação do script `desmatamento.py`.
  - `otimizacao_consultas.md`: Documentação do script `otimizacao_consultas.py`.
  - `processamento_consultas.md`: Documentação do script `processamento_consultas.py`.
- `main.py`: Script principal para processamento de consultas SQL.
- `parser.py`: Script para análise e validação de consultas SQL.
- `plantando_arvores/`: Scripts para manipulação e visualização de árvores de álgebra relacional.
  - `arvore.py`: Script para definição da estrutura de nós da árvore.
  - `desmatamento.py`: Script para reconstrução de álgebra relacional a partir da árvore.
  - `otimizacao_consultas.py`: Script para otimização de consultas SQL.
  - `processamento_consultas.py`: Script para processamento e visualização de árvores de álgebra relacional.

## Explicações Detalhadas

### Banco de Dados

O banco de dados SQLite `db_vendas.db` é utilizado para armazenar dados de vendas. Os scripts na pasta `definicao_banco/` são responsáveis por criar, popular e manipular o banco de dados.

- [Documentação do `definicao_banco.py`](definicao_banco.md)
- [Documentação do `geracao_dados.py`](geracao_dados.md)

### Processamento de Consultas SQL

O script `main.py` é a interface principal para o processamento de consultas SQL. Ele utiliza o script `parser.py` para analisar e validar as consultas, e os scripts na pasta `plantando_arvores/` para manipulação e visualização de árvores de álgebra relacional.

- [Documentação do `main.py`](main.md)
- [Documentação do `parser.py`](parser.md)

### Manipulação e Visualização de Árvores

Os scripts na pasta `plantando_arvores/` são responsáveis por definir a estrutura de nós da árvore, reconstruir a álgebra relacional a partir da árvore, otimizar consultas SQL e visualizar as árvores de álgebra relacional.

- [Documentação do `arvore.py`](arvore.md)
- [Documentação do `desmatamento.py`](desmatamento.md)
- [Documentação do `otimizacao_consultas.py`](otimizacao_consultas.md)
- [Documentação do `processamento_consultas.py`](processamento_consultas.md)
