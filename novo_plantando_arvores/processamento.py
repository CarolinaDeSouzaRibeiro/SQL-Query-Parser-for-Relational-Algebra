from .arvore import NoArvore, Arvore, ArvoreDrawer
from .parser import validar_algebra, formatar_algebra_relacional, converter_algebra_em_arvore
import re

'''
ETAPAS DE OTIMIZAÇÃO

1 - Posicionar as operações de select o mais longe possível da raiz
2 - Adicionar operações de projeção logo acima das folhas da árvore para excluir as colunas que não serão utilizadas de cada tabela
3 - Redefinir a ordem dos produtos cartesianos para que as tabela com menor quantidade de registros sejam envolvidas nos produtos cartesianos primeiro
'''

def remover_joins(algebra: str) -> str:
    '''Transforma joins (⨝[condição]) em produtos cartesianos (X) + seleção (𝛔[condição]) com parênteses em todas as condições'''
    
    # Extrai condições de join ⨝[...]
    join_condicoes = re.findall(r'⨝\[(.*?)\]', algebra)
    # Adiciona parênteses a cada condição de join
    join_condicoes_com_parenteses = [f'({cond})' for cond in join_condicoes]
    
    # Substitui joins por produtos cartesianos
    algebra_sem_joins = re.sub(r'⨝\[[^\]]+\]', 'X', algebra)

    # Verifica se já há uma seleção existente (𝛔[...])
    selecao_match = re.search(r'𝛔\[(.*?)\]', algebra_sem_joins)
    if selecao_match:
        # Garante que condições originais também estejam entre parênteses (se ainda não estiverem)
        condicoes_existentes = selecao_match.group(1)
        condicoes_originais = [f'({c.strip()})' if not c.strip().startswith('(') else c.strip()
                               for c in re.split(r'\s*∧\s*', condicoes_existentes)]
        # Combina as condições
        todas_condicoes = condicoes_originais + join_condicoes_com_parenteses
        novo_predicado = ' ∧ '.join(todas_condicoes)
        # Substitui o predicado antigo pelo novo
        algebra_sem_joins = algebra_sem_joins.replace(selecao_match.group(0), f'𝛔[{novo_predicado}]')
    else:
        # Caso não haja uma seleção anterior
        if join_condicoes_com_parenteses:
            novo_predicado = ' ∧ '.join(join_condicoes_com_parenteses)
            algebra_sem_joins = f'𝛔[{novo_predicado}]({algebra_sem_joins})'
    
    return algebra_sem_joins

def otimizar_selects(algebra: str) -> str:
    '''Posicionar as operações de select o mais longe possível da raiz.
    
    Pode-se fazer isso quando todos as tabelas das quais o select depende sofrerem produto cartesiano (ou forem juntador em um join)
    
    Se um select depender somente de uma tabela, então ele pode ser posicionado logo após a "instanciação" da tabela
    
    Exemplo:
    
    Não otimizado: "𝝿[C.Nome, E.CEP, P.Status](𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](((Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])))"
    
    Otimizado: "𝝿[C.Nome, E.CEP, P.Status](((𝛔[(C.TipoCliente = 4)](Cliente[C])) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])) ⨝[C.idCliente = E.Cliente_idCliente] (𝛔[(E.UF = "SP")](Endereco[E])))"
    '''
    algebra = formatar_algebra_relacional(algebra)

    # Extrair seleção principal
    match = re.search(r'𝛔\[(.*?)\]\((.*)\)', algebra, re.DOTALL)
    if not match:
        return algebra  # Não há seleção a otimizar

    condicoes_brutas = match.group(1)
    sub_algebra = match.group(2)

    # Separar condições da seleção
    condicoes = [c.strip() for c in re.split(r'\s*∧\s*', condicoes_brutas)]

    # Mapear condições por alias de tabela (C., E., P., etc.)
    condicoes_por_tabela = {}
    for cond in condicoes:
        tabelas_mencionadas = set(re.findall(r'\b([A-Z])\.', cond))
        if len(tabelas_mencionadas) == 1:
            alias = list(tabelas_mencionadas)[0]
            condicoes_por_tabela.setdefault(alias, []).append(cond)
        else:
            condicoes_por_tabela.setdefault('global', []).append(cond)

    # Inserir seleções específicas diretamente sobre as tabelas
    def inserir_selects_em_tabelas(expr: str) -> str:
        def aplicar_select(match):
            tabela_expr = match.group(0)
            alias_match = re.search(r'\[(\w)\]', tabela_expr)
            if not alias_match:
                return tabela_expr
            alias = alias_match.group(1)
            if alias in condicoes_por_tabela:
                conds = ' ∧ '.join(condicoes_por_tabela[alias])
                return f'𝛔[{conds}]({tabela_expr})'
            return tabela_expr

        return re.sub(r'\b\w+\[\w+\]', aplicar_select, expr)

    nova_expr = inserir_selects_em_tabelas(sub_algebra)

        # Recoloca a seleção global, se ainda houver alguma
    if 'global' in condicoes_por_tabela:
        conds = ' ∧ '.join(condicoes_por_tabela['global'])
        nova_expr = f'𝛔[{conds}]({nova_expr})'

    # Corrigir projeção
    match_proj = re.match(r'𝝿\[[^\]]+\]\(', algebra.strip())
    if match_proj:
        proj = match_proj.group(0)  # ex: '𝝿[C.Nome, E.CEP, P.Status]('
        return f'{proj}{nova_expr})'
    else:
        return nova_expr





if __name__ == "__main__":
    algebra_relacional = """
    𝝿[C.Nome, E.CEP, P.Status](
       𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
            (
              (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
            ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
       )
    )"""
    
    validar_algebra(algebra_relacional)
    
    algebra_desotimizada = formatar_algebra_relacional(remover_joins(algebra_relacional))
    
    arvore = converter_algebra_em_arvore(algebra_desotimizada)
    
    ArvoreDrawer(arvore).desenhar("arvore_consulta_processada")
    
    exit(0)
    
    print(formatar_algebra_relacional(otimizar_selects(algebra_relacional)))
    
    validar_algebra(formatar_algebra_relacional(otimizar_selects(algebra_relacional)))
    
    print(formatar_algebra_relacional(converter_algebra_em_arvore(otimizar_selects(algebra_relacional)).reconstruir_algebra_relacional()))