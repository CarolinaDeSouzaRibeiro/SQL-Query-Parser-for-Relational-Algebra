# Processamento de Consultas

Este documento descreve o propósito e a funcionalidade do script `processamento_consultas.py`, que é responsável pelo processamento e visualização de árvores de álgebra relacional.

## Propósito e Funcionalidade

O script `processamento_consultas.py` permite:

- Interpretar expressões de álgebra relacional e gerar a árvore de operações relacionais correspondente.
- Visualizar a árvore de operações relacionais utilizando a biblioteca Graphviz.

## Principais Funções e Seus Papéis

### `quebrar_condicoes(condicao: str) -> list[str]`

Divide uma expressão booleana com ∧ em partes isoladas, respeitando parênteses.

- **Parâmetros**:
  - `condicao` (str): String com múltiplas condições booleanas.

- **Retorno**:
  - `list[str]`: Lista de condições individuais.

### `extrair_conteudo_parenteses(s: str, inicio: int) -> tuple[str, int]`

Extrai o conteúdo interno dos parênteses a partir de uma posição inicial.

- **Parâmetros**:
  - `s` (str): String completa.
  - `inicio` (int): Posição do parêntese de abertura.

- **Retorno**:
  - `tuple[str, int]`: Conteúdo interno e posição do fechamento.

### `remover_parenteses_externos(s: str) -> str`

Remove parênteses externos redundantes de uma string.

- **Parâmetros**:
  - `s` (str): Expressão entre parênteses.

- **Retorno**:
  - `str`: Expressão sem os parênteses externos, se aplicável.

### `processar(s: str) -> NoArvore`

Processa uma string de álgebra relacional, preservando a estrutura sintática original, e quebra seleções compostas (com ∧) em nós separados.

- **Parâmetros**:
  - `s` (str): Expressão de álgebra relacional.

- **Retorno**:
  - `NoArvore`: Raiz da árvore de operações.

### `desenhar_arvore(no: NoArvore) -> Digraph`

Gera uma visualização em forma de árvore da consulta processada.

- **Parâmetros**:
  - `no` (NoArvore): Raiz da árvore de operações.

- **Retorno**:
  - `Digraph`: Objeto Graphviz com o grafo desenhado.

### `gerar_imagem_arvore_processada(algebra_relacional: str) -> None`

Processa uma expressão de álgebra relacional e gera sua árvore visual.

- **Parâmetros**:
  - `algebra_relacional` (str): A string da álgebra relacional a ser processada.

- **Retorno**:
  - `None`
