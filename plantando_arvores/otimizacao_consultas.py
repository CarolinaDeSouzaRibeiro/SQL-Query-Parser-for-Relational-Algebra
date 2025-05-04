'''
ETAPAS DE OTIMIZAÇÃO

1 - Posicionar as operações de select o mais longe possível da raiz
2 - Redefinir a ordem dos produtos cartesianos para que as tabela com menor quantidade de registros sejam envolvidas nos produtos cartesianos primeiro
3 - Adicionar operações de projeção logo acima das folhas da árvore para excluir as colunas que não serão utilizadas de cada tabela
'''

import re

def desotimizar_algebra(algebra_relacional: str) -> str:
    '''Modificação da álgebra relacional para substituir joins por seleções sobre produtos cartesianos,
    garantindo parênteses corretos nas condições.'''

    # Encontrar todas as condições de join
    condicoes_join = re.findall(r'⨝\[(.*?)\]', algebra_relacional, flags=re.DOTALL)
    
    # Remover todos os ⨝[...] e substituir por ×
    algebra_sem_joins = re.sub(r'⨝\[.*?\]', '×', algebra_relacional)
    
    # Pegar as condições de seleção já existentes
    selecao_existente = re.search(r'𝛔\[(.*?)\]', algebra_sem_joins, flags=re.DOTALL)

    if selecao_existente:
        condicao_existente = selecao_existente.group(1)
        # Separar as condições existentes
        condicoes_existentes = re.split(r'(?<![<>=])∧(?![<>=])', condicao_existente)
        condicoes_existentes = [c.strip() for c in condicoes_existentes if c.strip()]
    else:
        condicoes_existentes = []

    # Condições dos joins
    condicoes_joins = [c.strip() for c in condicoes_join if c.strip()]
    
    # Junta todas as condições
    todas_condicoes = condicoes_existentes + condicoes_joins

    # Adiciona parênteses só se ainda não houver
    def garantir_parenteses(cond):
        cond = cond.strip()
        if not (cond.startswith('(') and cond.endswith(')')):
            return f'({cond})'
        return cond

    todas_condicoes_parentesis = [garantir_parenteses(c) for c in todas_condicoes]
    condicao_final = ' ∧ '.join(todas_condicoes_parentesis)

    # Substitui a seleção antiga ou cria nova
    if selecao_existente:
        algebra_final = re.sub(r'𝛔\[.*?\]', f'𝛔[{condicao_final}]', algebra_sem_joins, flags=re.DOTALL)
    else:
        algebra_final = f'𝛔[{condicao_final}]({algebra_sem_joins})'
        
    # Remove quebras de linha e espaços desnecessários entre parênteses
    algebra_final = re.sub(r'\s+', ' ', algebra_final)  # primeiro, reduz tudo para um espaço
    algebra_final = re.sub(r'\(\s+', '(', algebra_final)  # tira espaço depois de (
    algebra_final = re.sub(r'\s+\)', ')', algebra_final)  # tira espaço antes de )
    algebra_final = re.sub(r'\[\s+', '[', algebra_final)  # tira espaço depois de [
    algebra_final = re.sub(r'\s+\]', ']', algebra_final)  # tira espaço antes de ]
    
    return algebra_final

def otimizacao_selects(algebra_relacional: str) -> str:
    '''Otimiza a álgebra relacional para que as operações de select ocorram o mais 
    longe possível da raiz da árvore de consultas. Ou seja, os selects ocorrem o quanto antes logo após as 
    tabelas das quais dependem sejam agrupadas por um produto cartesiano'''

if __name__ == "__main__": 
    algebra_relacional: str = """
𝝿[C.Nome, E.CEP, P.Status](
   𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
        (
          Cliente[C] ⨝[C.idCliente = P.Cliente_idCliente] Pedido[P]
        ) ⨝[C.idCliente = E.Cliente_idCliente] Endereco[E]
   )
)"""

    print(desotimizar_algebra(algebra_relacional))