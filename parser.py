"""
Módulo responsável pelo parsing, validação e conversão de comandos SQL restritos para álgebra relacional.
Implementa as regras do projeto de processador de consultas, incluindo validação de nomes, operadores e estrutura das consultas.
"""
#parse SQL based instructions
#i. Select, From, Where, INNER JOIN;
#ii. Operators =, >, <, <=, >=, <>, And, ( , ) ;

#all commands must begin with SELECT
#elements must be separated by commas

#FROM -> must be followed by an existing table name
#WHERE -> must be followed by a valid condition
#INNER JOIN -> must be followed by an existing table name

#operators:
# = has to be between two elements, either a column name or a value
# =, >, <, <=, >=, <>, do the same
#AND -> must be between two valid conditions
#( -> must be followed by a valid operation, column name or condition
#) -> must be preceded by a valid condition and close a parenthesis

#

# -*- coding: utf-8 -*-
import re
import io # Para silenciar prints durante testes
import sys # Para silenciar prints durante testes

# --- Definição do Esquema do Banco de Dados (Minúsculas para validação interna, Lista/Tupla para preservar case) ---
DATABASE_SCHEMA = {
    'categoria': ['idCategoria', 'Descricao'],
    'produto': ['idProduto', 'Nome', 'Descricao', 'Preco', 'QuantEstoque', 'Categoria_idCategoria'],
    'tipocliente': ['idTipoCliente', 'Descricao'],
    'cliente': ['idCliente', 'Nome', 'Email', 'Nascimento', 'Senha', 'TipoCliente_idTipoCliente', 'DataRegistro'],
    'tipoendereco': ['idTipoEndereco', 'Descricao'],
    'endereco': ['idEndereco', 'EnderecoPadrao', 'Logradouro', 'Numero', 'Complemento', 'Bairro', 'Cidade', 'UF', 'CEP', 'TipoEndereco_idTipoEndereco', 'Cliente_idCliente'],
    'telefone': ['Numero', 'Cliente_idCliente'],
    'status': ['idStatus', 'Descricao'],
    'pedido': ['idPedido', 'Status_idStatus', 'DataPedido', 'ValorTotalPedido', 'Cliente_idCliente'],
    'pedido_has_produto': ['idPedidoProduto', 'Pedido_idPedido', 'Produto_idProduto', 'Quantidade', 'PrecoUnitario']
}

# --- Operadores Permitidos ---
ALLOWED_OPERATORS = {'=', '>', '<', '<=', '>=', '<>'}
ALLOWED_CONNECTORS = {'AND'}

# --- Funções Auxiliares ---
def _normalize_name(name):
    """
    Normaliza um nome (tabela, coluna ou alias) para minúsculas e sem espaços.
    """
    if not isinstance(name, str): return ""
    return name.lower().strip()

# --- Funções de Validação e Reescrita ---
def _validate_and_get_table_alias(table_name, alias, used_aliases, table_to_alias_map):
    """
    Valida o nome da tabela e do alias, garantindo unicidade e existência no esquema.
    """
    norm_name = _normalize_name(table_name)
    if norm_name not in DATABASE_SCHEMA: raise ValueError(f"Erro de validação: Tabela '{table_name}' não encontrada no esquema.")
    alias_to_use = _normalize_name(alias) if alias else norm_name
    if alias_to_use in used_aliases: raise ValueError(f"Erro de validação: Alias ou nome de tabela '{alias_to_use}' (normalizado de '{alias or table_name}') usado mais de uma vez.")
    used_aliases.add(alias_to_use)
    table_to_alias_map[norm_name] = {'alias': alias_to_use} # Simplificado: só guarda alias
    return norm_name, alias_to_use

