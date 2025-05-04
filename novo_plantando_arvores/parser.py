from .arvore import NoArvore, Arvore, ArvoreDrawer
import re
from typing import NoReturn, Tuple
from banco_de_dados.definicao_banco.tabelas import tabelas

def formatar_algebra_relacional(algebra: str) -> str:
    algebra = re.sub(r'\s+', ' ', algebra)
    algebra = re.sub(r'\(\s+', '(', algebra)
    algebra = re.sub(r'\s+\)', ')', algebra)
    algebra = re.sub(r'\[\s+', '[', algebra)
    algebra = re.sub(r'\s+\]', ']', algebra)
    return algebra

def converter_algebra_em_arvore(algebra: str) -> Arvore:
    validar_algebra(algebra)
    algebra_formatada = formatar_algebra_relacional(algebra)
    tokens = list(algebra_formatada)
    raiz, _ = _parse(tokens)
    arvore = Arvore()
    arvore.raiz = raiz
    return arvore

def _parse(tokens: list[str], pos: int = 0) -> Tuple[NoArvore, int]:
    if tokens[pos] == '(':
        pos += 1
        esquerda, pos = _parse(tokens, pos)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1

        if pos < len(tokens):
            if tokens[pos] == ' ':
                pos += 1

            if tokens[pos] == 'X':
                pos += 1
                if tokens[pos] == '(':
                    pos += 1
                direita, pos = _parse(tokens, pos)
                if tokens[pos] == ')':
                    pos += 1
                raiz = NoArvore('X')
                raiz.filho_esquerda = esquerda
                raiz.filho_direita = direita
                return raiz, pos

            elif tokens[pos] == '⨝':
                pos += 1
                if tokens[pos] == '[':
                    condicao, pos = _read_until_balanced(tokens, '[', ']', pos + 1)
                    if tokens[pos] == ')':
                        pos += 1
                    if tokens[pos] == '(':
                        pos += 1
                    direita, pos = _parse(tokens, pos)
                    if tokens[pos] == ')':
                        pos += 1
                    raiz = NoArvore(f"⨝[{condicao}]")
                    raiz.filho_esquerda = esquerda
                    raiz.filho_direita = direita
                    return raiz, pos

        return esquerda, pos

    conteudo = ""
    while pos < len(tokens) and tokens[pos] not in ('(', ')'):
        if tokens[pos] == '[':
            conteudo += tokens[pos]
            pos += 1
            bloco, pos = _read_until_balanced(tokens, '[', ']', pos)
            conteudo += bloco + ']'
        else:
            conteudo += tokens[pos]
            pos += 1

    no = NoArvore(conteudo.strip())
    
    # print(f"DEBUG: criando nó '{no.conteudo}'")

    if pos < len(tokens) and tokens[pos] == '(':
        pos += 1
        no.filho_esquerda, pos = _parse(tokens, pos)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1
            
    # Elimina nós intermediários vazios, criados apenas por parênteses desnecessários
    if no.conteudo == "" and no.filho_esquerda and no.filho_direita is None:
        return no.filho_esquerda, pos


    return no, pos

def _read_until_balanced(tokens: list[str], open_char: str, close_char: str, start_pos: int) -> Tuple[str, int]:
    count = 1
    result = ""
    i = start_pos
    while i < len(tokens) and count > 0:
        char = tokens[i]
        if char == open_char:
            count += 1
        elif char == close_char:
            count -= 1
        if count > 0:
            result += char
        i += 1
    return result, i

def validar_algebra(algebra: str) -> None | NoReturn:
    algebra_formatada = formatar_algebra_relacional(algebra)
    tokens = list(algebra_formatada)
    _verificar_balanceamento(tokens)
    _verificar_operadores_unarios(algebra_formatada)
    _verificar_joins(algebra_formatada)
    _verificar_produto_cartesiano(algebra_formatada)

def _verificar_balanceamento(tokens: list[str]) -> None | NoReturn:
    pilha = []
    for i, char in enumerate(tokens):
        if char in ('(', '['):
            pilha.append(char)
        elif char == ')':
            if not pilha or pilha[-1] != '(':
                raise ValueError(f"Parêntese fechado ')' sem abertura correspondente na posição {i}")
            pilha.pop()
        elif char == ']':
            if not pilha or pilha[-1] != '[':
                raise ValueError(f"Colchete fechado ']' sem abertura correspondente na posição {i}")
            pilha.pop()
    if pilha:
        raise ValueError(f"Delimitadores não balanceados: {pilha}")

def _verificar_operadores_unarios(algebra_formatada: str) -> None | NoReturn:
    matches = re.findall(r'(𝝿|𝛔)\[[^\[\]]+\]\(', algebra_formatada)
    if not matches:
        if '𝝿' in algebra_formatada or '𝛔' in algebra_formatada:
            raise ValueError("Operador unário encontrado, mas está malformado. Esperado: '𝝿[...](...)' ou '𝛔[...](...)'")

def _verificar_joins(algebra_formatada: str) -> None | NoReturn:
    if '⨝' in algebra_formatada:
        if not re.search(r'\)\s*⨝\[[^\[\]]+\]\s*\(', algebra_formatada):
            raise ValueError("Join malformado. Esperado: (expr) ⨝[cond] (expr)")

def _verificar_produto_cartesiano(algebra_formatada: str) -> None | NoReturn:
    if 'X' in algebra_formatada:
        if not re.search(r'\)\s*X\s*\(', algebra_formatada):
            raise ValueError("Produto cartesiano malformado. Esperado: (expr) X (expr)")
        
if __name__ == '__main__':
    algebra_relacional = """
    𝝿[C.Nome, E.CEP, P.Status](
       𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
            (
              (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
            ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
       )
    )"""

    print(formatar_algebra_relacional(algebra_relacional))
    
    arvore = converter_algebra_em_arvore(algebra_relacional)
    
    print(formatar_algebra_relacional(arvore.reconstruir_algebra_relacional()))

    drawer: ArvoreDrawer = ArvoreDrawer(arvore)
    
    drawer.desenhar("teste_processamento")