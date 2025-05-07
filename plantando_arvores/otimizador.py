# otimizador.py
from __future__ import annotations
from typing import Set
from .arvore import NoArvore       # já existe no seu projeto
from .processamento_consultas import processar, desenhar_arvore


# --------------------------------------------------------------------------- #
# Funções utilitárias
# --------------------------------------------------------------------------- #

def _aliases_in(cond: str) -> Set[str]:
    """Devolve o conjunto de aliases presentes na condição."""
    out: set[str] = set()
    tok = ''
    for c in cond:
        if c.isalnum() or c == '.':
            tok += c
        else:
            if '.' in tok:
                out.add(tok.split('.')[0])
            tok = ''
    if '.' in tok:
        out.add(tok.split('.')[0])
    return out

def _aliases_subtree(node: NoArvore) -> Set[str]:
    """Coleciona aliases presentes em toda a sub-árvore."""
    if node.operacao.endswith(']'):             # folha "tabela[alias]"
        return {node.operacao.split('[')[-1][:-1]}
    if node.operacao.startswith(('𝛔 ', '𝝿 ')):
        return _aliases_subtree(node.filhos[0])
    if node.operacao in ('X', '⨝'):
        return _aliases_subtree(node.filhos[0]) | _aliases_subtree(node.filhos[1])
    return set()

# --------------------------------------------------------------------------- #
# Passo 1 – empurra seleções (agora agressivo e recursivo)
# --------------------------------------------------------------------------- #
def push_selecoes(node: NoArvore) -> NoArvore:
    """
    Empurra seleções (𝛔) para baixo da árvore o máximo possível.
    Se houver múltiplas seleções empilhadas, separa e empurra cada uma.
    """
    if not node.filhos:
        return node
    node.filhos = [push_selecoes(f) for f in node.filhos]

    # Se não for 𝛔, retorna normalmente
    if not node.operacao.startswith('𝛔 '):
        return node

    # Se houver múltiplas seleções empilhadas, separa-as
    conds = [c.strip() for c in node.operacao[2:].split('∧')]
    if len(conds) > 1:
        # Empilha cada condição como um 𝛔 separado
        sub = node.filhos[0] if len(node.filhos) == 1 else node.filhos
        for cond in reversed(conds):
            new_sigma = NoArvore(f'𝛔 {cond}')
            if isinstance(sub, list):
                new_sigma.filhos = sub
            else:
                new_sigma.adicionar_filho(sub)
            sub = new_sigma
        return push_selecoes(sub)

    # Agora só há uma condição
    cond = conds[0]
    cond_aliases = _aliases_in(cond)

    # nó unário --------------------------------------------------------------
    if len(node.filhos) == 1:
        child = node.filhos[0]
        # atravessa 𝝿 ou 𝛔 para colocá-la mais perto da relação
        if child.operacao.startswith(('𝝿 ', '𝛔 ')):
            node.filhos[0] = child.filhos[0]
            child.filhos[0] = node
            return push_selecoes(child)
        return node

    # nó binário (produto ou junção) -----------------------------------------
    left, right = node.filhos
    aliases_left  = _aliases_subtree(left)
    aliases_right = _aliases_subtree(right)

    # condição cabe só do lado esquerdo?
    if cond_aliases <= aliases_left:
        new_sigma = NoArvore(f'𝛔 {cond}')
        new_sigma.adicionar_filho(left)
        node.filhos[0] = push_selecoes(new_sigma)
        return node.filhos[0]
    # condição cabe só do lado direito?
    if cond_aliases <= aliases_right:
        new_sigma = NoArvore(f'𝛔 {cond}')
        new_sigma.adicionar_filho(right)
        node.filhos[1] = push_selecoes(new_sigma)
        return node.filhos[1]
    # condição usa os dois lados → deixa onde está
    return node

# --------------------------------------------------------------------------- #
# Passo 2 – transforma "𝛔 + X" em ⨝ (agora agressivo e recursivo)
# --------------------------------------------------------------------------- #
def produto_para_join(node: NoArvore) -> NoArvore:
    """
    Converte 𝛔 + X em ⨝ se a condição da seleção referenciar ambos os lados.
    Aplica recursivamente.
    """
    if not node.filhos:
        return node
    node.filhos = [produto_para_join(f) for f in node.filhos]

    # Caso: 𝛔 acima de X
    if node.operacao.startswith('𝛔 ') and len(node.filhos) == 1:
        child = node.filhos[0]
        if child.operacao == 'X':
            cond = node.operacao[2:].strip()
            cond_aliases = _aliases_in(cond)
            left_aliases  = _aliases_subtree(child.filhos[0])
            right_aliases = _aliases_subtree(child.filhos[1])
            # só vira junção se a condição tocar os DOIS lados
            if cond_aliases & left_aliases and cond_aliases & right_aliases:
                join = NoArvore(f'⨝ {cond}')
                join.adicionar_filho(child.filhos[0])
                join.adicionar_filho(child.filhos[1])
                return join
    return node

# --------------------------------------------------------------------------- #
# Passo 3 – push de projeções (opcional, igual ao seu)
# --------------------------------------------------------------------------- #
def push_projecoes(node: NoArvore, needed: Set[str] | None = None) -> NoArvore:
    if needed is None and node.operacao.startswith('𝝿 '):
        needed = {a.strip() for a in node.operacao[2:].split(',')}
        node.filhos[0] = push_projecoes(node.filhos[0], needed)
        return node

    if not node.filhos or needed is None:
        return node

    if node.operacao in ('X', '⨝'):
        left_need  = {a for a in needed if a.split('.')[0] in _aliases_subtree(node.filhos[0])}
        right_need = needed - left_need
        node.filhos[0] = push_projecoes(node.filhos[0], left_need)
        node.filhos[1] = push_projecoes(node.filhos[1], right_need)
    else:
        node.filhos[0] = push_projecoes(node.filhos[0], needed)
    return node

# --------------------------------------------------------------------------- #
# Pipeline de otimização (agora aplica até não mudar mais)
# --------------------------------------------------------------------------- #
def otimizar(root: NoArvore) -> NoArvore:
    """
    Aplica push_selecoes e produto_para_join recursivamente até não haver mais mudanças.
    Garante que todas as seleções são empurradas e todos joins são reconhecidos.
    """
    prev = None
    curr = root
    # Repete até não mudar mais
    while True:
        after_push = push_selecoes(curr)
        after_join = produto_para_join(after_push)
        if repr(after_join) == repr(curr):
            break
        curr = after_join
    # Projeções (opcional, uma vez)
    curr = push_projecoes(curr)
    return curr


#Funcao principal
def gerar_grafo_otimizado(consulta:str):
    arvore_otimiz_inicial = processar(consulta)
    arvore_otim = otimizar(arvore_otimiz_inicial)
    arvore_desenh = desenhar_arvore(arvore_otim)

    arvore_desenh.render('arvore_consulta_otimizada', format='png', cleanup=True)