def _validate_column_name(col_name, involved_aliases_map):
    """
    Valida o nome da coluna, considerando alias e ambiguidades, conforme as tabelas envolvidas.
    """
    col_name = col_name.strip()
    norm_col_name_full = _normalize_name(col_name)
    possible_matches = []
    if '.' in norm_col_name_full:
        alias_part, col_part = norm_col_name_full.split('.', 1)
        if alias_part not in involved_aliases_map:
            aliases_involved_str = ', '.join(involved_aliases_map.keys())
            raise ValueError(f"Alias ou Tabela '{alias_part}' referenciado na coluna '{col_name}' não está entre os aliases/tabelas envolvidos: {aliases_involved_str}.")
        table_norm = involved_aliases_map[alias_part]
        normalized_schema_cols = [_normalize_name(c) for c in DATABASE_SCHEMA[table_norm]]
        if col_part not in normalized_schema_cols:
            schema_cols_str = ", ".join(DATABASE_SCHEMA.get(table_norm, ['???']))
            raise ValueError(f"Coluna '{col_part}' não encontrada na tabela '{table_norm}' (alias '{alias_part}'). Colunas disponíveis: [{schema_cols_str}]")
        return table_norm, col_part, alias_part
    else:
        col_part = norm_col_name_full
        for alias_norm, table_norm in involved_aliases_map.items():
            normalized_schema_cols = [_normalize_name(c) for c in DATABASE_SCHEMA[table_norm]]
            if col_part in normalized_schema_cols: possible_matches.append((table_norm, col_part, alias_norm))
        if not possible_matches:
            aliases_involved_str = ', '.join(involved_aliases_map.keys())
            raise ValueError(f"Coluna '{col_name}' não encontrada em nenhuma das tabelas/aliases envolvidos: {aliases_involved_str}.")
        if len(possible_matches) > 1:
            aliases_found_str = ', '.join([m[2] for m in possible_matches])
            raise ValueError(f"Coluna '{col_name}' é ambígua. Ela existe nos aliases/tabelas: {aliases_found_str}. Use qualificação (Alias.Coluna).")
        return possible_matches[0]

