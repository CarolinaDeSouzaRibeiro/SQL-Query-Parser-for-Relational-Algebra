# Geração de Dados Sintéticos

Este documento descreve o propósito e a funcionalidade do script `geracao_dados.py`, que é responsável pela geração automatizada de arquivos SQL com dados sintéticos para testes de desempenho.

## Propósito e Funcionalidade

O script `geracao_dados.py` permite:

- Criar dados fictícios realistas em português (Brasil) utilizando a biblioteca Faker.
- Gerar arquivos .sql com comandos INSERT correspondentes a diferentes configurações de volume de dados.
- Salvar os arquivos gerados no diretório `configuracoes/` para popular um banco de dados SQLite em testes de performance, validação de estruturas de dados ou simulações de carga.

## Principais Funções e Seus Papéis

### `sql_str(val: Any) -> str`

Converte valores em representações seguras para uso em instruções SQL.

- **Parâmetros**:
  - `val` (Any): Valor a ser convertido.

- **Retorno**:
  - `str`: Representação segura do valor, com aspas se for string.

### `definir_configuracoes(ver_progresso: bool = True) -> None`

Gera arquivos SQL contendo comandos de inserção de dados para diferentes configurações de volume.

- **Parâmetros**:
  - `ver_progresso` (bool): Se True, exibe barra de progresso durante a geração.

### `range_progress(total: int, desc: str) -> Any`

Função interna que encapsula o uso de barra de progresso opcional.

- **Parâmetros**:
  - `total` (int): Total de iterações.
  - `desc` (str): Descrição da barra de progresso.

- **Retorno**:
  - `Any`: Iterador com ou sem barra de progresso.

### `gerar_dados_tabela(cfg: dict[str, int], ver_progresso: bool) -> list[str]`

Gera dados para cada tabela com base na configuração fornecida.

- **Parâmetros**:
  - `cfg` (dict[str, int]): Configuração de volume de dados.
  - `ver_progresso` (bool): Se True, exibe barra de progresso durante a geração.

- **Retorno**:
  - `list[str]`: Lista de comandos SQL para inserção de dados.

### `salvar_arquivo_sql(nome_cfg: str, conteudos_arquivo: list[str]) -> None`

Salva os comandos SQL gerados em um arquivo .sql.

- **Parâmetros**:
  - `nome_cfg` (str): Nome da configuração.
  - `conteudos_arquivo` (list[str]): Lista de comandos SQL.

### `main() -> None`

Ponto de entrada principal: executa a função `definir_configuracoes` quando o script é chamado diretamente.
