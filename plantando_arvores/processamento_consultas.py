"""
𝝿[E.LNAME](
   𝛔[(P.PNAME='AQUARIUS') ∧ (P.PNUMBER=W.PNO) ∧ (W.ESSN=E.SSN)](
      (EMPLOYEE[E] ⨝ WORKS_ON[W]) ⨝ PROJECT[P]
   )
)

Este módulo interpreta expressões de álgebra relacional similar à acima e gera a árvore de operações
relacionais correspondente, visualizando-a com a biblioteca Graphviz.
"""

from .arvore import NoArvore
from graphviz import Digraph
from pathlib import Path

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


def processar(s: str) -> NoArvore:
    """
    Processa recursivamente a string de álgebra relacional, retornando a árvore sintática correspondente.

    Args:
        s (str): Expressão de álgebra relacional.

    Returns:
        NoArvore: Raiz da árvore de operações.
    """
    s = remover_parenteses_externos(''.join(s.strip().splitlines()))

    if s.startswith("𝝿["):  # Projeção
        idx: int = s.index("](")
        proj: str = "π " + s[2:idx]
        conteudo, _ = extrair_conteudo_parenteses(s, idx + 1)
        no: NoArvore = NoArvore(proj)
        no.adicionar_filho(processar(conteudo))
        return no

    elif s.startswith("𝛔["):  # Seleção
        idx: int = s.index("](")
        condicoes_brutas: str = s[2:idx]
        condicoes: list[str] = quebrar_condicoes(condicoes_brutas)
        conteudo, _ = extrair_conteudo_parenteses(s, idx + 1)
        no_atual: NoArvore = processar(conteudo)
        # Aplica cada condição de seleção como um nó separado, da mais interna à mais externa
        for cond in reversed(condicoes):
            no_cond: NoArvore = NoArvore(f"σ {cond}")
            no_cond.adicionar_filho(no_atual)
            no_atual = no_cond
        return no_atual

    elif "⨝" in s or "X" in s:  # Junção natural ou produto cartesiano
        partes: list[str] = []
        nivel: int = 0
        inicio: int = 0
        i: int = 0
        while i < len(s):
            if s[i] == '(':
                nivel += 1
            elif s[i] == ')':
                nivel -= 1
            elif s[i:i+1] in ("⨝", "X") and nivel == 0:
                partes.append(s[inicio:i])
                inicio = i + 1
            i += 1
        partes.append(s[inicio:])

        if len(partes) < 2:
            raise ValueError(f"Erro ao processar junção: não foi possível dividir corretamente a string: {s}")

        filhos: list[NoArvore] = [processar(p) for p in partes]
        no: NoArvore = NoArvore("X")  # Nome genérico para junção
        for f in filhos:
            no.adicionar_filho(f)
        return no

    else:  # Caso base: nome de uma tabela
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
𝝿[E.LNAME](
   𝛔[(P.PNAME='AQUARIUS') ∧ (P.PNUMBER=W.PNO) ∧ (W.ESSN=E.SSN)](
      (EMPLOYEE[E] ⨝ WORKS_ON[W]) ⨝ PROJECT[P]
   )
)
"""
    gerar_imagem_arvore_processada(algebra_relacional)