def _rewrite_condition_part(part, involved_aliases_map, table_alias_details):
    """
    Reescreve uma parte de condição para o formato da álgebra relacional, validando colunas e operadores.
    """
    part = part.strip()
    if not part: return ""

    # Tenta Coluna OP Valor (Número ou String) - Regex mais explícita
    match_col_op_val = re.match(r"""
        \s*([\w\.]+)              # Grupo 1: Coluna (com ou sem alias)
        \s*(=|>|<|<=|>=|<>)      # Grupo 2: Operador
        \s*(                     # Grupo 3: Valor (Número ou String)
            (?:                  #   Inicio: Grupo não capturante para OU
                [+-]?\d+\.?\d* |  #     Opção 1: Número (int/float, opcionalmente assinado)
                [+-]?\.\d+    |  #     Opção 1b: Número começando com . (ex: .5)
                '.*?'         |  #     Opção 2: String com aspas simples
                \".*?\"          #     Opção 3: String com aspas duplas
            )                    #   Fim: Grupo não capturante para OU
        )\s*$                    # Fim do Valor e da string
    """, part, re.IGNORECASE | re.VERBOSE)

    # Tenta Coluna OP Coluna
    match_col_op_col = re.match(r"""
        \s*([\w\.]+)              # Grupo 1: Coluna 1
        \s*(=|>|<|<=|>=|<>)      # Grupo 2: Operador
        \s*([\w\.]+)              # Grupo 3: Coluna 2
        \s*$
    """, part, re.IGNORECASE | re.VERBOSE)

    match = None
    is_col_op_col = False

    if match_col_op_val:
        match = match_col_op_val
    elif match_col_op_col:
        match = match_col_op_col
        is_col_op_col = True
    else:
        # Tentativa final com regex genérica (pode pegar casos não previstos acima)
        # Ou tratar Valor OP Coluna aqui explicitamente se necessário
        match_generic = re.match(r'\s*([\w\.]+)\s*(=|>|<|<=|>=|<>)\s*(.*?)?\s*$', part, re.IGNORECASE)
        if match_generic:
             match = match_generic
             # Assume que o lado direito é literal se não casou como coluna antes
             # Precisaria validar o literal aqui também
        else:
            raise ValueError(f"Formato inválido ou operador não reconhecido na condição: '{part}'. Use Coluna OP Valor ou Alias1.Coluna1 OP Alias2.Coluna2.")


    left_operand_str = match.group(1).strip()
    operator = match.group(2).strip()
    right_operand_str = match.group(3).strip() if match.group(3) is not None else ""

    if operator not in ALLOWED_OPERATORS: raise ValueError(f"Operador '{operator}' não permitido: '{part}'. Permitidos: {', '.join(ALLOWED_OPERATORS)}")

    try:
        l_table_norm, l_col_norm, l_alias_norm = _validate_column_name(left_operand_str, involved_aliases_map)
        rewritten_left = f"{l_alias_norm}.{l_col_norm}"
    except ValueError as e: raise ValueError(f"Erro no operando esquerdo da condição '{part}': {e}")

    rewritten_right = ""
    if is_col_op_col: # Se casou com Coluna OP Coluna
         try:
             r_table_norm, r_col_norm, r_alias_norm = _validate_column_name(right_operand_str, involved_aliases_map)
             rewritten_right = f"{r_alias_norm}.{r_col_norm}"
         except ValueError as e: raise ValueError(f"Erro no operando direito (coluna) da condição '{part}': {e}")
    else: # Se casou com Coluna OP Valor (ou genérico)
         # Revalida o lado direito como literal (segurança)
         try:
            # Tenta validar como coluna (caso a regex genérica tenha casado)
             _validate_column_name(right_operand_str, involved_aliases_map)
             # Se passou, é um erro - deveria ter casado com Col Op Col antes
             raise ValueError(f"Ambiguidade inesperada no tipo do operando direito '{right_operand_str}' na condição '{part}'.")
         except ValueError:
             # Não é coluna, valida como número ou string
             try:
                 float(right_operand_str)
                 rewritten_right = right_operand_str # Mantém número
             except ValueError:
                 if not ((right_operand_str.startswith("'") and right_operand_str.endswith("'")) or \
                         (right_operand_str.startswith('"') and right_operand_str.endswith('"'))):
                     raise ValueError(f"Valor '{right_operand_str}' na condição '{part}' não é um número, string entre aspas ou coluna válida.")
                 rewritten_right = right_operand_str # Mantém string

    return f"{rewritten_left} {operator} {rewritten_right}"


def _process_conditions(condition_str, involved_aliases_map, table_alias_details):
    """
    Processa e reescreve todas as condições de uma cláusula WHERE ou ON, retornando-as no formato da álgebra relacional.
    """
    if not condition_str: return []
    parts = re.split(r'\s+AND\s+', condition_str, flags=re.IGNORECASE)
    rewritten_parts = []
    for part in parts:
        part = part.strip().strip('()')
        if part:
            try:
                rewritten = _rewrite_condition_part(part, involved_aliases_map, table_alias_details)
                rewritten_parts.append(rewritten)
            except ValueError as e: raise ValueError(f"Erro ao processar parte da condição '{part}': {e}")
    return rewritten_parts

