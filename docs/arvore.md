# Estrutura de Dados de Árvore

Este documento descreve o propósito e a funcionalidade do script `arvore.py`, que é responsável pela definição da estrutura de nós da árvore de operações de álgebra relacional.

## Propósito e Funcionalidade

O script `arvore.py` permite:

- Definir a estrutura de nós da árvore de operações de álgebra relacional.
- Adicionar filhos a um nó existente.
- Obter a representação da árvore a partir de um nó específico.

## Principais Funções e Seus Papéis

### `class NoArvore`

Representa um nó na árvore de operações de álgebra relacional.

- **Atributos**:
  - `operacao` (str): O operador ou conteúdo do nó (por exemplo, σ condição, π atributos, nome da tabela).
  - `filhos` (list[NoArvore]): Lista de filhos do nó atual.
  - `id` (str): Identificador único para uso no grafo visual.

### `adicionar_filho(self, filho: "NoArvore") -> None`

Adiciona um filho ao nó atual.

- **Parâmetros**:
  - `filho` (NoArvore): O nó filho a ser adicionado.

### `get_arvore(self) -> dict`

Retorna um dicionário representando a árvore a partir deste nó.

- **Retorno**:
  - `dict`: Dicionário onde a chave é o ID de cada nó e o valor é um dicionário com os atributos.
