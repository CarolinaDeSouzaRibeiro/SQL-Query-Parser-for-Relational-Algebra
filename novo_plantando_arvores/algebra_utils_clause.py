from .arvore import NoArvore, Arvore, ArvoreDrawer
from .parser_algebra import construir_arvore
import re

def formatar_algebra_relacional(algebra: str) -> str:
    """
    Remove espaços desnecessários em uma expressão de álgebra relacional.
    Esta função normaliza a expressão de álgebra relacional, garantindo que:
    - Espaços em branco em excesso sejam reduzidos a um único espaço.
    - Não haja espaços logo após parênteses ou colchetes de abertura.
    - Não haja espaços logo antes de parênteses ou colchetes de fechamento.
    Args:
        algebra (str): Expressão de álgebra relacional em formato textual.
    Returns:
        str: Expressão formatada com espaçamento consistente.
    """
    algebra = re.sub(r'\s+', ' ', algebra)
    algebra = re.sub(r'\(\s+', '(', algebra)
    algebra = re.sub(r'\s+\)', ')', algebra)
    algebra = re.sub(r'\[\s+', '[', algebra)
    algebra = re.sub(r'\s+\]', ']', algebra)
    return algebra.strip()

def extrair_subexpressao(expr: str, inicio: int) -> tuple[str, int]:
    """
    Extrai a subexpressão entre parênteses a partir de `inicio`.
    
    Args:
        expr (str): A expressão completa.
        inicio (int): Índice do parêntese de abertura.
        
    Returns:
        tuple[str, int]: A subexpressão (incluindo parênteses) e o índice após o parêntese de fechamento.
    """
    assert expr[inicio] == '(', "Início inválido para subexpressão"
    contador = 1
    fim = inicio + 1
    while fim < len(expr) and contador > 0:
        if expr[fim] == '(':
            contador += 1
        elif expr[fim] == ')':
            contador -= 1
        fim += 1
    return expr[inicio:fim], fim

def remover_joins(algebra: str) -> str:
    """
    Substitui operadores de junção (⨝[condição]) por produto cartesiano (X) e
    eleva suas condições para a cláusula de seleção (𝛔).
    Se já houver uma seleção no nível apropriado, a condição será aninhada com `∧`.
    Caso contrário, será criada uma nova seleção englobando o produto cartesiano.
    
    Args:
        algebra (str): Expressão de álgebra relacional com junções.
        
    Returns:
        str: Expressão equivalente sem junções explícitas.
    """
    algebra = formatar_algebra_relacional(algebra)
    condicoes = []
    
    def substituir_joins(expr: str) -> str:
        """
        Substitui todas as junções da expressão por produtos cartesianos.
        """
        i = 0
        while i < len(expr):
            if expr[i] == '(':
                subexpr_esq, fim_esq = extrair_subexpressao(expr, i)
                j = fim_esq
                while j < len(expr) and expr[j].isspace():
                    j += 1
                if j < len(expr) and expr[j:j+2] == '⨝[':
                    idx_ini_cond = j + 2
                    idx_fim_cond = expr.find(']', idx_ini_cond)
                    if idx_fim_cond == -1:
                        raise ValueError("Não foi encontrado o fechamento do colchete na condição de junção")
                    cond = expr[idx_ini_cond:idx_fim_cond]
                    condicoes.append(cond.strip())
                    k = idx_fim_cond + 1
                    while k < len(expr) and expr[k].isspace():
                        k += 1
                    if k >= len(expr) or expr[k] != '(':
                        raise ValueError("Expressão de join malformada")
                    subexpr_dir, fim_dir = extrair_subexpressao(expr, k)
                    # Recurso principal: substituir tudo
                    nova_expr = f"{substituir_joins(subexpr_esq[1:-1])} X {substituir_joins(subexpr_dir[1:-1])}"
                    expr = expr[:i] + '(' + nova_expr + ')' + expr[fim_dir:]
                    i = 0  # reiniciar busca
                else:
                    # Processa parênteses aninhados
                    subexpr_interna = substituir_joins(subexpr_esq[1:-1])
                    expr = expr[:i] + '(' + subexpr_interna + ')' + expr[fim_esq:]
                    i = fim_esq
            else:
                i += 1
        return expr
    
    def inserir_condicoes(expr: str) -> str:
        if not condicoes:
            return expr
        condicao_total = ' ∧ '.join(f'({c})' for c in condicoes)
        padrao = re.compile(r'𝛔\[(.*?)\]\(')
        match = padrao.search(expr)
        if match:
            cond_existente = match.group(1)
            nova_cond = f'{cond_existente} ∧ {condicao_total}'
            return padrao.sub(f'𝛔[{nova_cond}](', expr, count=1)
        else:
            return f'𝛔[{condicao_total}]({expr})'
    
    resultado = substituir_joins(algebra)
    resultado = inserir_condicoes(resultado)
    return resultado

