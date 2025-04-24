'''
ETAPAS DE OTIMIZAÇÃO

1 - Posicionar as operações de select o mais longe possível da raiz
2 - Redefinir a ordem dos produtos cartesianos para que as tabela com menor quantidade de registros sejam envolvidas nos produtos cartesianos primeiro
3 - Adicionar operações de projeção logo acima das folhas da árvore para excluir as colunas que não serão utilizadas de cada tabela
'''

from .arvore import NoArvore
from .processamento_consultas import desenhar_arvore, processar
from graphviz import Digraph
from pathlib import Path
import re

NOME_IMAGEM: str = "arvore_consulta_otimizada"
FORMATO_IMAGEM: str = "png"

def tabelas_usadas(condicao: str) -> set[str]:
    return set(re.findall(r'\b([A-Z])\.', condicao))

def coletar_tabelas(no: NoArvore) -> set[str]:
    if "[" in no.operacao and "]" in no.operacao:
        match = re.search(r"\[(\w+)\]", no.operacao)
        return {match.group(1)} if match else set()
    tabelas = set()
    for filho in no.filhos:
        tabelas |= coletar_tabelas(filho)
    return tabelas

def empurrar_selecao(condicao: str, no: NoArvore) -> NoArvore:
    tabelas_necessarias = tabelas_usadas(condicao)
    tabelas_subarvore = coletar_tabelas(no)

    if not tabelas_necessarias.issubset(tabelas_subarvore):
        return no

    if len(no.filhos) == 2:
        esquerda, direita = no.filhos
        esquerda_tabelas = coletar_tabelas(esquerda)
        direita_tabelas = coletar_tabelas(direita)

        if tabelas_necessarias.issubset(esquerda_tabelas):
            no.filhos[0] = empurrar_selecao(condicao, esquerda)
            return no
        elif tabelas_necessarias.issubset(direita_tabelas):
            no.filhos[1] = empurrar_selecao(condicao, direita)
            return no

    for i, filho in enumerate(no.filhos):
        no.filhos[i] = empurrar_selecao(condicao, filho)

    novo_no = NoArvore(f"σ {condicao}")
    novo_no.adicionar_filho(no)
    return novo_no

def otimizar_arvore(raiz: NoArvore) -> NoArvore:
    if not raiz.operacao.startswith("π") and not raiz.operacao.startswith("σ"):
        return raiz

    if raiz.operacao.startswith("π"):
        raiz.filhos[0] = otimizar_arvore(raiz.filhos[0])
        return raiz

    selecoes = []
    atual = raiz
    while atual.operacao.startswith("σ") and len(atual.filhos) == 1:
        cond = atual.operacao[2:].strip()
        selecoes.append(cond)
        atual = atual.filhos[0]

    subraiz = otimizar_arvore(atual)

    for cond in selecoes:
        subraiz = empurrar_selecao(cond, subraiz)

    return subraiz


def gerar_imagem_arvore_otimizada(algebra_relacional: str) -> None:
    arvore_processada: NoArvore = processar(algebra_relacional)
    arvore_otimizada: NoArvore = otimizar_arvore(arvore_processada)
    grafico: Digraph = desenhar_arvore(arvore_otimizada)
    raiz_do_projeto: Path = Path(__file__).parent.parent
    caminho_imagem: Path = raiz_do_projeto / f"{NOME_IMAGEM}.{FORMATO_IMAGEM}"
    caminho_imagem_sem_extensao: Path = raiz_do_projeto / f"{NOME_IMAGEM}"
    grafico.render(caminho_imagem_sem_extensao, format=FORMATO_IMAGEM, cleanup=True)
    print(f"✅ Árvore otimizada salva como imagem: {caminho_imagem}")

if __name__ == "__main__": 
    algebra_relacional: str = """
𝝿[C.Nome, E.CEP, P.Status](
   𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP") ∧ (C.idCliente = E.Cliente_idCliente) ∧ (C.idCliente = P.Cliente_idCliente)](
      (Cliente[C] ⨝ Pedido[P]) ⨝ Endereco[E]
   )
)"""

    gerar_imagem_arvore_otimizada(algebra_relacional)