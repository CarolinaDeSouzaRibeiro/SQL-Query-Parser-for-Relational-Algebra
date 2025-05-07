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
    if node.operacao.startswith(('σ ', 'π ')):
        return _aliases_subtree(node.filhos[0])
    if node.operacao in ('X', '⨝'):
        return _aliases_subtree(node.filhos[0]) | _aliases_subtree(node.filhos[1])
    return set()

# --------------------------------------------------------------------------- #
# Passo 1 – empurra seleções
# --------------------------------------------------------------------------- #
def push_selecoes(node: NoArvore) -> NoArvore:
    if not node.filhos:
        return node

    node.filhos = [push_selecoes(f) for f in node.filhos]

    if not node.operacao.startswith('σ '):
        return node

    cond = node.operacao[2:].strip()
    cond_aliases = _aliases_in(cond)

    # nó unário --------------------------------------------------------------
    if len(node.filhos) == 1:
        child = node.filhos[0]
        # atravessa π ou σ para colocá-la mais perto da relação
        if child.operacao.startswith(('π ', 'σ ')):
            node.filhos[0] = child.filhos[0]
            child.filhos[0] = node
            return child
        return node

    # nó binário (produto ou junção) -----------------------------------------
    left, right = node.filhos
    aliases_left  = _aliases_subtree(left)
    aliases_right = _aliases_subtree(right)

    # condição cabe só do lado esquerdo?
    if cond_aliases <= aliases_left:
        # cria novo σ como pai do ramo esquerdo
        new_sigma = NoArvore(node.operacao)
        new_sigma.adicionar_filho(left)
        node.filhos[0] = push_selecoes(new_sigma)
        return node.filhos[0]             # sobe o σ
    # condição cabe só do lado direito?
    if cond_aliases <= aliases_right:
        new_sigma = NoArvore(node.operacao)
        new_sigma.adicionar_filho(right)
        node.filhos[1] = push_selecoes(new_sigma)
        return node.filhos[1]
    # condição usa os dois lados → deixa onde está
    return node

# --------------------------------------------------------------------------- #
# Passo 2 – transforma “σ + X” em ⨝
# --------------------------------------------------------------------------- #
def produto_para_join(node: NoArvore) -> NoArvore:
    if not node.filhos:
        return node
    node.filhos = [produto_para_join(f) for f in node.filhos]

    if node.operacao.startswith('σ ') and len(node.filhos) == 1:
        child = node.filhos[0]
        if child.operacao == 'X':
            cond = node.operacao[2:].strip()
            cond_aliases = _aliases_in(cond)
            left_aliases  = _aliases_subtree(child.filhos[0])
            right_aliases = _aliases_subtree(child.filhos[1])

            # só vira junção se a condição tocar os DOIS lados
            if cond_aliases & left_aliases and cond_aliases & right_aliases:
                child.operacao = f"⨝ {cond}"
                return child          # σ absorvido
    return node

# --------------------------------------------------------------------------- #
# Passo 3 – push de projeções (opcional)
# --------------------------------------------------------------------------- #
def push_projecoes(node: NoArvore, needed: Set[str] | None = None) -> NoArvore:
    if needed is None and node.operacao.startswith('π '):
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
# Pipeline de otimização
# --------------------------------------------------------------------------- #
def otimizar(root: NoArvore) -> NoArvore:
    stage1 = push_selecoes(root)
    stage2 = produto_para_join(stage1)
    stage3 = push_projecoes(stage2)
    return stage3


#Funcao principal
def gerar_grafo_otimizado(consulta:str):
    arvore_otimiz_inicial = processar(consulta)
    arvore_otim = otimizar(arvore_otimiz_inicial)
    arvore_desenh = desenhar_arvore(arvore_otim)

    arvore_desenh.render('arvore_consulta_otimizada', format='png', cleanup=True)