def quebrar_por_conjuncao(condicao: str) -> list[str]:
    """
    Quebra uma condição composta por conjunções (∧) em uma lista de condições simples,
    respeitando parênteses.
    
    Args:
        condicao (str): Condição composta.
        
    Returns:
        list[str]: Lista de condições simples.
    """
    partes = []
    atual = ''
    nivel = 0
    i = 0
    while i < len(condicao):
        if condicao[i] == '(':
            nivel += 1
            atual += condicao[i]
        elif condicao[i] == ')':
            nivel -= 1
            atual += condicao[i]
        elif nivel == 0 and condicao[i:i+1] == '∧':
            partes.append(atual.strip())
            atual = ''
            i += 1  # Pular o símbolo de conjunção
            continue
        else:
            atual += condicao[i]
        i += 1
    
    if atual.strip():
        partes.append(atual.strip())
    return partes

def desaninhar_selects(algebra: str) -> str:
    """
    Desfaz seleções compostas (𝛔) com múltiplas condições unidas por ∧,
    transformando-as em seleções aninhadas, uma por condição.
    
    Args:
        algebra (str): Expressão de álgebra relacional com seleções compostas.
        
    Returns:
        str: Expressão com seleções aninhadas.
    """
    algebra = formatar_algebra_relacional(algebra)
    
    def quebrar_condicoes(expr: str) -> str:
        """
        Substitui seleções compostas por seleções aninhadas.
        Mantém os parênteses balanceados corretamente.
        """
        # Verificar se há alguma seleção composta
        padrao = re.compile(r'𝛔\[(.*?)\]\(')
        match = padrao.search(expr)
        
        if not match:
            return expr
            
        # Encontramos uma seleção, vamos processá-la
        idx_inicio = match.start()
        idx_subexpr = match.end()
        condicao = match.group(1)
        
        # Extrai a subexpressão dentro da seleção
        subexpr_completa, fim_subexpr = extrair_subexpressao(expr, idx_subexpr - 1)
        subexpr = subexpr_completa[1:-1]  # Remove os parênteses externos
        
        # Processa recursivamente o que está dentro da subexpressão
        subexpr_processada = quebrar_condicoes(subexpr)
        
        # Quebra as condições desta seleção
        conds = quebrar_por_conjuncao(condicao)
        
        # Aplica cada condição como uma seleção separada
        nova_expr = subexpr_processada
        for cond in reversed(conds):
            nova_expr = f'𝛔[{cond}]({nova_expr})'
        
        # Monta a expressão final
        prefixo = expr[:idx_inicio]
        sufixo = expr[fim_subexpr:]
        
        # Processa o restante da expressão recursivamente
        sufixo_processado = quebrar_condicoes(sufixo)
        
        return prefixo + nova_expr + sufixo_processado
    
    return quebrar_condicoes(algebra)

def extrair_tabelas_dependentes(condicao: str) -> set[str]:
    """
    Extrai os aliases de tabelas das quais uma condição depende.
    
    Args:
        condicao (str): Condição de seleção (ex: "C.TipoCliente = 4").
        
    Returns:
        set[str]: Conjunto de aliases de tabelas.
    """
    # Identifica padrões como X.campo onde X é o alias da tabela
    aliases = re.findall(r'([A-Za-z0-9_]+)\.[A-Za-z0-9_]+', condicao)
    return set(aliases)

def extrair_tabelas_da_expressao(expr: str) -> set[str]:
    """
    Extrai os aliases de tabelas presentes em uma expressão.
    
    Args:
        expr (str): Subexpressão da álgebra relacional.
        
    Returns:
        set[str]: Conjunto de aliases de tabelas.
    """
    # Encontra padrões como Tabela[Alias]
    padrao_tabela = re.compile(r'([A-Za-z0-9_]+)\[([A-Za-z0-9_]+)\]')
    return {m.group(2) for m in padrao_tabela.finditer(expr)}