# --- Função Principal de Parsing e Validação ---
def parse_validate_sql(sql_query):
    """
    Realiza o parsing e validação de uma consulta SQL restrita, retornando a estrutura parseada.
    """
    query = sql_query.strip()
    if not query: raise ValueError("Consulta SQL não pode ser vazia.")
    select_match = re.match(r"SELECT\s+(.*?)\s+(FROM\s+.*)", query, re.IGNORECASE | re.DOTALL)
    if not select_match: raise ValueError("Erro de sintaxe: Consulta deve começar com 'SELECT ... FROM ...'")
    select_part = select_match.group(1).strip(); remaining_query = select_match.group(2).strip()
    if not select_part: raise ValueError("Erro de sintaxe: Cláusula SELECT não pode ser vazia.")
    select_columns_str = [col.strip() for col in select_part.split(',')]
    if not select_columns_str or any(not col for col in select_columns_str): raise ValueError("Erro de sintaxe: Especifique colunas válidas ou '*' na cláusula SELECT.")

    from_pattern_str = r"FROM\s+(?P<from_table>\S+)(?:\s+(?:AS\s+)?(?P<from_alias>\S+))?"
    join_block_pattern_str = r"(?P<joins>(?:\s+INNER\s+JOIN\s+\S+(?:\s+(?:AS\s+)?\S+)?\s+ON\s+.*?)+)"
    where_pattern_str = r"(?:\s+WHERE\s+(?P<where>.*))?"
    full_pattern = re.compile(from_pattern_str + r"\s*(?:" + join_block_pattern_str + r")?" + r"\s*" + where_pattern_str + r"\s*$", re.IGNORECASE | re.DOTALL)
    match = full_pattern.match(remaining_query)
    if not match: raise ValueError(f"Erro de sintaxe: Não foi possível parsear a estrutura após SELECT. Query restante: '{remaining_query}'")
    match_dict = match.groupdict()

    parsed_data = {'select_columns_str': select_columns_str}; aliases = {}; table_alias_details = {}; used_aliases = set(); joins_info_list = []; where_condition_str = None

    from_table_name = match_dict.get('from_table'); from_alias = match_dict.get('from_alias')
    from_table_norm, from_alias_norm = _validate_and_get_table_alias(from_table_name, from_alias, used_aliases, table_alias_details)
    aliases[from_alias_norm] = from_table_norm
    parsed_data['from_table'] = {'name': from_table_norm, 'alias': from_alias_norm}

    if 'joins' in match_dict and match_dict['joins']:
        all_joins_str = match_dict['joins'].strip()
        join_pattern = re.compile(r"INNER\s+JOIN\s+(?P<jt>\S+)(?:\s+(?:AS\s+)?(?P<ja>\S+))?\s+ON\s+(?P<jc>.+?)(?=\s+INNER\s+JOIN|\s*$)", re.IGNORECASE | re.DOTALL)
        last_join_end = 0
        for join_match in join_pattern.finditer(all_joins_str):
            join_match_dict = join_match.groupdict()
            join_table_name = join_match_dict.get('jt'); join_alias = join_match_dict.get('ja'); join_condition_str = join_match_dict.get('jc','').strip()
            if not join_condition_str: raise ValueError(f"Erro de sintaxe: INNER JOIN com tabela '{join_table_name}' requer uma condição ON não vazia.")
            join_table_norm, join_alias_norm = _validate_and_get_table_alias(join_table_name, join_alias, used_aliases, table_alias_details)
            aliases[join_alias_norm] = join_table_norm
            joins_info_list.append({'table_norm': join_table_norm, 'alias_norm': join_alias_norm, 'condition_str': join_condition_str})
            last_join_end = join_match.end()
        if last_join_end < len(all_joins_str):
             remaining_part = all_joins_str[last_join_end:].strip()
             if remaining_part: raise ValueError(f"Erro de sintaxe: Parte não reconhecida no final do bloco de JOINs: '{remaining_part}'")

    if 'where' in match_dict and match_dict['where']: where_condition_str = match_dict['where'].strip()
    parsed_data['joins'] = joins_info_list; parsed_data['where_condition_str'] = where_condition_str; parsed_data['aliases'] = aliases; parsed_data['table_alias_details'] = table_alias_details

    all_involved_aliases_map = aliases.copy()
    validated_select_cols = []
    is_select_all = (len(select_columns_str) == 1 and select_columns_str[0] == '*')
    if not is_select_all:
        for col_str in select_columns_str:
            try:
                table_norm, col_norm, alias_norm = _validate_column_name(col_str, all_involved_aliases_map)
                validated_select_cols.append({'original': col_str, 'table': table_norm, 'column': col_norm, 'alias': alias_norm})
            except ValueError as e:
                aliases_involved_str = ', '.join(all_involved_aliases_map.keys())
                raise ValueError(f"Erro na cláusula SELECT validando '{col_str}': {e} (Aliases/Tabelas disponíveis: {aliases_involved_str})")
    else: validated_select_cols.append({'original': '*'})
    parsed_data['validated_select_cols'] = validated_select_cols

    try: parsed_data['rewritten_where_conditions'] = _process_conditions(parsed_data['where_condition_str'], all_involved_aliases_map, table_alias_details) if parsed_data['where_condition_str'] else []
    except ValueError as e: raise ValueError(f"Erro na cláusula WHERE: {e}")

    for join_info in parsed_data['joins']:
         involved_in_on = all_involved_aliases_map
         try:
             join_info['rewritten_conditions'] = _process_conditions(join_info['condition_str'], involved_in_on, table_alias_details)
             if not join_info['rewritten_conditions']: raise ValueError(f"Condição ON resultou em predicados vazios após processamento.")
         except ValueError as e:
             original_table_name = next((v['original_table_name'] for k, v in table_alias_details.items() if k == join_info['table_norm']), '???') # Get original name for error
             raise ValueError(f"Erro na condição ON para JOIN com tabela '{original_table_name}' (alias '{join_info['alias_norm']}'): {e} (Condição original: '{join_info['condition_str']}')")

    return parsed_data

