from __future__ import annotations
from typing import Optional, NoReturn
from graphviz import Digraph
from pathlib import Path

class NoArvore:
    def __init__(self, conteudo: str):
        self.conteudo: str = conteudo
        self.filho_esquerda: Optional[NoArvore] = None
        self.filho_direita: Optional[NoArvore] = None

class Arvore:
    def __init__(self):
        self.raiz: Optional[NoArvore] = None

    def reconstruir_algebra_relacional(self) -> Optional[str]:
        if self.raiz is None:
            return None
        return self._percorrer(self.raiz)

    def _percorrer(self, no: NoArvore, nivel: int = 0) -> str:
        indent = "   " * nivel

        # Caso folha: sem filhos => só imprime conteúdo
        if no.filho_esquerda is None and no.filho_direita is None:
            return f"{indent}{no.conteudo}\n"

        # Combinar seletores
        if self._is_select(no) and self._is_select(no.filho_esquerda):
            return self._combinar_selects(no, nivel)

        # Joins e produtos cartesianos
        if self._is_join(no):
            return self._renderizar_join(no, nivel)
        if self._is_produto_cartesiano(no):
            return self._renderizar_produto_cartesiano(no, nivel)

        # Caso geral com filhos
        expressao = f"{indent}{no.conteudo}(\n"
        if no.filho_esquerda:
            expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        if no.filho_direita:
            expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _is_select(self, no: Optional[NoArvore]) -> bool:
        return no is not None and no.conteudo.startswith("𝛔[")

    def _is_join(self, no: Optional[NoArvore]) -> bool:
        return no is not None and no.conteudo.startswith("⨝[")

    def _is_produto_cartesiano(self, no: Optional[NoArvore]) -> bool:
        return no is not None and no.conteudo.strip() == "X"

    def _extrair_condicao(self, conteudo: str) -> str:
        return conteudo[2:-1]  # remove '𝛔[' e ']'

    def _combinar_selects(self, no: NoArvore, nivel: int) -> str:
        indent = "   " * nivel
        cond1 = self._extrair_condicao(no.conteudo)
        filho = no.filho_esquerda
        cond2 = self._extrair_condicao(filho.conteudo)

        combinada = f"({cond1}) ^ ({cond2})"
        novo_no = filho.filho_esquerda

        if self._is_select(novo_no):
            novo_combinado = NoArvore(f"𝛔[{combinada}]")
            novo_combinado.filho_esquerda = novo_no
            return self._percorrer(novo_combinado, nivel)

        expressao = f"{indent}𝛔[{combinada}](\n"
        if novo_no:
            expressao += self._percorrer(novo_no, nivel + 1)
        if filho.filho_direita:
            expressao += self._percorrer(filho.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _renderizar_join(self, no: NoArvore, nivel: int) -> str:
        indent = "   " * nivel
        condicao = no.conteudo
        expressao = f"{indent}(\n"
        expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        expressao += f"{indent}) {condicao} (\n"
        expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _renderizar_produto_cartesiano(self, no: NoArvore, nivel: int) -> str:
        indent = "   " * nivel
        expressao = f"{indent}(\n"
        expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        expressao += f"{indent}) X (\n"
        expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

class ArvoreDrawer:
    
    DIRETORIO_IMAGEM: Path = Path.cwd() / "img"
    FORMATO_IMAGEM: str = "png"
    
    def __init__(self, arvore: Arvore):
        self.arvore = arvore
        self.dot = Digraph(format=self.FORMATO_IMAGEM)
        self.node_count = 0  # contador para criar identificadores únicos

    def desenhar(self, nome_imagem: str) -> None | NoReturn:
        if not self.arvore.raiz:
            raise ValueError("A árvore está vazia.")
        
        self.DIRETORIO_IMAGEM.mkdir(parents=True, exist_ok=True)
        
        self.node_count = 0
        
        self._desenhar_no(self.arvore.raiz)
        
        self.dot.render(filename=(self.DIRETORIO_IMAGEM / nome_imagem), cleanup=True)
        
        print(f"✅ Árvore desenhada com sucesso em: {self.DIRETORIO_IMAGEM / nome_imagem}.{self.FORMATO_IMAGEM}")

    def _desenhar_no(self, no: NoArvore) -> str:
        id_atual = f"node{self.node_count}"
        self.node_count += 1

        # Substituição de símbolos incompatíveis
        conteudo_legivel = (
            no.conteudo
            .replace("𝝿", "π")     # projeção
            .replace("𝛔", "σ")     # seleção
            .replace("⨝", "X")     # inner join, convertendo para o mesmo símbolo do produto cartesiano
        )

        # Adiciona o nó ao gráfico
        self.dot.node(id_atual, label=conteudo_legivel)

        # Conecta filhos, se existirem
        if no.filho_esquerda:
            id_esq = self._desenhar_no(no.filho_esquerda)
            self.dot.edge(id_atual, id_esq)

        if no.filho_direita:
            id_dir = self._desenhar_no(no.filho_direita)
            self.dot.edge(id_atual, id_dir)

        return id_atual


    
if __name__ == "__main__":
    '''
𝝿[C.Nome, E.CEP, P.Status](
   𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
        (
          Cliente[C] ⨝[C.idCliente = P.Cliente_idCliente] Pedido[P]
        ) ⨝[C.idCliente = E.Cliente_idCliente] Endereco[E]
   )
)
    '''
    
    arvore = Arvore()
    
    arvore.raiz = NoArvore("𝝿[C.Nome, E.CEP, P.Status]")
    
    arvore.raiz.filho_esquerda = NoArvore("𝛔[C.TipoCliente = 4]")
    
    arvore.raiz.filho_esquerda.filho_esquerda = NoArvore("𝛔[E.UF = \"SP\"]")
    
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("⨝[C.idCliente = E.Cliente_idCliente]")
    
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("⨝[C.idCliente = P.Cliente_idCliente]")
    
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("Cliente[C]")
    
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda.filho_direita = NoArvore("Pedido[P]")
    
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_direita = NoArvore("Endereco[E]")
    
    print(arvore.reconstruir_algebra_relacional())
    
    drawer: ArvoreDrawer = ArvoreDrawer(arvore)
    
    drawer.desenhar()