def encontrar_operacao_principal(expr: str) -> tuple[str, int, int]:
    """
    Identifica o operador principal (⨝ ou X) na raiz da expressão e seus índices.
    
    Args:
        expr (str): Expressão de álgebra relacional.
        
    Returns:
        tuple[str, int, int]: Operador, índice de início e fim da primeira subexpressão.
    """
    nivel = 0
    for i, c in enumerate(expr):
        if c == '(':
            nivel += 1
        elif c == ')':
            nivel -= 1
        # Só verificamos operadores no nível raiz (nivel == 1)
        elif nivel == 1:
            # Verificar se é um operador de junção
            if expr[i:i+2] == '⨝[':
                idx_fim = expr.find(']', i+2)
                subexpr_esq, _ = extrair_subexpressao(expr, 0)
                return '⨝', 0, len(subexpr_esq)
            # Verificar se é um operador de produto cartesiano
            elif c == 'X' and expr[i-1].isspace() and expr[i+1].isspace():
                subexpr_esq, _ = extrair_subexpressao(expr, 0)
                return 'X', 0, len(subexpr_esq)
    return None, -1, -1

def empurrar_selects_para_baixo(algebra: str) -> str:
    """
    Empurra os operadores de seleção (𝛔) para o mais próximo possível das tabelas
    das quais dependem. Se uma seleção depende de apenas uma tabela, ela é aplicada
    diretamente à tabela. Se depende de múltiplas tabelas, ela é aplicada no nível
    mais baixo onde todas essas tabelas estão disponíveis.
    
    Args:
        algebra (str): Expressão de álgebra relacional com seleções no topo.
        
    Returns:
        str: Expressão com seleções empurradas para baixo.
    """
    algebra = formatar_algebra_relacional(algebra)
    
    # Primeira etapa: extrair todas as condições de seleção
    def extrair_selects(expr: str) -> tuple[str, list[tuple[str, set[str]]]]:
        """
        Extrai todos os operadores de seleção de uma expressão.
        
        Returns:
            tuple: (expr_sem_selects, lista_de_selects)
                onde lista_de_selects é uma lista de tuplas (condição, conjunto_de_tabelas)
        """
        selects = []
        
        # Verifica se a expressão começa com uma seleção
        while True:
            match = re.match(r'^𝛔\[(.*?)\]\((.*)\)$', expr)
            if not match:
                break
                
            condicao = match.group(1)
            expr = match.group(2)  # Expressão sem a seleção atual
            
            # Extrai tabelas dependentes na condição
            tabelas_deps = extrair_tabelas_dependentes(condicao)
            selects.append((condicao, tabelas_deps))
        
        return expr, selects
    
    # Segunda etapa: aplicar as seleções nos níveis mais baixos possíveis
    def aplicar_selects(expr: str, selects: list[tuple[str, set[str]]]) -> tuple[str, list[tuple[str, set[str]]]]:
        """
        Aplica as seleções extraídas no nível mais baixo possível.
        
        Returns:
            tuple: (nova_expressao, selects_restantes)
        """
        # Caso base: se não há mais seleções para aplicar
        if not selects:
            return expr, []
            
        # Caso de tabela simples: aplica diretamente as seleções relevantes
        match_tabela = re.match(r'^([A-Za-z0-9_]+)\[([A-Za-z0-9_]+)\]$', expr)
        if match_tabela:
            # Pegamos o alias da tabela
            tabela = match_tabela.group(1)
            alias = match_tabela.group(2)
            
            # Filtramos apenas as seleções que dependem exclusivamente desta tabela
            selects_aplicaveis = [(cond, tabs) for cond, tabs in selects if tabs == {alias}]
            selects_restantes = [(cond, tabs) for cond, tabs in selects if tabs != {alias}]
            
            # Aplicamos as seleções relevantes
            result = expr
            for cond, _ in selects_aplicaveis:
                result = f"𝛔[{cond}]({result})"
                
            return result, selects_restantes
        
        # Caso de projeção (𝝿): processa a subexpressão
        match_proj = re.match(r'^𝝿\[(.*?)\]\((.*)\)$', expr)
        if match_proj:
            atributos = match_proj.group(1)
            subexpr = match_proj.group(2)
            
            # Processa a subexpressão recursivamente
            nova_subexpr, selects_restantes = aplicar_selects(subexpr, selects)
            
            # Reconstrói a projeção com a subexpressão processada
            result = f"𝝿[{atributos}]({nova_subexpr})"
            
            return result, selects_restantes
        
        # Caso de junção ou produto cartesiano
        if expr.startswith('(') and expr.endswith(')'):
            conteudo = expr[1:-1]
            
            # Verificamos se é uma operação binária (junção ou produto cartesiano)
            # Procuramos o operador principal no nível raiz
            nivel_par = 0
            pos_operador = -1
            tipo_operador = None
            
            for i, c in enumerate(conteudo):
                if c == '(':
                    nivel_par += 1
                elif c == ')':
                    nivel_par -= 1
                elif nivel_par == 0:
                    # Verificamos para junção (⨝)
                    if conteudo[i:i+2] == '⨝[':
                        pos_operador = i
                        tipo_operador = '⨝'
                        break
                    # Verificamos para produto cartesiano (X)
                    elif i > 0 and i < len(conteudo) - 1 and conteudo[i] == 'X' and conteudo[i-1].isspace() and conteudo[i+1].isspace():
                        pos_operador = i
                        tipo_operador = 'X'
                        break
            
            # Se encontramos um operador binário
            if tipo_operador:
                # Extraímos os operandos (esquerdo e direito)
                operand_esq = conteudo[:pos_operador].strip()
                
                if tipo_operador == '⨝':
                    # Para junção, precisamos extrair também a condição
                    inicio_cond = pos_operador + 2
                    fim_cond = conteudo.find(']', inicio_cond)
                    cond_join = conteudo[inicio_cond:fim_cond]
                    operand_dir = conteudo[fim_cond+1:].strip()
                else:  # tipo_operador == 'X'
                    cond_join = None
                    operand_dir = conteudo[pos_operador+1:].strip()
                
                # Extraímos todas as tabelas de cada lado
                tabelas_esq = extrair_tabelas_da_expressao(operand_esq)
                tabelas_dir = extrair_tabelas_da_expressao(operand_dir)
                
                # Dividimos as seleções por dependência
                selects_esq = []
                selects_dir = []
                selects_ambos = []
                selects_restantes = []
                
                for cond, tabs in selects:
                    if tabs.issubset(tabelas_esq):
                        selects_esq.append((cond, tabs))
                    elif tabs.issubset(tabelas_dir):
                        selects_dir.append((cond, tabs))
                    elif tabs.issubset(tabelas_esq.union(tabelas_dir)):
                        selects_ambos.append((cond, tabs))
                    else:
                        selects_restantes.append((cond, tabs))
                
                # Processamos recursivamente cada lado
                novo_esq, _ = aplicar_selects(operand_esq, selects_esq)
                novo_dir, _ = aplicar_selects(operand_dir, selects_dir)
                
                # Reconstruímos a expressão
                if tipo_operador == '⨝':
                    nova_expr = f"({novo_esq} ⨝[{cond_join}] {novo_dir})"
                else:  # tipo_operador == 'X'
                    nova_expr = f"({novo_esq} X {novo_dir})"
                
                # Aplicamos as seleções que dependem de ambos os lados
                result = nova_expr
                for cond, _ in selects_ambos:
                    result = f"𝛔[{cond}]({result})"
                
                return result, selects_restantes
            
            # Se não é uma operação binária, processamos o conteúdo recursivamente
            nova_expr, selects_restantes = aplicar_selects(conteudo, selects)
            result = f"({nova_expr})"
            return result, selects_restantes
        
        # Caso não identificado, mantemos as seleções no topo
        result = expr
        for cond, _ in selects:
            result = f"𝛔[{cond}]({result})"
        
        return result, []
    
    # Processamento principal
    # 1. Extraímos todas as seleções
    expr_sem_selects, selects = extrair_selects(algebra)
    
    # 2. Aplicamos as seleções nos níveis apropriados
    resultado, selects_restantes = aplicar_selects(expr_sem_selects, selects)
    
    # 3. Aplicamos qualquer seleção restante no topo (não deveria ocorrer se tudo for processado corretamente)
    for cond, _ in selects_restantes:
        resultado = f"𝛔[{cond}]({resultado})"
    
    return resultado

