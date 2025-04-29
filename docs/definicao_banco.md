# Definição do Banco de Dados

Este documento descreve o propósito e a funcionalidade do script `definicao_banco.py`, que é responsável pelo gerenciamento do ciclo de vida do banco de dados para testes com dados sintéticos.

## Propósito e Funcionalidade

O script `definicao_banco.py` permite:

- Criar as tabelas e índices do banco de dados `db_vendas.db`.
- Popular o banco com dados gerados artificialmente, de acordo com uma configuração de volume.
- Excluir registros e índices existentes.
- Verificar se o banco está vazio.
- Executar scripts SQL localizados em subpastas organizadas por tipo (`criacao/`, `exclusao/`, `configuracoes/`).

Esse fluxo automatizado é útil para testes de performance, simulações de carga e desenvolvimento de aplicações com banco de dados SQLite.

## Principais Funções e Seus Papéis

### `executar_script_sql(nome_dir: str, nome_arquivo: str, ver_progresso: bool = True) -> None`

Executa um script SQL localizado em um subdiretório específico.

- **Parâmetros**:
  - `nome_dir` (str): Nome do diretório onde está o script (ex: 'criacao', 'exclusao', 'configuracoes').
  - `nome_arquivo` (str): Nome do arquivo SQL (sem extensão).
  - `ver_progresso` (bool): Se True, exibe barra de progresso simbólica.

- **Exceções**:
  - `FileNotFoundError`: Se o arquivo .sql não for encontrado.

### `criar_tabelas(ver_progresso: bool = True) -> None`

Cria as tabelas do banco de dados executando o script SQL correspondente.

### `criar_indexes(ver_progresso: bool = True) -> None`

Cria os índices do banco de dados executando o script SQL correspondente.

### `excluir_registros(ver_progresso: bool = True) -> None`

Exclui todos os registros das tabelas do banco de dados.

### `excluir_indexes(ver_progresso: bool = True) -> None`

Remove os índices existentes do banco de dados.

### `banco_esta_vazio() -> bool`

Verifica se o banco de dados está vazio, ou seja, se não possui nenhuma tabela.

- **Retorno**:
  - `bool`: True se não houver tabelas no banco, False caso contrário.

### `popular_db(configuracao: int, ver_progresso: bool = True) -> None`

Popula o banco de dados com dados sintéticos com base na configuração escolhida.

- **Etapas**:
  - Verifica se o script SQL correspondente à configuração existe e está preenchido.
  - Gera o script, se necessário, utilizando o módulo `geracao_dados`.
  - Cria as tabelas se o banco estiver vazio, ou limpa os dados e índices se não estiver.
  - Executa o script de inserção de dados com barra de progresso (opcional).
  - Recria os índices após a carga.

- **Parâmetros**:
  - `configuracao` (int): Número da configuração (1 a 4).
  - `ver_progresso` (bool): Se True, exibe barra de progresso durante a geração e execução do script.

- **Exceções**:
  - `ValueError`: Se o número da configuração estiver fora do intervalo permitido.
