from typing import TypeAlias

class NoArvore:
    """
    Representa um nó na árvore de operações de álgebra relacional.

    Attributes:
        operacao (str): O operador ou conteúdo do nó (por exemplo, σ condição, π atributos, nome da tabela).
        filhos (list[NoArvore]): Lista de filhos do nó atual.
        id (str): Identificador único para uso no grafo visual.
    """
    _arvore: TypeAlias = dict[str, dict[str, str|list[str]]]
    
    id_counter: int = 0  # Contador estático para criar IDs únicos
 
    def __init__(self, operacao: str) -> None:
        self.operacao: str = operacao
        self.filhos: list["NoArvore"] = []
        self.id: str = f'node{NoArvore.id_counter}'
        NoArvore.id_counter += 1

    def adicionar_filho(self, filho: "NoArvore") -> None:
        """
        Adiciona um filho ao nó atual.
        """
        self.filhos.append(filho)
        
    def get_arvore(self) -> _arvore:
        """
        Retorna um dicionário representando a árvore a partir deste nó.
        A chave é o ID de cada nó e o valor é um dicionário com os atributos.
        """
        arvore = {}

        def visitar(no: "NoArvore"):
            if no.id not in arvore:
                arvore[no.id] = {
                    "operacao": no.operacao,
                    "filhos": [filho.id for filho in no.filhos]
                }
                for filho in no.filhos:
                    visitar(filho)

        visitar(self)
        return arvore