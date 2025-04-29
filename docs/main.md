# Documentação do Script `main.py`

Este documento descreve o propósito e a funcionalidade do script `main.py`, que é responsável pelo processamento de consultas SQL e geração de árvores de álgebra relacional.

## Propósito e Funcionalidade

O script `main.py` permite:

- Processar consultas SQL fornecidas pelo usuário.
- Validar a sintaxe das consultas SQL.
- Gerar a álgebra relacional correspondente às consultas SQL.
- Visualizar a árvore de álgebra relacional gerada.

## Principais Funções e Seus Papéis

### `funcao_btn(comando)`

Função chamada ao clicar no botão de submissão da consulta SQL.

- **Parâmetros**:
  - `comando` (str): Comando SQL fornecido pelo usuário.

- **Retorno**:
  - `tuple`: Contém a álgebra relacional, a imagem da árvore não-otimizada e a imagem da árvore otimizada.

- **Exceções**:
  - `gr.Error`: Se o comando SQL for inválido ou ocorrer um erro na geração do grafo.

### `demo`

Bloco principal do Gradio para a interface de usuário.

- **Componentes**:
  - `cmd_sql` (Textbox): Campo de entrada para o comando SQL.
  - `btn` (Button): Botão de submissão.
  - `algeb_relac` (Textbox): Campo de saída para a álgebra relacional.
  - `grafo` (Image): Campo de saída para a imagem da árvore não-otimizada.
  - `grafo_otim` (Image): Campo de saída para a imagem da árvore otimizada.

- **Comportamento**:
  - Ao clicar no botão de submissão, a função `funcao_btn` é chamada com o comando SQL fornecido.
  - A álgebra relacional e as imagens das árvores são exibidas nos campos de saída correspondentes.
