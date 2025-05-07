# otimizador.py
from __future__ import annotations
from typing import Tuple, Set
from .arvore import NoArvore
from .processamento_consultas import processar, desenhar_arvore

# caracteres que identificam atributos:  <alias>.<atributo>
def _atributos(expr: str) -> Set[str]:
    return {tok.strip() for tok in expr.replace('(', ' ').replace(')', ' ').replace('=', ' ').split()
            if '.' in tok}

# Passo 1 ──────────────────────────────────────────────────────────────────────
def push_selecoes(no: NoArvore) -> NoArvore:
    if not no.filhos:
        return no  # folha

    # otimiza filhos primeiro
    no.filhos = [push_selecoes(f) for f in no.filhos]

    if no.operacao.startswith("σ "):
        cond = no.operacao[2:].strip()
        cond_atrs = _atributos(cond)

        # caso unário
        if len(no.filhos) == 1:
            filho = no.filhos[0]
            if filho.operacao.startswith("σ ") or filho.operacao.startswith("π "):
                # passa por cima de σ/π unários
                no.filhos[0] = filho.filhos[0]
                filho.filhos[0] = no
                return filho
            return no

        # caso binário (produto ou junção)
        esq, dir_ = no.filhos
        atrs_esq = _atributos_subarvore(esq)
        atrs_dir = _atributos_subarvore(dir_)

        # condição usa somente atributos do lado esquerdo?
        if cond_atrs <= atrs_esq:
            # empurra p/ esquerda
            no.filhos = [push_selecoes(NoArvore(no.operacao).tap(lambda n: n.adicionar_filho(esq))), dir_]  # type: ignore
            return no.filhos[0]  # nova raiz é esse σ
        # somente do lado direito?
        elif cond_atrs <= atrs_dir:
            no.filhos = [esq, push_selecoes(NoArvore(no.operacao).tap(lambda n: n.adicionar_filho(dir_)))]  # type: ignore
            return no.filhos[1]
    return no

def _atributos_subarvore(no: NoArvore) -> Set[str]:
    """Coleta rapidamente todos os aliases presentes na subárvore."""
    if no.operacao.endswith(']'):                    # folha: "tabela[alias]"
        alias = no.operacao.split('[')[-1][:-1]
        return {alias}
    if no.operacao.startswith(('σ ', 'π ')):
        return _atributos_subarvore(no.filhos[0])
    if no.operacao in ('X', '⨝'):
        return _atributos_subarvore(no.filhos[0]) | _atributos_subarvore(no.filhos[1])
    return set()

# Passo 2 ──────────────────────────────────────────────────────────────────────
def produto_para_join(no: NoArvore) -> NoArvore:
    if not no.filhos:
        return no
    no.filhos = [produto_para_join(f) for f in no.filhos]

    # procura padrão σ(cond) -> X
    if no.operacao.startswith("σ ") and len(no.filhos) == 1:
        filho = no.filhos[0]
        if filho.operacao == 'X':
            cond = no.operacao[2:].strip()
            # converte: troca rótulo do filho e “puxa” cond para ele
            filho.operacao = f"⨝ {cond}"
            return filho  # elimina o σ separado
    return no

# Passo 3 ──────────────────────────────────────────────────────────────────────
def push_projecoes(no: NoArvore, needed: Set[str] | None = None) -> NoArvore:
    """
    Percorre recursivamente mantendo apenas colunas realmente necessárias.
    `needed` começa com o conjunto de atributos pedidos pela projeção raiz.
    """
    if needed is None and no.operacao.startswith("π "):
        needed = set(attr.strip() for attr in no.operacao[2:].split(','))
        # continua descendo sem alterar essa projeção por enquanto
        no.filhos[0] = push_projecoes(no.filhos[0], needed)
        return no

    if not no.filhos or needed is None:
        return no

    if no.operacao in ('X', '⨝'):
        esq_needed = {a for a in needed if a.split('.')[0] in _atributos_subarvore(no.filhos[0])}
        dir_needed = needed - esq_needed
        no.filhos[0] = push_projecoes(no.filhos[0], esq_needed)
        no.filhos[1] = push_projecoes(no.filhos[1], dir_needed)
    else:  # σ ou π intermed.
        no.filhos[0] = push_projecoes(no.filhos[0], needed)
    return no

# Função otimizar ─────────────────────────────────────────────────────────────
def otimizar(raiz: NoArvore) -> NoArvore:
    r1 = push_selecoes(raiz)
    r2 = produto_para_join(r1)
    r3 = push_projecoes(r2)
    return r3


#Funcao principal
def gerar_grafo_otimizado(consulta:str):
    arvore_otimiz_inicial = processar(consulta)
    arvore_otim = otimizar(arvore_otimiz_inicial)
    arvore_desenh = desenhar_arvore(arvore_otim)

    arvore_desenh.render('arvore_consulta_otimizada', format='png', cleanup=True)



# helper “tap” para Python < 3.12
def _tap(self, f): f(self); return self
setattr(NoArvore, 'tap', _tap)