# --- Função de Conversão para Álgebra Relacional ---
def convert_to_relational_algebra(parsed_data):
    """
    Converte a estrutura parseada para uma expressão de álgebra relacional.
    """
    details = parsed_data['table_alias_details']
    from_table_info = parsed_data['from_table']
    from_table_norm = from_table_info['name']
    from_alias_norm = details[from_table_norm]['alias']
    # Formato: nometabela[alias]
    base_operation = f"{from_table_norm}[{from_alias_norm}]"

    all_join_conditions = []
    for join_info in parsed_data['joins']:
        join_table_norm = join_info['table_norm']
        join_alias_norm = details[join_table_norm]['alias']
        base_operation = f"({base_operation} ⨝ {join_table_norm}[{join_alias_norm}])"
        all_join_conditions.extend(join_info['rewritten_conditions'])

    all_conditions = parsed_data['rewritten_where_conditions'] + all_join_conditions
    condition_string = " ∧ ".join(all_conditions) if all_conditions else ""

    selection_result = base_operation
    if condition_string: selection_result = f"𝛔[{condition_string}]({base_operation})"

    select_cols_info = parsed_data['validated_select_cols']
    projection_attributes = []
    details_for_projection = parsed_data['table_alias_details']

    if select_cols_info[0]['original'] == '*':
        involved_table_order = [parsed_data['from_table']['name']] + [j['table_norm'] for j in parsed_data['joins']]
        processed_tables = set()
        for table_norm in involved_table_order:
             if table_norm not in processed_tables:
                 alias_norm = details_for_projection[table_norm]['alias']
                 for column_name_original_case in DATABASE_SCHEMA[table_norm]:
                      col_norm = _normalize_name(column_name_original_case)
                      projection_attributes.append(f"{alias_norm}.{col_norm}")
                 processed_tables.add(table_norm)
    else:
        for col_info in select_cols_info:
            alias_norm = col_info['alias']
            col_norm = col_info['column']
            projection_attributes.append(f"{alias_norm}.{col_norm}")

    projection_string = ", ".join(projection_attributes)
    final_algebra = f"𝝿[{projection_string}]({selection_result})"
    return final_algebra

# --- Função Principal de Processamento ---
def process_sql_query(sql_query):
    """
    Função principal para processar uma consulta SQL: faz o parsing, valida e converte para álgebra relacional.
    """
    try:
        parsed_data = parse_validate_sql(sql_query)
        relational_algebra = convert_to_relational_algebra(parsed_data)
        return relational_algebra
    except ValueError as e:
        print(f"Erro: {e}")
        return e
    except Exception as e:
        print(f"Erro inesperado no processamento: {e}")
        import traceback
        traceback.print_exc()
        return e

