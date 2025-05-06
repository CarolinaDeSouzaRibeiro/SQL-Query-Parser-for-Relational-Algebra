from .arvore import NoArvore, Arvore, ArvoreDrawer

def eh_operador_unario(token: str) -> bool:
    return token.startswith("𝛔[") or token.startswith("𝝿[")

def eh_operador_binario(token: str) -> bool:
    return token.startswith("⨝[") or token == "X"

def extrair_subexpressao(expr: str, inicio: int) -> tuple[str, int]:
    """Extrai a subexpressão entre parênteses e retorna ela com o índice de fim."""
    contador = 1
    fim = inicio + 1
    while fim < len(expr):
        if expr[fim] == '(':
            contador += 1
        elif expr[fim] == ')':
            contador -= 1
            if contador == 0:
                break
        fim += 1
    return expr[inicio+1:fim], fim

def construir_arvore(algebra: str) -> Arvore:
    arvore = Arvore()
    arvore.raiz = _construir_no(algebra.strip())
    return arvore

def _construir_no(expr: str) -> NoArvore:
    expr = expr.strip()

    # Caso mais simples: folha (ex: Cliente[C])
    if not any(op in expr for op in ("𝝿", "𝛔", "⨝", "X")):
        return NoArvore(expr)

    # Projeção ou Seleção: operador unário
    if expr.startswith("𝝿[") or expr.startswith("𝛔["):
        idx_fim_operador = expr.find("]") + 1
        operador = expr[:idx_fim_operador]
        resto = expr[idx_fim_operador:].strip()
        if resto.startswith("("):
            subexpr, _ = extrair_subexpressao(resto, 0)
            no = NoArvore(operador)
            no.filho_esquerda = _construir_no(subexpr)
            return no

    # Junção ou Produto cartesiano: operador binário entre parênteses
    if expr.startswith("("):
        subexpr_esq, fim_esq = extrair_subexpressao(expr, 0)
        resto = expr[fim_esq+1:].strip()

        # Detectar operador central
        if resto.startswith("⨝["):
            idx_fim_op = resto.find("]") + 1
            operador = resto[:idx_fim_op]
            resto_dir = resto[idx_fim_op:].strip()
        elif resto.startswith("X"):
            operador = "X"
            resto_dir = resto[1:].strip()
        else:
            raise ValueError(f"Operador desconhecido em: {resto}")

        if not resto_dir.startswith("("):
            raise ValueError(f"Expressão da direita inválida: {resto_dir}")
        
        subexpr_dir, _ = extrair_subexpressao(resto_dir, 0)
        no = NoArvore(operador)
        no.filho_esquerda = _construir_no(subexpr_esq)
        no.filho_direita = _construir_no(subexpr_dir)
        return no

    raise ValueError(f"Expressão inválida: {expr}")

if __name__ == "__main__":
    expr = '''𝝿[C.Nome, E.CEP, P.Status](
       𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
            (
              (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
            ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
       )
    )'''

    arv = construir_arvore(expr)
    print(arv.reconstruir_algebra_relacional())
    desenhista: ArvoreDrawer = ArvoreDrawer(arv)
    desenhista.desenhar("arvore")
    print("Árvore desenhada e salva como 'arvore.png'.")
    