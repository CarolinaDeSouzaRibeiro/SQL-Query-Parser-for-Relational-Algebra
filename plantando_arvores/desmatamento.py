from .arvore import NoArvore

def reconstruir_algebra(no: NoArvore) -> str:
    """
    Reconstrói a string de álgebra relacional a partir da árvore de operações.

    Args:
        no (NoArvore): Nó raiz da árvore.

    Returns:
        str: Expressão de álgebra relacional equivalente.
    """
    op: str = no.operacao.strip()

    if op.startswith("π "):  # Projeção
        return f"𝝿[{op[2:]}]({reconstruir_algebra(no.filhos[0])})"

    elif op.startswith("σ "):  # Seleção
        condicoes = [op[2:]]
        filho = no.filhos[0]
        while filho.operacao.startswith("σ "):  # Agrupar condições se houver várias seleções aninhadas
            condicoes.append(filho.operacao[2:])
            filho = filho.filhos[0]
        condicoes_str = " ∧ ".join(condicoes)
        return f"𝛔[{condicoes_str}]({reconstruir_algebra(filho)})"

    elif op == "X":  # Junção ou produto cartesiano
        return f"({') ⨝ ('.join(reconstruir_algebra(f) for f in no.filhos)})"

    else:  # Caso base: nome da tabela
        return op

if __name__ == "__main__":
    from .processamento_consultas import processar
    
    algebra_relacional: str = """
    𝝿[E.LNAME](
        𝛔[(P.PNAME='AQUARIUS') ∧ (P.PNUMBER=W.PNO) ∧ (W.ESSN=E.SSN)](
            (EMPLOYEE[E] ⨝ WORKS_ON[W]) ⨝ PROJECT[P]
        )
    )
    """
    arvore: NoArvore = processar(algebra_relacional)
    algebra_recuperada: str = reconstruir_algebra(arvore)
    print(algebra_recuperada)