# --- Bloco Principal para Testes ---
if __name__ == "__main__":
    print("--- Iniciando Bateria de Testes do Parser SQL (v2 - Revisão 6/Final) ---")

    # ATENÇÃO: Todas as expected_ra usam minúsculas para identificadores
    test_cases = [
        # --- Testes: SELECT Simples ---
        {"description": "T1: SELECT simples, duas colunas", "sql": "SELECT nome, email FROM Cliente", "expect_error": False, "expected_ra": "𝝿[cliente.nome, cliente.email](cliente[cliente])"},
        {"description": "T2: SELECT simples, case-insensitive", "sql": "select NOME, EmAiL FrOm CLIENTE", "expect_error": False, "expected_ra": "𝝿[cliente.nome, cliente.email](cliente[cliente])"},
        {"description": "T3: SELECT * simples", "sql": "SELECT * FROM TipoCliente", "expect_error": False, "expected_ra": "𝝿[tipocliente.idtipocliente, tipocliente.descricao](tipocliente[tipocliente])"},
        # --- Testes: Cláusula WHERE ---
        {"description": "T4: SELECT com WHERE simples (número)", "sql": "SELECT Nome FROM Produto WHERE Preco > 50.00", "expect_error": False, "expected_ra": "𝝿[produto.nome](𝛔[produto.preco > 50.00](produto[produto]))"},
        {"description": "T5: SELECT com WHERE simples (string)", "sql": "SELECT Nome FROM Cliente WHERE Email = 'teste@mail.com'", "expect_error": False, "expected_ra": "𝝿[cliente.nome](𝛔[cliente.email = 'teste@mail.com'](cliente[cliente]))"},
        {"description": "T6: SELECT com WHERE e AND", "sql": "SELECT idProduto, QuantEstoque FROM Produto WHERE Preco < 100 AND QuantEstoque >= 10", "expect_error": False, "expected_ra": "𝝿[produto.idproduto, produto.quantestoque](𝛔[produto.preco < 100 ∧ produto.quantestoque >= 10](produto[produto]))"},
        {"description": "T14: WHERE com coluna não qualificada (não ambígua)", "sql": "SELECT Nome FROM Cliente WHERE idCliente < 5", "expect_error": False, "expected_ra": "𝝿[cliente.nome](𝛔[cliente.idcliente < 5](cliente[cliente]))"},
        {"description": "T15: Comparação entre colunas no WHERE (qualificadas)", "sql": "SELECT p.idPedido FROM Pedido p INNER JOIN Cliente c ON p.Cliente_idCliente = c.idCliente WHERE p.DataPedido > c.DataRegistro", "expect_error": False, "expected_ra": "𝝿[p.idpedido](𝛔[p.datapedido > c.dataregistro ∧ p.cliente_idcliente = c.idcliente]((pedido[p] ⨝ cliente[c])))"},
        # --- Testes: INNER JOIN ---
        {"description": "T7: SELECT com INNER JOIN simples (sem alias)", "sql": "SELECT Cliente.Nome, Pedido.DataPedido FROM Cliente INNER JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente", "expect_error": False, "expected_ra": "𝝿[cliente.nome, pedido.datapedido](𝛔[cliente.idcliente = pedido.cliente_idcliente]((cliente[cliente] ⨝ pedido[pedido])))"},
        {"description": "T8: SELECT com INNER JOIN simples (com alias)", "sql": "SELECT c.Nome, p.DataPedido FROM Cliente c INNER JOIN Pedido p ON c.idCliente = p.Cliente_idCliente", "expect_error": False, "expected_ra": "𝝿[c.nome, p.datapedido](𝛔[c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))"},
        {"description": "T9: SELECT com INNER JOIN e WHERE (com alias)", "sql": "SELECT c.Nome, p.idPedido FROM Cliente AS c INNER JOIN Pedido AS p ON c.idCliente = p.Cliente_idCliente WHERE p.ValorTotalPedido > 100.0", "expect_error": False, "expected_ra": "𝝿[c.nome, p.idpedido](𝛔[p.valortotalpedido > 100.0 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))"},
        {"description": "T10: SELECT * com INNER JOIN (com alias)", "sql": "SELECT * FROM Categoria C INNER JOIN Produto P ON C.idCategoria = P.Categoria_idCategoria", "expect_error": False, "expected_ra": "𝝿[c.idcategoria, c.descricao, p.idproduto, p.nome, p.descricao, p.preco, p.quantestoque, p.categoria_idcategoria](𝛔[c.idcategoria = p.categoria_idcategoria]((categoria[c] ⨝ produto[p])))"},
        {"description": "T11: SELECT com Múltiplos INNER JOINs (com alias)", "sql": "SELECT Ped.idPedido, Prod.Nome, Itens.Quantidade FROM Pedido Ped INNER JOIN Pedido_has_Produto Itens ON Ped.idPedido = Itens.Pedido_idPedido INNER JOIN Produto Prod ON Itens.Produto_idProduto = Prod.idProduto", "expect_error": False, "expected_ra": "𝝿[ped.idpedido, prod.nome, itens.quantidade](𝛔[ped.idpedido = itens.pedido_idpedido ∧ itens.produto_idproduto = prod.idproduto](((pedido[ped] ⨝ pedido_has_produto[itens]) ⨝ produto[prod])))"},
        {"description": "T12: SELECT com Múltiplos INNER JOINs e WHERE", "sql": "SELECT Ped.idPedido, Prod.Nome FROM Pedido Ped INNER JOIN Pedido_has_Produto Itens ON Ped.idPedido = Itens.Pedido_idPedido INNER JOIN Produto Prod ON Itens.Produto_idProduto = Prod.idProduto WHERE Ped.Cliente_idCliente = 10 AND Itens.Quantidade > 1", "expect_error": False, "expected_ra": "𝝿[ped.idpedido, prod.nome](𝛔[ped.cliente_idcliente = 10 ∧ itens.quantidade > 1 ∧ ped.idpedido = itens.pedido_idpedido ∧ itens.produto_idproduto = prod.idproduto](((pedido[ped] ⨝ pedido_has_produto[itens]) ⨝ produto[prod])))"},
        {"description": "T13: Condição ON com colunas em ordem invertida", "sql": "SELECT c.Nome, p.DataPedido FROM Cliente c INNER JOIN Pedido p ON p.Cliente_idCliente = c.idCliente", "expect_error": False, "expected_ra": "𝝿[c.nome, p.datapedido](𝛔[p.cliente_idcliente = c.idcliente]((cliente[c] ⨝ pedido[p])))"},
        # --- Testes: Erros Esperados ---
        {"description": "E1: Tabela inexistente no FROM", "sql": "SELECT nome FROM Clientes", "expect_error": True},
        {"description": "E2: Tabela inexistente no JOIN", "sql": "SELECT c.nome FROM Cliente c INNER JOIN Pedidos_Invalidos p ON c.idCliente = p.cliente_id", "expect_error": True},
        {"description": "E3: Coluna inexistente no SELECT", "sql": "SELECT nome, sobrenome FROM Cliente", "expect_error": True},
        {"description": "E4: Coluna inexistente no WHERE", "sql": "SELECT nome FROM Cliente WHERE apelido = 'Jo'", "expect_error": True},
        {"description": "E5: Coluna inexistente no ON", "sql": "SELECT c.nome FROM Cliente c INNER JOIN Pedido p ON c.id = p.Cliente_idCliente", "expect_error": True},
        {"description": "E6: Alias repetido", "sql": "SELECT c.nome FROM Cliente c INNER JOIN Pedido c ON c.idCliente = c.Cliente_idCliente", "expect_error": True},
        {"description": "E7: Alias não definido referenciado no SELECT", "sql": "SELECT x.nome FROM Cliente c WHERE c.idCliente = 1", "expect_error": True},
        {"description": "E7b: Alias não definido referenciado no WHERE", "sql": "SELECT c.nome FROM Cliente c WHERE x.idCliente = 1", "expect_error": True},
        # --- Testes: Ambiguidade ---
        {"description": "E8: Coluna ambígua no SELECT", "sql": "SELECT Descricao FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = C.idCategoria", "expect_error": True},
        {"description": "E9: Coluna ambígua no WHERE", "sql": "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = C.idCategoria WHERE Descricao = 'Teste'", "expect_error": True},
        {"description": "E10: Coluna ambígua no ON (lado direito) - NÃO É AMBIGUO", "sql": "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = idCategoria", "expect_error": False, "expected_ra": "𝝿[p.nome](𝛔[p.categoria_idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
        {"description": "E10b: Coluna ambígua no ON (lado esquerdo) - NÃO É AMBIGUO", "sql": "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON idCategoria = C.idCategoria", "expect_error": False, "expected_ra": "𝝿[p.nome](𝛔[c.idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
        {"description": "E10c: Ambas colunas ambíguas no ON - NÃO É AMBIGUO", "sql": "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON idCategoria = idCategoria", "expect_error": False, "expected_ra": "𝝿[p.nome](𝛔[c.idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
        {"description": "E10d: Ambiguidade com Self Join - É AMBIGUO", "sql": "SELECT c1.Nome FROM Cliente c1 INNER JOIN Cliente c2 ON c1.TipoCliente_idTipoCliente = TipoCliente_idTipoCliente", "expect_error": True},
        # --- Testes: Erros de Sintaxe ---
        {"description": "E11: Operador inválido no WHERE", "sql": "SELECT nome FROM Produto WHERE Preco && 10", "expect_error": True},
        {"description": "E12: JOIN sem ON", "sql": "SELECT nome FROM Cliente INNER JOIN Pedido", "expect_error": True},
        {"description": "E13: Condição ON vazia", "sql": "SELECT c.nome FROM Cliente c INNER JOIN Pedido p ON", "expect_error": True},
        {"description": "E14: Sintaxe SQL inválida geral", "sql": "SELECT FROM nome clientes WHERE id = 1", "expect_error": True},
    ]

    passed_count = 0; failed_count = 0; failed_tests_details = []
    print("\n--- Executando Testes ---"); test_results = {}
    original_stdout = sys.stdout; sys.stdout = io.StringIO() # Silencia prints internos
    for i, test in enumerate(test_cases):
        test_index = i + 1; #print(f"\n[{test_index}] {test['description']}") # Comentado para output limpo
        result_ra = process_sql_query(test['sql']); test_results[test_index] = {'result': result_ra, 'test': test}
    sys.stdout = original_stdout # Restaura prints

    print("\n--- Verificando Resultados ---")
    for i, data in test_results.items():
        test = data['test']; result_ra = data['result']; status = "FAIL"; details = ""; passed = False
        print(f"\n[{i}] {test['description']}")
        if test['expect_error']:
            if result_ra is None: status = "PASS"; details = "Erro esperado ocorreu."; passed = True
            else: details = f"Falhou! Erro era esperado, mas query foi processada.\n      Resultado: {result_ra}"
        else:
            if result_ra is not None:
                expected_ra_norm = ' '.join(test['expected_ra'].split())
                result_ra_norm = ' '.join(result_ra.split())
                if result_ra_norm == expected_ra_norm: status = "PASS"; details = "Álgebra Relacional Correta."; passed = True
                else: details = f"Falhou! Álgebra Relacional incorreta.\n      Esperado: '{test['expected_ra']}'\n      Recebido: '{result_ra}'"
            else: details = f"Falhou! Erro inesperado ocorreu (query não processada - veja log de erro impresso durante execução se houver)."
        print(f"Status: {status}")
        if passed: passed_count += 1
        else: print(details); failed_count += 1; failed_tests_details.append(f"[{i}] {test['description']}\n{details}")

    print("\n--- Resumo dos Testes ---"); print(f"Total Executado: {len(test_cases)}"); print(f"Aprovados: {passed_count}"); print(f"Reprovados: {failed_count}")
    if failed_count > 0: print("\n--- Detalhes das Falhas ---"); [print(f"\n{detail}") for detail in failed_tests_details]
    print("\n--- Testes Concluídos ---")