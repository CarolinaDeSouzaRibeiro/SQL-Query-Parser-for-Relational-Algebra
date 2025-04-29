# Documentação do Script `parser.py`

Este documento descreve o propósito e a funcionalidade do script `parser.py`, que é responsável pela análise e validação de consultas SQL.

## Propósito e Funcionalidade

O script `parser.py` permite:

- Analisar consultas SQL fornecidas pelo usuário.
- Validar a sintaxe das consultas SQL.
- Converter consultas SQL para álgebra relacional.

## Principais Funções e Seus Papéis

### `_normalize_name(name)`

Normaliza o nome de uma tabela ou coluna, convertendo-o para minúsculas e removendo espaços em branco.

- **Parâmetros**:
  - `name` (str): Nome a ser normalizado.

- **Retorno**:
  - `str`: Nome normalizado.

### `_validate_and_get_table_alias(table_name, alias, used_aliases, table_to_alias_map)`

Valida o nome da tabela e o alias, garantindo que não haja duplicatas.

- **Parâmetros**:
  - `table_name` (str): Nome da tabela.
  - `alias` (str): Alias da tabela.
  - `used_aliases` (set): Conjunto de aliases já utilizados.
  - `table_to_alias_map` (dict): Mapeamento de tabelas para aliases.

- **Retorno**:
  - `tuple`: Nome normalizado da tabela e alias.

### `_validate_column_name(col_name, involved_aliases_map)`

Valida o nome da coluna, garantindo que ela exista na tabela ou alias especificado.

- **Parâmetros**:
  - `col_name` (str): Nome da coluna.
  - `involved_aliases_map` (dict): Mapeamento de aliases envolvidos.

- **Retorno**:
  - `tuple`: Nome normalizado da tabela, coluna e alias.

### `_rewrite_condition_part(part, involved_aliases_map, table_alias_details)`

Reescreve uma parte da condição para o formato de álgebra relacional.

- **Parâmetros**:
  - `part` (str): Parte da condição.
  - `involved_aliases_map` (dict): Mapeamento de aliases envolvidos.
  - `table_alias_details` (dict): Detalhes dos aliases das tabelas.

- **Retorno**:
  - `str`: Parte da condição reescrita.

### `_process_conditions(condition_str, involved_aliases_map, table_alias_details)`

Processa as condições da cláusula WHERE, dividindo-as em partes individuais.

- **Parâmetros**:
  - `condition_str` (str): String da condição.
  - `involved_aliases_map` (dict): Mapeamento de aliases envolvidos.
  - `table_alias_details` (dict): Detalhes dos aliases das tabelas.

- **Retorno**:
  - `list`: Lista de condições processadas.

### `parse_validate_sql(sql_query)`

Parseia e valida a consulta SQL, retornando uma estrutura de dados com as informações parseadas.

- **Parâmetros**:
  - `sql_query` (str): Consulta SQL a ser parseada e validada.

- **Retorno**:
  - `dict`: Estrutura de dados com as informações parseadas.

### `convert_to_relational_algebra(parsed_data)`

Converte a estrutura de dados parseada para álgebra relacional.

- **Parâmetros**:
  - `parsed_data` (dict): Estrutura de dados parseada.

- **Retorno**:
  - `str`: Expressão de álgebra relacional.

### `process_sql_query(sql_query)`

Processa a consulta SQL, parseando, validando e convertendo para álgebra relacional.

- **Parâmetros**:
  - `sql_query` (str): Consulta SQL a ser processada.

- **Retorno**:
  - `str`: Expressão de álgebra relacional ou erro.