if __name__ == "__main__":
    expr = '''𝝿[C.Nome, E.CEP, P.Status](
        𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
             (
               (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
             ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
        )
    )'''
    
    # Exemplo de expressão ideal após transformação
    expr_ideal_sem_joins = '''𝝿[C.Nome, E.CEP, P.Status](
        𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP") ∧ (C.idCliente = E.Cliente_idCliente) ∧ (C.idCliente = P.Cliente_idCliente)](
             (
               (Cliente[C]) X (Pedido[P])
             ) X (Endereco[E])
        )
    )'''
    
    expr_ideal_desaninhado = '''𝝿[C.Nome, E.CEP, P.Status](
        𝛔[C.TipoCliente = 4](
          𝛔[E.UF = "SP"](
             (
               (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
             ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
          )
        )
    )'''
    
    # Ideal com selects empurrados para baixo
    expr_ideal_empurrado = '''𝝿[C.Nome, E.CEP, P.Status](
         (
             (𝛔[C.TipoCliente = 4](Cliente[C])) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
         ) ⨝[C.idCliente = E.Cliente_idCliente] (𝛔[E.UF = "SP"](Endereco[E]))
    )'''
    
    print("Expressão original:")
    original = formatar_algebra_relacional(expr)
    print(original)
    
    print("\n====== APLICAÇÃO INDEPENDENTE DAS TRANSFORMAÇÕES ======")
    
    print("\nTransformação 1: Remover junções")
    sem_juncoes = remover_joins(original)
    print(sem_juncoes)
    
    print("\nTransformação 2: Desaninhar seleções")
    sem_selects_aninhados = desaninhar_selects(original)
    print(sem_selects_aninhados)
    
    print("\n====== APLICAÇÃO SEQUENCIAL DAS TRANSFORMAÇÕES ======")
    
    print("\nRemovendo junções e depois desaninhando:")
    sequencial = desaninhar_selects(remover_joins(original))
    print(sequencial)
    
    print("\n====== VERIFICAÇÕES ======")
    
    # Verificar se a função de desaninhar selects está balanceando corretamente os parênteses
    def verificar_parenteses(expr):
        contador = 0
        for c in expr:
            if c == '(':
                contador += 1
            elif c == ')':
                contador -= 1
            if contador < 0:
                return False
        return contador == 0
        
    print("Parênteses balanceados em original:", verificar_parenteses(original))
    print("Parênteses balanceados em sem_juncoes:", verificar_parenteses(sem_juncoes))
    print("Parênteses balanceados em sem_selects_aninhados:", verificar_parentheses(sem_selects_aninhados))
    print("Parênteses balanceados em sequencial:", verificar_parentheses(sequencial))
    
    print("\n====== NOVA TRANSFORMAÇÃO: EMPURRAR SELECTS PARA BAIXO ======")
    
    selects_abaixo = empurrar_selects_para_baixo(sem_selects_aninhados)
    print(selects_abaixo)
    
    print("Parênteses balanceados em selects empurrados para baixo:", verificar_parentheses(selects_abaixo))
    
    print("\n====== DESENHANDO ARVORES ======")
    
    original_arvore = construir_arvore(original)
    sem_juncoes_arvore = construir_arvore(sem_juncoes)
    sem_selects_aninhados_arvore = construir_arvore(sem_selects_aninhados)
    sequencial_arvore = construir_arvore(sequencial)
    empurrar_arvore = construir_arvore(selects_abaixo)
    
    original_desenhista = ArvoreDrawer(original_arvore)
    sem_juncoes_desenhista = ArvoreDrawer(sem_juncoes_arvore)
    sem_selects_aninhados_desenhista = ArvoreDrawer(sem_selects_aninhados_arvore)
    sequencial_desenhista = ArvoreDrawer(sequencial_arvore)
    empurrar_desenhista = ArvoreDrawer(empurrar_arvore)
    
    original_desenhista.desenhar("original")
    sem_juncoes_desenhista.desenhar("sem_juncoes")
    sem_selects_aninhados_desenhista.desenhar("sem_selects_aninhados")
    sequencial_desenhista.desenhar("sequencial")
    empurrar_desenhista.desenhar("empurrar_selects")
