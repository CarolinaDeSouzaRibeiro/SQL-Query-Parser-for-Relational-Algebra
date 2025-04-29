# Otimização de Consultas

Este documento descreve o propósito e a funcionalidade do script `otimizacao_consultas.py`, que é responsável pela otimização de consultas SQL e geração de árvores de álgebra relacional otimizadas.

## Propósito e Funcionalidade

O script `otimizacao_consultas.py` permite:

- Otimizar consultas SQL aplicando técnicas de álgebra relacional.
- Gerar árvores de álgebra relacional otimizadas.
- Visualizar as árvores otimizadas utilizando a biblioteca Graphviz.

## Principais Funções e Seus Papéis

### `tabelas_usadas(condicao: str) -> set[str]`

Extrai as tabelas usadas em uma condição.

- **Parâmetros**:
  - `condicao` (str): Condição a ser analisada.

- **Retorno**:
  - `set[str]`: Conjunto de tabelas usadas na condição.

### `coletar_tabelas(no: NoArvore) -> set[str]`

Coleta todas as tabelas usadas em uma subárvore.

- **Parâmetros**:
  - `no` (NoArvore): Nó raiz da subárvore.

- **Retorno**:
  - `set[str]`: Conjunto de tabelas usadas na subárvore.

### `empurrar_selecao(condicao: str, no: NoArvore) -> NoArvore`

Empurra uma operação de seleção o mais próximo possível das folhas da árvore.

- **Parâmetros**:
  - `condicao` (str): Condição de seleção.
  - `no` (NoArvore): Nó raiz da subárvore.

- **Retorno**:
  - `NoArvore`: Subárvore com a seleção empurrada.

### `otimizar_arvore(raiz: NoArvore) -> NoArvore`

Otimiza a árvore de álgebra relacional aplicando técnicas de empurrar seleções e reordenar produtos cartesianos.

- **Parâmetros**:
  - `raiz` (NoArvore): Nó raiz da árvore.

- **Retorno**:
  - `NoArvore`: Árvore otimizada.

### `gerar_imagem_arvore_otimizada(algebra_relacional: str) -> None`

Gera uma imagem da árvore de álgebra relacional otimizada.

- **Parâmetros**:
  - `algebra_relacional` (str): Expressão de álgebra relacional a ser otimizada.

- **Retorno**:
  - `None`
