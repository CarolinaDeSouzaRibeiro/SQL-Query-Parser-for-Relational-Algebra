# Roteiro de Apresentação — Projeto ProcConsultas

## 1. Introdução e Objetivo do Projeto

- **Contexto:** Trabalho da disciplina de Banco de Dados — Processador de Consultas.
- **Objetivo:** Implementar um sistema capaz de:
  - Analisar e validar consultas SQL restritas;
  - Converter para álgebra relacional;
  - Construir e otimizar a árvore de operadores;
  - Visualizar as árvores antes e depois da otimização.
- **Motivação:** Entender, na prática, como funciona o processamento interno de consultas em SGBDs.

## 2. Estrutura Geral do Projeto

- **parser.py:** Parsing, validação e conversão SQL → álgebra relacional.
- **arvores_construcao_otimizacao.py:** Construção, otimização e visualização das árvores de álgebra relacional.
- **main.py:** Interface gráfica (Gradio) para interação e visualização.
- **tests/** e **docs/exemplos_consultas.txt:** Testes automatizados e exemplos canônicos.

## 3. Demonstração do Funcionamento

### a) Interface Gráfica
- Mostre a tela inicial, campo de entrada SQL, exibição da álgebra relacional e das imagens das árvores.
- Explique o fluxo: usuário insere SQL → parser → árvore → otimização → visualização.

### b) Parsing e Validação
- Mostre um exemplo de SQL válido e um inválido.
- Explique como o parser valida nomes de tabelas, colunas, aliases e operadores.
- Referência: Função `process_sql_query` e helpers em `parser.py`.

### c) Conversão para Álgebra Relacional
- Explique como a consulta SQL é convertida para álgebra relacional.
- Mostre exemplos de saída.
- Referência: Função `convert_to_relational_algebra` em `parser.py`.

### d) Construção da Árvore de Operadores
- Explique a estrutura da árvore (classe `No`, classe `Arvore`).
- Mostre como a árvore é construída a partir da álgebra relacional.
- Referência: Função `converter_algebra_em_arvore` em `arvores_construcao_otimizacao.py`.

### e) Otimização Heurística
- Explique as heurísticas implementadas:
  - Pushdown de seleções (função `otimizar_selects`)
  - Pushdown de projeções (função `otimizar_projecoes`)
- Mostre exemplos de árvores antes e depois da otimização.
- Referência: Funções de otimização em `arvores_construcao_otimizacao.py`.

### f) Visualização
- Mostre as imagens geradas das árvores (não-otimizada e otimizada).
- Explique como o Graphviz é utilizado para gerar os grafos.
- Referência: Função `desenhar_arvore` em `arvores_construcao_otimizacao.py`.

### g) Testes Automatizados
- Explique a importância dos testes.
- Mostre como os testes são executados (ex: `python -m unittest tests/test_query_processor_suite.py` ou `python -m tests.batch_run_examples`).
- Referência: scripts em `tests/` e exemplos em `docs/exemplos_consultas.txt`.

## 4. Perguntas de Treinamento e Respostas Sugeridas

### 1. "Onde no código ocorre a validação dos nomes de tabelas e colunas?"
- **Resposta:**
  - A validação ocorre nas funções `_validate_and_get_table_alias` e `_validate_column_name` em `parser.py`.
  - Essas funções garantem que apenas nomes presentes no esquema sejam aceitos.

### 2. "Como o sistema transforma uma consulta SQL em álgebra relacional?"
- **Resposta:**
  - O parser primeiro valida e decompõe a consulta (função `parse_validate_sql`).
  - Em seguida, a função `convert_to_relational_algebra` monta a expressão de álgebra relacional.

### 3. "Explique o conceito de pushdown de seleção e onde ele é implementado."
- **Resposta:**
  - Pushdown de seleção é uma heurística de otimização que move operações de seleção o mais próximo possível das tabelas, reduzindo o volume de dados intermediários.
  - No código, está implementado na função `otimizar_selects` em `arvores_construcao_otimizacao.py`.

### 4. "Como a árvore de operadores é construída a partir da álgebra relacional?"
- **Resposta:**
  - A função `converter_algebra_em_arvore` em `arvores_construcao_otimizacao.py` faz o parsing da álgebra relacional e constrói recursivamente a árvore de operadores, usando a classe `No` para os nós.

### 5. "Como é feita a visualização das árvores?"
- **Resposta:**
  - A função `desenhar_arvore` utiliza a biblioteca Graphviz para gerar imagens PNG das árvores, que são exibidas na interface.

### 6. "Como os testes automatizados garantem a robustez do sistema?"
- **Resposta:**
  - Os testes em `tests/` cobrem casos válidos e inválidos, verificam a geração correta da álgebra relacional e a aplicação das otimizações, além de garantir que erros são tratados adequadamente.

### 7. "Como o sistema lida com erros de sintaxe ou semântica nas consultas?"
- **Resposta:**
  - O parser retorna mensagens de erro detalhadas quando encontra problemas de sintaxe ou nomes inválidos, e a interface exibe esses erros ao usuário.

### 8. "Quais limitações do sistema em relação ao SQL padrão?"
- **Resposta:**
  - O sistema aceita apenas um subconjunto restrito do SQL: SELECT, FROM, WHERE, INNER JOIN, operadores básicos (=, >, <, etc.), e não suporta subconsultas, funções agregadas, ORDER BY, etc.

## 5. Dicas Finais para a Apresentação

- Tenha exemplos prontos para demonstrar cada etapa (parsing, árvore, otimização, visualização).
- Esteja preparado para navegar rapidamente entre os arquivos de código e apontar funções específicas.
- Se possível, execute um teste ao vivo para mostrar a robustez do sistema.
- Mostre como os testes automatizados ajudam a garantir a qualidade do trabalho.

---

**Boa apresentação!** 