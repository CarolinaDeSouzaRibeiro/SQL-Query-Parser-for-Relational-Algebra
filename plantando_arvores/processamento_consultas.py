"""
Este módulo interpreta expressões de álgebra relacional similar à acima e gera a árvore de operações
relacionais correspondente, visualizando-a com a biblioteca Graphviz.
"""

from .arvore import NoArvore
from graphviz import Digraph
from pathlib import Path
import re

NOME_IMAGEM: str = "arvore_consulta_processada"
FORMATO_IMAGEM: str = "png"

def quebrar_condicoes(condicao: str) -> list[str]:
    """
    Divide uma expressão booleana com ∧ em partes isoladas, respeitando parênteses.

    Exemplo:
        "A ∧ (B ∧ C)" → ["A", "(B ∧ C)"]

    Args:
        condicao (str): String com múltiplas condições booleanas.

    Returns:
        list[str]: Lista de condições individuais.
    """
    condicoes: list[str] = []
    buffer: str = ''
    nivel: int = 0
    for c in condicao:
        if c == '(':
            nivel += 1
        elif c == ')':
            nivel -= 1
        if c == '∧' and nivel == 0:
            condicoes.append(buffer)
            buffer = ''
        else:
            buffer += c
    condicoes.append(buffer)
    return condicoes


def extrair_conteudo_parenteses(s: str, inicio: int) -> tuple[str, int]:
    """
    Extrai o conteúdo interno dos parênteses a partir de uma posição inicial.

    Args:
        s (str): String completa.
        inicio (int): Posição do parêntese de abertura.

    Returns:
        tuple[str, int]: Conteúdo interno e posição do fechamento.
    """
    cont: int = 0
    for i in range(inicio, len(s)):
        if s[i] == '(':
            cont += 1
        elif s[i] == ')':
            cont -= 1
        if cont == 0:
            return s[inicio+1:i], i
    raise ValueError("Parênteses não balanceados")


def remover_parenteses_externos(s: str) -> str:
    """
    Remove parênteses externos redundantes de uma string.

    Args:
        s (str): Expressão entre parênteses.

    Returns:
        str: Expressão sem os parênteses externos, se aplicável.
    """
    while s.startswith("(") and s.endswith(")"):
        conteudo: str
        fim: int
        conteudo, fim = extrair_conteudo_parenteses(s, 0)
        if fim == len(s) - 1:
            s = conteudo.strip()
        else:
            break
    return s

def extrair_conteudo_colchetes(s: str, inicio: int) -> tuple[str, int]:
    """
    Extrai o conteúdo interno dos colchetes a partir de uma posição inicial.

    Args:
        s (str): String completa.
        inicio (int): Posição do colchete de abertura.

    Returns:
        tuple[str, int]: Conteúdo interno e posição do fechamento.
    """
    if s[inicio] != '[':
        raise ValueError("Esperado '[' na posição de início")

    cont = 0
    for i in range(inicio, len(s)):
        if s[i] == '[':
            cont += 1
        elif s[i] == ']':
            cont -= 1
        if cont == 0:
            return s[inicio + 1:i], i
    raise ValueError("Colchetes não balanceados")


def processar(s: str) -> NoArvore:
    s = remover_parenteses_externos(''.join(s.strip().splitlines()))

    if s.startswith("𝝿[") or s.startswith("𝛔["):
        operador = "π" if s.startswith("𝝿[") else "σ"
        idx = s.index("](")
        parametro = s[2:idx]
        conteudo, _ = extrair_conteudo_parenteses(s, idx + 1)
        no_sub = processar(conteudo)

        if operador == "σ":
            condicoes = quebrar_condicoes(parametro)
            for cond in reversed(condicoes):
                no = NoArvore(f"σ {cond.strip()}")
                no.adicionar_filho(no_sub)
                no_sub = no
            return no_sub
        else:
            no = NoArvore(f"{operador} {parametro}")
            no.adicionar_filho(no_sub)
            return no

    nivel = 0
    i = 0
    while i < len(s):
        if s[i] == '(':
            nivel += 1
        elif s[i] == ')':
            nivel -= 1
        elif nivel == 0:
            if s[i] == 'X':
                esquerda = s[:i]
                direita = s[i+1:]
                no = NoArvore('×')
                no.adicionar_filho(processar(esquerda.strip()))
                no.adicionar_filho(processar(direita.strip()))
                return no
        elif s[i] == '⨝':
            if i + 1 < len(s) and s[i + 1] == '[':
                # JOIN com condição
                condicao, fim = extrair_conteudo_colchetes(s, i + 1)
                fim += 1  # avança para depois do colchete de fechamento ']'
                esquerda = s[:i].strip()
                direita = remover_parenteses_externos(s[fim:].strip())
                simbolo = f"% {condicao.strip()}"
                print(f"{condicao=}")
            else:
                # JOIN natural
                esquerda = s[:i].strip()
                direita = s[i + 1:].strip()
                simbolo = "%"

            no = NoArvore(simbolo)
            no.adicionar_filho(processar(esquerda))
            no.adicionar_filho(processar(direita))
            return no

        i += 1

    return NoArvore(s)



def desenhar_arvore(no: NoArvore) -> Digraph:
    """
    Gera uma visualização em forma de árvore da consulta processada.

    Args:
        no (NoArvore): Raiz da árvore de operações.

    Returns:
        Digraph: Objeto Graphviz com o grafo desenhado.
    """
    dot: Digraph = Digraph()

    def adicionar_nos(n: NoArvore) -> None:
        dot.node(n.id, n.operacao, shape="box")
        for filho in n.filhos:
            adicionar_nos(filho)
            dot.edge(n.id, filho.id)

    adicionar_nos(no)
    return dot


def gerar_imagem_arvore_processada(
    algebra_relacional: str = "𝝿[E.LNAME](𝛔[(P.PNAME='AQUARIUS')∧(P.PNUMBER=W.PNO)∧(W.ESSN=E.SSN)]((EMPLOYEE[E]⨝WORKS_ON[W])⨝PROJECT[P]))"
) -> None:
    """
    Processa uma expressão de álgebra relacional e gera sua árvore visual.

    A saída é salva como imagem PNG com o nome `arvore_consulta_processada.png`.

    Args:
        algebra_relacional (str): A string da álgebra relacional a ser processada.
    """
    arvore: NoArvore = processar(algebra_relacional)
    grafico: Digraph = desenhar_arvore(arvore)
    grafico.render(NOME_IMAGEM, format=FORMATO_IMAGEM, cleanup=True)
    raiz_do_projeto: Path = Path(__file__).parent.parent
    caminho_imagem: Path = raiz_do_projeto / f"{NOME_IMAGEM}.{FORMATO_IMAGEM}"
    print(f"✅ Álgebra relacional convertida para árvore de consulta com sucesso! A imagem representando-a foi salva em {caminho_imagem}")


# Execução direta (sem necessidade de argumento externo)
if __name__ == '__main__':
    algebra_relacional: str = """
𝝿[C.Nome, E.CEP, P.Status](
   𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
        (
          Cliente[C] ⨝[C.idCliente = P.Cliente_idCliente] Pedido[P]
        ) ⨝[C.idCliente = E.Cliente_idCliente] Endereco[E]
   )
)"""

    gerar_imagem_arvore_processada(algebra_relacional)