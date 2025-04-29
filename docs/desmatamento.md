# Reconstrução de Álgebra Relacional

Este documento descreve o propósito e a funcionalidade do script `desmatamento.py`, que é responsável pela reconstrução de álgebra relacional a partir da árvore de operações.

## Propósito e Funcionalidade

O script `desmatamento.py` permite:

- Reconstruir a string de álgebra relacional a partir da árvore de operações.
- Utilizar a estrutura de nós da árvore para gerar a expressão de álgebra relacional equivalente.

## Principais Funções e Seus Papéis

### `reconstruir_algebra(no: NoArvore) -> str`

Reconstrói a string de álgebra relacional a partir da árvore de operações.

- **Parâmetros**:
  - `no` (NoArvore): Nó raiz da árvore.

- **Retorno**:
  - `str`: Expressão de álgebra relacional equivalente.

### `if __name__ == "__main__":`

Ponto de entrada principal: executa a função `reconstruir_algebra` quando o script é chamado diretamente.
