"""
# Módulo de Álgebra Relacional para Otimização de Consultas

Este módulo implementa um conjunto de ferramentas para converter expressões de álgebra relacional em árvores de operações
e realizar otimizações sobre essas árvores. Ele é útil para sistemas de gerenciamento de banco de dados, otimizadores de 
consultas e ferramentas educacionais relacionadas a banco de dados.

## Principais Funcionalidades

- Conversão de expressões de álgebra relacional em árvores binárias
- Otimização de árvores através do reposicionamento de operações de seleção
- Otimização de árvores através da introdução de projeções precoces
- Geração de representações visuais das árvores usando Graphviz

## Classes Principais

- `No`: Representa um nó na árvore de álgebra relacional
- `Arvore`: Representa uma árvore completa de álgebra relacional

## Operações Suportadas

- PROJECT (π): Projeção de atributos
- SELECT (σ): Seleção de tuplas baseada em condições
- JOIN (⨝): Junção natural ou junção com condição
- PRODUCT (⨝): Produto cartesiano
- TABLE: Declaração de tabela base

## Otimizações Implementadas

1. **Otimização de Seleções**: Move operações de seleção para mais próximo das tabelas
   base sempre que possível, reduzindo o volume de dados a serem processados nas operações
   subsequentes.

2. **Otimização de Projeções**: Introduz projeções logo após as operações de tabela base
   para reduzir o número de atributos transportados entre as operações, diminuindo o custo
   de processamento e transferência de dados.

## Exemplo de Uso

```python
# Expressão de álgebra relacional
algebra = "𝝿[cliente.nome, pedido.datapedido](𝛔[cliente.idcliente = pedido.cliente_idcliente]((cliente[cliente] ⨝ pedido[pedido])))"

# Converter para árvore
arvore = converter_algebra_em_arvore(algebra)

# Otimizar a árvore
arvore_otimizada = otimizar_selects(arvore)
arvore_otimizada = otimizar_projecoes(arvore_otimizada)

# Gerar visualização
desenhar_arvore(arvore, "arvore_original")
desenhar_arvore(arvore_otimizada, "arvore_otimizada")
"""

from __future__ import annotations
from typing import Optional, Literal
from graphviz import Digraph
from copy import deepcopy
from pathlib import Path

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
## DECLARAÇÃO DAS CLASSES QUE COMPÕE A ÁRVORE ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###

class No:
    def __init__(
        self: No, 
        conteudo: str,
        nivel: int, 
        pai: Optional[No], 
        filho_esq: Optional[No], 
        filho_dir: Optional[No]
    ) -> None:
        """
        Inicializa um nó da árvore binária.
        
        Args:
            conteudo (str): O conteúdo do nó.
            nivel (int): O nível do nó na árvore.
            pai (Optional[No]): O nó pai do nó atual. Com exceção da raiz, todos os nós devem ter um nó pai.
            filho_esq (Optional[No]): O filho esquerdo do nó atual. Com exceção dos nós de declaração de tabela, todos os nós devem ter filhos esquerdos.
            filho_dir (Optional[No]): O filho direito do nó atual. Somente os nós de join e de produto devem ter filhos direitos.
        """
        
        if not (pai is None or nivel == pai.nivel + 1):
            raise ValueError(f"O nível do nó atual deve ser igual ao nível do pai + 1. Nível do pai: {pai.nivel}, nível do nó atual: {nivel}.")
        
        self.valor = conteudo
        self.nivel = nivel
        self.pai = pai
        self.filho_esq = filho_esq
        self.filho_dir = filho_dir
        
    def get_operacao(self: No) -> Literal["PROJECT","SELECT","JOIN","PRODUCT","TABLE"]:
        """
        Retorna qual operação o nó representa.
        
        Possíveis operações:
        - PROJECT: Representada por '𝝿'
        - SELECT: Representada por '𝛔'
        - JOIN: Um produto cartesiano com uma condição de junção, representada por '⨝' com colchetes.
        - PRODUCT: Um produto cartesiano, representada por '⨝' sem colchetes.
        - TABLE: A declaração de uma tabela.
        """
        if sum(['𝝿' in self.valor, '𝛔' in self.valor, '⨝' in self.valor]) > 1:
            raise ValueError(f"Um nó não pode representar mais de uma operação ao mesmo tempo. Conteúdo do nó: {self.valor}.")

        if '𝝿' in self.valor:
            return "PROJECT"
        
        if '𝛔' in self.valor:
            return "SELECT"
        
        if '⨝' in self.valor:
            
            if '[' in self.valor and ']' in self.valor:
                return "JOIN"
            
            return "PRODUCT"
        
        return "TABLE"
        
    def __str__(self):
        return self.valor
    
    def __repr__(self):
        return f"No(valor={self.valor}, nivel={self.nivel}, pai={self.pai.valor if self.pai else None})"
        
class Arvore:
    def __init__(self: Arvore) -> None:
        self.raiz = None
        
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ####
## PROCESSAMENTO DE UMA ÁLGEBRA RELACIONAL PARA UMA ÁRVORE BINÁRIA DE CONSULTAS ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ####
        
def remover_espacamentos_e_quebras_de_linhas(
    expressao: str,
) -> str:
    """
    Remove espaços e quebras de linha de uma expressão algébrica.
    
    Args:
        expressao (str): A expressão algébrica a ser limpa.
        
    Returns:
        str: A expressão limpa.
    """
    return expressao.replace(" ", "").replace("\n", "").replace("\t", "")

def encontrar_divisao_join(expr: str) -> tuple[str, str]:
    """
    Encontra o ponto correto para dividir uma expressão de join.
    
    Args:
        expr (str): A expressão de join a ser dividida.
        
    Returns:
        tuple[str, str]: As subexpressões esquerda e direita.
    """
    # Se não começar com parênteses, é uma expressão simples
    if not expr.startswith("("):
        partes = expr.split("⨝", 1)
        if len(partes) < 2:
            raise ValueError(f"Expressão de join inválida: {expr}")
        return partes[0], partes[1]
    
    # Encontrar o ponto de divisão considerando parênteses aninhados
    contador_parenteses = 0
    for i, char in enumerate(expr):
        if char == '(':
            contador_parenteses += 1
        elif char == ')':
            contador_parenteses -= 1
        
        # Encontramos o fim do primeiro operando quando fechamos o conjunto de parênteses inicial
        if contador_parenteses == 0 and i > 0:
            # Verificar se o próximo caractere é um operador de join
            if i + 1 < len(expr) and expr[i+1] == '⨝':
                return expr[:i+1], expr[i+2:]
    
    raise ValueError(f"Não foi possível dividir a expressão de join: {expr}")

def converter_algebra_em_arvore(
    algebra_relacional: str,
) -> Arvore:
    """
    Converte uma expressão algébrica em uma árvore binária.
    
    Args:
        algebra_relacional (str): A expressão algébrica a ser convertida.
        
    Returns:
        Arvore: A árvore binária resultante da conversão.
    """
    algebra_relacional = remover_espacamentos_e_quebras_de_linhas(algebra_relacional)
    
    arvore = Arvore()
    arvore.raiz = parse(algebra_relacional)
    
    return arvore

def parse(expr: str, nivel: int = 0, pai: Optional[No] = None) -> No:
    """
    Analisa uma expressão algébrica e constrói uma árvore binária a partir dela.
    
    Args:
        expr (str): A expressão algébrica a ser analisada.
        nivel (int): O nível atual na árvore. Padrão é 0.
        pai (Optional[No]): O nó pai do nó atual. Padrão é None.
    """
    # Remover parênteses externos desnecessários
    expr = remover_parenteses_externos(expr)
    
    if expr.startswith("𝝿"):  # Projeção
        fim_param = expr.find("]")  # Encontra o fim dos atributos
        conteudo = expr[:fim_param + 1]
        subexpr = expr[fim_param + 1:].strip("()")
        no = No(conteudo, nivel, pai, None, None)
        no.filho_esq = parse(subexpr, nivel + 1, no)
        return no
    
    elif expr.startswith("𝛔"):  # Seleção
        fim_param = expr.find("]")
        conteudo = expr[:fim_param + 1]
        subexpr = expr[fim_param + 1:].strip("()")
        
        # Verifica se há múltiplas condições separadas por "∧"
        if "∧" in conteudo[1:-1]:  # Verifica se o AND está dentro dos colchetes da seleção
            condicoes = conteudo[2:-1].split("∧")  # Remove os colchetes e separa as condições
            no_atual = No(f"𝛔[{condicoes[-1].strip()}]", nivel, pai, None, None)
            nivel_atual = nivel + 1
            subexpr_atual = subexpr
            
            # Processa cada condição de baixo para cima (exceto a última que já foi processada)
            for condicao in reversed(condicoes[:-1]):
                subno = No(f"𝛔[{condicao.strip()}]", nivel_atual, no_atual, None, None)
                subno.filho_esq = parse(subexpr_atual, nivel_atual + 1, subno)
                no_atual.filho_esq = subno
                no_atual = subno
                nivel_atual += 1
            
            # O último nó (mais interno) recebe a subexpressão original
            if no_atual.filho_esq is None:
                no_atual.filho_esq = parse(subexpr, nivel_atual, no_atual)
            
            return no_atual.pai if no_atual.pai else no_atual
        else:
            no = No(conteudo, nivel, pai, None, None)
            no.filho_esq = parse(subexpr, nivel + 1, no)
            return no

    elif "⨝" in expr:  # Join ou Produto
        # Limpar parênteses externos
        expr = remover_parenteses_externos(expr)
        
        # Verifica se é um JOIN com condição
        if expr.startswith("⨝["):
            fim_param = expr.find("]")
            conteudo = expr[:fim_param + 1]
            restante = expr[fim_param + 1:]
            
            # Procura pelo ponto de divisão entre os operandos
            try:
                # Identifica os dois operandos do join
                if '⨝' in restante:
                    # Caso complexo, precisa analisar parênteses para encontrar a divisão correta
                    esq, dir = identificar_operandos_complexos(restante)
                else:
                    # Caso simples onde há apenas um operando após o join com condição
                    esq, dir = restante, ""
            except Exception as e:
                raise ValueError(f"Erro ao identificar os operandos do join: {e}")
        else:
            # É um produto simples ou join sem condição explícita
            conteudo = "⨝"
            
            try:
                # Tenta dividir a expressão nas duas subexpressões do produto/join
                if expr.count("⨝") == 1:
                    # Caso simples: único operador de join
                    partes = expr.split("⨝", 1)
                    esq, dir = partes[0], partes[1]
                else:
                    # Caso complexo: múltiplos joins
                    try:
                        esq, dir = encontrar_divisao_join(expr)
                    except:
                        # Tentativa alternativa para expressões muito complexas
                        esq, dir = identificar_operandos_complexos(expr)
            except Exception as e:
                raise ValueError(f"Erro ao identificar os operandos do produto/join: {e}")
        
        # Remove parênteses externos dos operandos
        esq = remover_parenteses_externos(esq)
        dir = remover_parenteses_externos(dir)
        
        # Cria o nó para o join/produto
        no = No(conteudo, nivel, pai, None, None)
        
        # Processa os operandos como subárvores
        no.filho_esq = parse(esq, nivel + 1, no)
        no.filho_dir = parse(dir, nivel + 1, no)
        
        return no

    else:  # Tabela (base case)
        return No(expr, nivel, pai, None, None)

def remover_parenteses_externos(expr: str) -> str:
    """
    Remove parênteses externos desnecessários de uma expressão.
    
    Args:
        expr (str): A expressão a ser processada.
        
    Returns:
        str: A expressão sem parênteses externos desnecessários.
    """
    expr = expr.strip()
    
    # Se não começar e terminar com parênteses, retorna como está
    if not (expr.startswith("(") and expr.endswith(")")):
        return expr
    
    # Verifica se os parênteses externos são necessários
    contador = 0
    for i, char in enumerate(expr):
        if char == '(':
            contador += 1
        elif char == ')':
            contador -= 1
        
        # Se o contador chegar a zero antes do final, os parênteses externos não podem ser removidos
        if contador == 0 and i < len(expr) - 1:
            return expr
    
    # Recursivamente remove parênteses externos
    return remover_parenteses_externos(expr[1:-1])

def identificar_operandos_complexos(expr: str) -> tuple[str, str]:
    """
    Identifica os dois operandos em uma expressão de join complexa.
    
    Args:
        expr (str): A expressão complexa a ser analisada.
        
    Returns:
        tuple[str, str]: Os operandos esquerdo e direito.
    """
    # Remove parênteses externos
    expr = remover_parenteses_externos(expr)
    
    if "⨝" not in expr:
        # Se não houver join, a expressão completa é um único operando
        return expr, ""
    
    # Encontrar a posição correta do operador de join, respeitando parênteses aninhados
    contador_parenteses = 0
    for i, char in enumerate(expr):
        if char == '(':
            contador_parenteses += 1
        elif char == ')':
            contador_parenteses -= 1
        elif char == '⨝' and contador_parenteses == 0:
            # Encontrou o operador de join principal
            return expr[:i], expr[i+1:]
    
    # Se não encontrou um ponto de divisão adequado
    # Para expressões como ((a ⨝ b) ⨝ c)
    if expr.startswith("(") and ")" in expr:
        idx = expr.find(")")
        if idx + 1 < len(expr) and expr[idx+1] == '⨝':
            return expr[:idx+1], expr[idx+2:]
    
    raise ValueError(f"Não foi possível identificar os operandos em: {expr}")

## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
## GERANDO A IMAGEM DA ÁRVORE DE CONSULTAS ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ###

def desenhar_arvore(arvore: Arvore, nome_arquivo: str, nome_subpasta: Optional[str] = None) -> None:
    if arvore.raiz is None:
        raise ValueError("A árvore está vazia. Não é possível desenhar.")
    
    Path("img").mkdir(exist_ok=True)
    
    if nome_subpasta:
        img_dir = Path("img", nome_subpasta)
        img_dir.mkdir(exist_ok=True)
    else:
        img_dir = Path("img")
    
    # Cria o caminho completo para o arquivo dentro da pasta 'img'
    caminho_arquivo = img_dir / nome_arquivo

    dot = Digraph(comment="Árvore de Álgebra Relacional", format="png")
    
    def adicionar_nos(dot: Digraph, no: No):
        dot.node(str(id(no)), label=no.valor.replace("𝝿", "π").replace("𝛔", "σ").replace("⨝", "X"))
        
        if no.filho_esq:
            dot.edge(str(id(no)), str(id(no.filho_esq)))
            adicionar_nos(dot, no.filho_esq)
        
        if no.filho_dir:
            dot.edge(str(id(no)), str(id(no.filho_dir)))
            adicionar_nos(dot, no.filho_dir)

    adicionar_nos(dot, arvore.raiz)
    dot.render(filename=str(caminho_arquivo), cleanup=True)
    print(f"Árvore salva como {caminho_arquivo.with_suffix('.png')}")
    
## ## ## ## ## ## ## ## ## ## ## ## ####
## OTIMIZAÇÃO DAS OPERAÇÕES DE SELECT ##
## ## ## ## ## ## ## ## ## ## ## ## ####

def otimizar_selects(arvore_nao_otimizada: Arvore) -> Arvore:
    """
    Otimiza a árvore de álgebra relacional movendo seleções para mais perto das tabelas
    quando possível, respeitando as dependências entre tabelas.
    
    Args:
        arvore_nao_otimizada (Arvore): A árvore a ser otimizada.
        
    Returns:
        Arvore: A árvore otimizada.
    """
    # Cria uma cópia profunda para não modificar a árvore original
    arvore_otimizada = Arvore()
    if arvore_nao_otimizada.raiz is None:
        return arvore_otimizada
    
    # Copia a raiz
    arvore_otimizada.raiz = deepcopy(arvore_nao_otimizada.raiz)
    
    # Coleta todas as seleções na árvore
    selecoes = []
    coletar_selecoes(arvore_otimizada.raiz, selecoes)
    
    # Remove todas as seleções da árvore
    nova_raiz = remover_selecoes(arvore_otimizada.raiz)
    if nova_raiz:
        arvore_otimizada.raiz = nova_raiz
        arvore_otimizada.raiz.nivel = 0
        atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_esq, 1)
        atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_dir, 1)
    
    # Classifica as seleções em dois grupos: 
    # 1. Seleções que envolvem apenas uma tabela
    # 2. Seleções que envolvem múltiplas tabelas
    selecoes_unica_tabela = []
    selecoes_multiplas_tabelas = []
    
    for selecao in selecoes:
        if len(selecao["tabelas"]) == 1:
            selecoes_unica_tabela.append(selecao)
        else:
            selecoes_multiplas_tabelas.append(selecao)
    
    # Primeiro, insere as seleções de uma única tabela
    if selecoes_unica_tabela:
        nova_raiz = inserir_selecoes_unica_tabela(arvore_otimizada.raiz, selecoes_unica_tabela)
        if nova_raiz:
            arvore_otimizada.raiz = nova_raiz
            arvore_otimizada.raiz.nivel = 0
            atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_esq, 1)
            atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_dir, 1)
    
    # Depois, insere as seleções que envolvem múltiplas tabelas
    if selecoes_multiplas_tabelas:
        nova_raiz = inserir_selecoes_multiplas_tabelas(arvore_otimizada.raiz, selecoes_multiplas_tabelas)
        if nova_raiz:
            arvore_otimizada.raiz = nova_raiz
            arvore_otimizada.raiz.nivel = 0
            atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_esq, 1)
            atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_dir, 1)
    
    return arvore_otimizada

def inserir_selecoes_unica_tabela(no: No, selecoes: list[dict]) -> No:
    """
    Insere seleções que envolvem apenas uma tabela diretamente acima dessa tabela.
    
    Args:
        no (No): O nó atual sendo processado.
        selecoes (list[dict]): Lista de seleções a serem inseridas.
        
    Returns:
        No: O nó após a inserção das seleções.
    """
    if no is None:
        return None
    
    # Processa os filhos recursivamente
    no.filho_esq = inserir_selecoes_unica_tabela(no.filho_esq, selecoes)
    if no.filho_esq:
        no.filho_esq.pai = no
        no.filho_esq.nivel = no.nivel + 1
        
    no.filho_dir = inserir_selecoes_unica_tabela(no.filho_dir, selecoes)
    if no.filho_dir:
        no.filho_dir.pai = no
        no.filho_dir.nivel = no.nivel + 1
    
    # Se é uma tabela, verifica se há seleções aplicáveis
    if no.get_operacao() == "TABLE":
        # Extrai o nome/alias da tabela
        nome_tabela = no.valor
        alias = nome_tabela
        if "[" in nome_tabela and "]" in nome_tabela:
            alias = nome_tabela.split("[")[1].split("]")[0]
        
        # Filtra as seleções aplicáveis a esta tabela
        selecoes_aplicaveis = [s for s in selecoes if len(s["tabelas"]) == 1 and next(iter(s["tabelas"])) == alias]
        
        # Aplica as seleções em ordem
        novo_no = no
        for selecao in selecoes_aplicaveis:
            nivel = novo_no.nivel
            pai = novo_no.pai
            
            # Cria o nó de seleção
            novo_selecao = No(f"𝛔[{selecao['condicao']}]", nivel, pai, novo_no, None)
            novo_no.pai = novo_selecao
            novo_no.nivel = novo_selecao.nivel + 1
            
            # Conecta ao pai original
            if pai:
                if pai.filho_esq == novo_no:
                    pai.filho_esq = novo_selecao
                elif pai.filho_dir == novo_no:
                    pai.filho_dir = novo_selecao
            
            # Atualiza o nó atual
            novo_no = novo_selecao
        
        return novo_no
    
    return no

def inserir_selecoes_multiplas_tabelas(no: No, selecoes: list[dict]) -> No:
    """
    Insere seleções que envolvem múltiplas tabelas nos pontos adequados da árvore.
    Versão melhorada que posiciona corretamente operações que envolvem múltiplas tabelas.
    
    Args:
        no (No): O nó atual sendo processado.
        selecoes (list[dict]): Lista de seleções a serem inseridas.
        
    Returns:
        No: O nó após a inserção das seleções.
    """
    if no is None:
        return None
    
    # Primeiro, processa os filhos recursivamente
    no.filho_esq = inserir_selecoes_multiplas_tabelas(no.filho_esq, selecoes)
    if no.filho_esq:
        no.filho_esq.pai = no
        no.filho_esq.nivel = no.nivel + 1
        
    no.filho_dir = inserir_selecoes_multiplas_tabelas(no.filho_dir, selecoes)
    if no.filho_dir:
        no.filho_dir.pai = no
        no.filho_dir.nivel = no.nivel + 1
    
    # Se é um JOIN ou PRODUCT, verifica quais seleções podem ser aplicadas aqui
    if no.get_operacao() in ["JOIN", "PRODUCT"]:
        # Identifica tabelas disponíveis nesta subárvore
        tabelas_disponiveis = obter_tabelas_da_subarvore(no)
        
        # Filtra as seleções aplicáveis - aquelas cujas tabelas estão todas disponíveis
        selecoes_aplicaveis = []
        selecoes_nao_aplicaveis = []
        
        for selecao in selecoes:
            if all(tabela in tabelas_disponiveis for tabela in selecao["tabelas"]):
                # Verifica se a seleção envolve tabelas de ambos os lados do JOIN/PRODUCT
                tabelas_esq = obter_tabelas_da_subarvore(no.filho_esq)
                tabelas_dir = obter_tabelas_da_subarvore(no.filho_dir)
                
                # Se há tabelas de ambos os lados, a seleção deve ser aplicada neste nível
                if (any(t in tabelas_esq for t in selecao["tabelas"]) and 
                    any(t in tabelas_dir for t in selecao["tabelas"])):
                    selecoes_aplicaveis.append(selecao)
                # Se todas as tabelas estão em apenas um dos lados, a seleção não é aplicável neste nível
                elif all(t in tabelas_esq for t in selecao["tabelas"]):
                    selecoes_nao_aplicaveis.append(selecao)
                elif all(t in tabelas_dir for t in selecao["tabelas"]):
                    selecoes_nao_aplicaveis.append(selecao)
                # Se não se encaixa em nenhum dos casos acima, aplica neste nível
                else:
                    selecoes_aplicaveis.append(selecao)
            else:
                selecoes_nao_aplicaveis.append(selecao)
        
        # Atualiza a lista de seleções
        selecoes[:] = selecoes_nao_aplicaveis
        
        # Aplica as seleções aplicáveis
        novo_no = no
        for selecao in selecoes_aplicaveis:
            nivel = novo_no.nivel
            pai = novo_no.pai
            
            # Cria o nó de seleção
            novo_selecao = No(f"𝛔[{selecao['condicao']}]", nivel, pai, novo_no, None)
            novo_no.pai = novo_selecao
            novo_no.nivel = novo_selecao.nivel + 1
            
            # Conecta ao pai original
            if pai:
                if pai.filho_esq == novo_no:
                    pai.filho_esq = novo_selecao
                elif pai.filho_dir == novo_no:
                    pai.filho_dir = novo_selecao
            
            # Atualiza o nó atual
            novo_no = novo_selecao
        
        return novo_no
    
    return no

def extrair_tabelas_da_condicao(condicao: str) -> set[str]:
    """
    Extrai os nomes das tabelas envolvidas em uma condição de seleção.
    Versão melhorada que identifica corretamente todas as tabelas.
    
    Args:
        condicao (str): A condição de seleção.
        
    Returns:
        set[str]: Conjunto de nomes de tabelas envolvidas.
    """
    colunas_por_tabela = extrair_colunas_da_condicao(condicao)
    return set(colunas_por_tabela.keys())

def coletar_selecoes(no: No, selecoes: list[dict]):
    """
    Coleta todas as seleções presentes na árvore.
    Versão melhorada que identifica corretamente as tabelas dependentes.
    
    Args:
        no (No): O nó atual sendo visitado.
        selecoes (list[dict]): lista onde as seleções serão coletadas.
    """
    if no is None:
        return
    
    if no.get_operacao() == "SELECT":
        # Extrai a condição da seleção
        condicao = no.valor[2:-1]  # Remove "𝛔[" e "]"
        
        # Identifica as tabelas envolvidas na condição
        tabelas_envolvidas = extrair_tabelas_da_condicao(condicao)
        
        selecoes.append({
            "condicao": condicao,
            "tabelas": tabelas_envolvidas
        })
    
    # Continua a busca nos filhos
    coletar_selecoes(no.filho_esq, selecoes)
    coletar_selecoes(no.filho_dir, selecoes)

def remover_selecoes(no: No) -> Optional[No]:
    """
    Remove todos os nós de seleção da árvore.
    
    Args:
        no (No): O nó atual sendo processado.
        
    Returns:
        Optional[No]: O nó resultante após a remoção das seleções.
    """
    if no is None:
        return None
    
    if no.get_operacao() == "SELECT":
        # Substitui o nó de seleção pelo seu filho
        if no.filho_esq:
            filho = remover_selecoes(no.filho_esq)
            if filho:
                filho.pai = no.pai
                # Ajuste o nível do filho para manter a consistência com o novo pai
                if filho.pai:
                    filho.nivel = filho.pai.nivel + 1
                else:
                    filho.nivel = 0  # Se é a nova raiz
                # Atualiza os níveis dos descendentes
                atualizar_niveis_recursivamente(filho.filho_esq, filho.nivel + 1)
                atualizar_niveis_recursivamente(filho.filho_dir, filho.nivel + 1)
            return filho
        return None
    
    # Processa os filhos
    no.filho_esq = remover_selecoes(no.filho_esq)
    if no.filho_esq:
        no.filho_esq.pai = no
        no.filho_esq.nivel = no.nivel + 1  # Garante nível consistente
        
    no.filho_dir = remover_selecoes(no.filho_dir)
    if no.filho_dir:
        no.filho_dir.pai = no
        no.filho_dir.nivel = no.nivel + 1  # Garante nível consistente
    
    return no

def obter_tabelas_da_subarvore(no: No) -> set[str]:
    """
    Identifica todas as tabelas presentes em uma subárvore.
    
    Args:
        no (No): A raiz da subárvore.
        
    Returns:
        set[str]: Conjunto de nomes de tabelas.
    """
    if no is None:
        return set()
    
    tabelas = set()
    
    if no.get_operacao() == "TABLE":
        # O valor pode ser algo como "tabela[alias]"
        nome_completo = no.valor
        if "[" in nome_completo and "]" in nome_completo:
            alias = nome_completo.split("[")[1].split("]")[0]
            tabelas.add(alias)
        else:
            tabelas.add(nome_completo)
    
    # Adiciona tabelas dos filhos
    tabelas.update(obter_tabelas_da_subarvore(no.filho_esq))
    tabelas.update(obter_tabelas_da_subarvore(no.filho_dir))
    
    return tabelas

def atualizar_niveis_recursivamente(no: No, nivel: int) -> None:
    """
    Atualiza os níveis de um nó e de todos os seus descendentes.
    
    Args:
        no (No): O nó a ter seu nível atualizado.
        nivel (int): O novo nível do nó.
    """
    if no is None:
        return
    
    no.nivel = nivel
    
    # Atualiza os filhos recursivamente
    atualizar_niveis_recursivamente(no.filho_esq, nivel + 1)
    atualizar_niveis_recursivamente(no.filho_dir, nivel + 1)

## ## ## ## ## ## ## ## ## ## ## ## ## ##
## OTIMIZAÇÃO DAS OPERAÇÕES DE PROJECT ##
## ## ## ## ## ## ## ## ## ## ## ## ## ##

def otimizar_projecoes(arvore_nao_otimizada: Arvore) -> Arvore:
    """
    Otimiza a árvore de álgebra relacional adicionando uma projeção logo imediatamente 
    após as tabelas para filtrar somente as colunas necessárias para a consulta.
    
    Esta técnica reduz a quantidade de dados movidos entre operações, melhorando o desempenho.
    
    Args:
        arvore_nao_otimizada (Arvore): A árvore a ser otimizada.
        
    Returns:
        Arvore: A árvore otimizada.
    """
    # Cria uma cópia profunda para não modificar a árvore original
    arvore_otimizada = Arvore()
    if arvore_nao_otimizada.raiz is None:
        return arvore_otimizada
    
    # Copia a raiz
    arvore_otimizada.raiz = deepcopy(arvore_nao_otimizada.raiz)
    
    # Identifica todas as colunas necessárias para a consulta
    colunas_necessarias = identificar_colunas_necessarias(arvore_otimizada.raiz)
    
    # Insere projeções em cada tabela base para limitar as colunas
    novo_raiz = inserir_projecoes_precoces(arvore_otimizada.raiz, colunas_necessarias)
    if novo_raiz:
        arvore_otimizada.raiz = novo_raiz
        # Garantir que a raiz está no nível 0
        arvore_otimizada.raiz.nivel = 0
        # Atualizar os níveis da árvore inteira para garantir consistência
        atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_esq, 1)
        atualizar_niveis_recursivamente(arvore_otimizada.raiz.filho_dir, 1)
    
    return arvore_otimizada

def identificar_colunas_necessarias(no: No) -> dict[str, set[str]]:
    """
    Identifica todas as colunas necessárias para a consulta, agrupadas por tabela.
    Versão melhorada que considera corretamente operações intermediárias.
    
    Args:
        no (No): O nó atual sendo analisado.
        
    Returns:
        dict[str, set[str]]: Dicionário com tabelas como chaves e conjuntos de colunas como valores.
    """
    colunas = {}
    
    # Analisa o nó atual
    if no.get_operacao() == "PROJECT":
        # Extrai as colunas da projeção
        projecao = no.valor[2:-1]  # Remove "𝝿[" e "]"
        for coluna in projecao.split(","):
            coluna = coluna.strip()
            if "." in coluna:
                tabela, nome_coluna = coluna.split(".")
                if tabela not in colunas:
                    colunas[tabela] = set()
                colunas[tabela].add(nome_coluna)
    
    elif no.get_operacao() == "SELECT":
        # Extrai colunas da condição de seleção
        condicao = no.valor[2:-1]  # Remove "𝛔[" e "]"
        # Extrai todas as colunas mencionadas na condição
        colunas_select = extrair_colunas_da_condicao(condicao)
        for tabela, cols in colunas_select.items():
            if tabela not in colunas:
                colunas[tabela] = set()
            colunas[tabela].update(cols)
    
    elif no.get_operacao() == "JOIN":
        # Extrai colunas da condição de join
        if "[" in no.valor and "]" in no.valor:
            condicao = no.valor[2:-1]  # Remove "⨝[" e "]"
            colunas_join = extrair_colunas_da_condicao(condicao)
            for tabela, cols in colunas_join.items():
                if tabela not in colunas:
                    colunas[tabela] = set()
                colunas[tabela].update(cols)
    
    # Processa os filhos recursivamente e combina os resultados
    if no.filho_esq:
        colunas_filho = identificar_colunas_necessarias(no.filho_esq)
        for tabela, cols in colunas_filho.items():
            if tabela not in colunas:
                colunas[tabela] = set()
            colunas[tabela].update(cols)
    
    if no.filho_dir:
        colunas_filho = identificar_colunas_necessarias(no.filho_dir)
        for tabela, cols in colunas_filho.items():
            if tabela not in colunas:
                colunas[tabela] = set()
            colunas[tabela].update(cols)
    
    return colunas

def extrair_colunas_da_condicao(condicao: str) -> dict[str, set[str]]:
    """
    Extrai todas as colunas mencionadas em uma condição.
    
    Args:
        condicao (str): A condição a ser analisada.
        
    Returns:
        dict[str, set[str]]: Dicionário com tabelas como chaves e conjuntos de colunas como valores.
    """
    colunas = {}
    
    # Normaliza a condição removendo operadores lógicos
    tokens = []
    # Lista de operadores comuns em condições
    operadores = ["∧", "AND", "OR", "=", ">", "<", ">=", "<=", "<>"]
    
    # Substituir operadores por espaços para facilitar a tokenização
    condicao_norm = condicao
    for op in operadores:
        condicao_norm = condicao_norm.replace(op, " ")
    
    # Extrai tokens potenciais
    for token in condicao_norm.split():
        token = token.strip("()[],'\"")
        tokens.append(token)
    
    # Analisa cada token em busca de padrões "tabela.coluna"
    for token in tokens:
        if "." in token:
            partes = token.split(".")
            if len(partes) == 2:
                tabela, coluna = partes
                if tabela not in colunas:
                    colunas[tabela] = set()
                colunas[tabela].add(coluna)
    
    return colunas

def inserir_projecoes_precoces(no: No, colunas_necessarias: dict[str, set[str]]) -> No:
    """
    Insere projeções precoces nos nós de tabela.
    Versão melhorada que considera todas as colunas necessárias.
    
    Args:
        no (No): O nó atual sendo processado.
        colunas_necessarias (dict[str, set[str]]): Dicionário de colunas necessárias por tabela.
        
    Returns:
        No: O nó raiz da subárvore (possivelmente modificado)
    """
    if no is None:
        return None
    
    # Processa os filhos primeiro
    no.filho_esq = inserir_projecoes_precoces(no.filho_esq, colunas_necessarias)
    if no.filho_esq:
        no.filho_esq.pai = no
        no.filho_esq.nivel = no.nivel + 1
    
    no.filho_dir = inserir_projecoes_precoces(no.filho_dir, colunas_necessarias)
    if no.filho_dir:
        no.filho_dir.pai = no
        no.filho_dir.nivel = no.nivel + 1
    
    # Se é uma tabela, insere uma projeção
    if no.get_operacao() == "TABLE":
        nome_tabela = no.valor
        alias = nome_tabela
        
        # Extrai o alias se existir
        if "[" in nome_tabela and "]" in nome_tabela:
            alias = nome_tabela.split("[")[1].split("]")[0]
        
        # Verifica se há colunas específicas para esta tabela
        if alias in colunas_necessarias and colunas_necessarias[alias]:
            # Cria a lista de colunas para a projeção
            cols = [f"{alias}.{col}" for col in colunas_necessarias[alias]]
            cols_str = ", ".join(cols)
            
            # Cria o nó de projeção
            projecao = No(f"𝝿[{cols_str}]", no.nivel, no.pai, no, None)
            
            # Ajusta o pai do nó de tabela
            no.pai = projecao
            no.nivel = projecao.nivel + 1
            
            # Conecta a projeção ao pai original
            if projecao.pai:
                if projecao.pai.filho_esq == no:
                    projecao.pai.filho_esq = projecao
                elif projecao.pai.filho_dir == no:
                    projecao.pai.filho_dir = projecao
            
            return projecao
    
    # Se não houve modificação, retorna o nó original
    return no

## ## ## ## ## ## ##
## CASOS DE TESTE ##
## ## ## ## ## ## ##

test_cases = [
    # (Somente os testes com `expected_ra`, removi os que esperam erro)
    {"description": "T1", "expected_ra": "𝝿[cliente.nome, cliente.email](cliente[cliente])"},
    {"description": "T2", "expected_ra": "𝝿[cliente.nome, cliente.email](cliente[cliente])"},
    {"description": "T3", "expected_ra": "𝝿[tipocliente.idtipocliente, tipocliente.descricao](tipocliente[tipocliente])"},
    {"description": "T4", "expected_ra": "𝝿[produto.nome](𝛔[produto.preco > 50.00](produto[produto]))"},
    {"description": "T5", "expected_ra": "𝝿[cliente.nome](𝛔[cliente.email = 'teste@mail.com'](cliente[cliente]))"},
    {"description": "T6", "expected_ra": "𝝿[produto.idproduto, produto.quantestoque](𝛔[produto.preco < 100 ∧ produto.quantestoque >= 10](produto[produto]))"},
    {"description": "T14", "expected_ra": "𝝿[cliente.nome](𝛔[cliente.idcliente < 5](cliente[cliente]))"},
    {"description": "T15", "expected_ra": "𝝿[p.idpedido](𝛔[p.datapedido > c.dataregistro ∧ p.cliente_idcliente = c.idcliente]((pedido[p] ⨝ cliente[c])))"},
    {"description": "T7", "expected_ra": "𝝿[cliente.nome, pedido.datapedido](𝛔[cliente.idcliente = pedido.cliente_idcliente]((cliente[cliente] ⨝ pedido[pedido])))"},
    {"description": "T8", "expected_ra": "𝝿[c.nome, p.datapedido](𝛔[c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))"},
    {"description": "T9", "expected_ra": "𝝿[c.nome, p.idpedido](𝛔[p.valortotalpedido > 100.0 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))"},
    {"description": "T10", "expected_ra": "𝝿[c.idcategoria, c.descricao, p.idproduto, p.nome, p.descricao, p.preco, p.quantestoque, p.categoria_idcategoria](𝛔[c.idcategoria = p.categoria_idcategoria]((categoria[c] ⨝ produto[p])))"},
    {"description": "T11", "expected_ra": "𝝿[ped.idpedido, prod.nome, itens.quantidade](𝛔[ped.idpedido = itens.pedido_idpedido ∧ itens.produto_idproduto = prod.idproduto](((pedido[ped] ⨝ pedido_has_produto[itens]) ⨝ produto[prod])))"},
    {"description": "T12", "expected_ra": "𝝿[ped.idpedido, prod.nome](𝛔[ped.cliente_idcliente = 10 ∧ itens.quantidade > 1 ∧ ped.idpedido = itens.pedido_idpedido ∧ itens.produto_idproduto = prod.idproduto](((pedido[ped] ⨝ pedido_has_produto[itens]) ⨝ produto[prod])))"},
    {"description": "T13", "expected_ra": "𝝿[c.nome, p.datapedido](𝛔[p.cliente_idcliente = c.idcliente]((cliente[c] ⨝ pedido[p])))"},
    {"description": "E10", "expected_ra": "𝝿[p.nome](𝛔[p.categoria_idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
    {"description": "E10b", "expected_ra": "𝝿[p.nome](𝛔[c.idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
    {"description": "E10c", "expected_ra": "𝝿[p.nome](𝛔[c.idcategoria = c.idcategoria]((produto[p] ⨝ categoria[c])))"},
]

## ## ## ## ## ## ## ###
## GERAÇÃO DE IMAGENS ##
## ## ## ## ## ## ## ###

def gerar_imagens(algebra: str, nome_arquivo: str) -> None:
    """
    Gera imagens da árvore de álgebra relacional a partir de uma expressão.
    
    Args:
        algebra_relacional (str): A expressão de álgebra relacional.
        nome_arquivo (str): O nome do arquivo para salvar a imagem.
    """
    try:
        arvore_nao_otimizada = converter_algebra_em_arvore(algebra)
        desenhar_arvore(arvore_nao_otimizada, nome_arquivo, nome_subpasta="nao_otimizadas")
        
        arvore_selects_otimizadas = otimizar_selects(arvore_nao_otimizada)
        desenhar_arvore(arvore_selects_otimizadas, nome_arquivo, nome_subpasta="selects_otimizadas")
        
        arvore_projecoes_otimizadas = otimizar_projecoes(arvore_nao_otimizada)
        desenhar_arvore(arvore_projecoes_otimizadas, nome_arquivo, nome_subpasta="projecoes_otimizadas")
        
        arvore_final = otimizar_projecoes(arvore_selects_otimizadas)
        desenhar_arvore(arvore_final, nome_arquivo, nome_subpasta="otimizadas")
    except Exception as e:
        print(f"❌ Falha ao processar {descricao}: {e}")
    else:
        print(f"✅ Árvore gerada para {descricao} e salva como '{nome_arquivo}.png'")

def gerar_imagem_arvore_processada(algebra_relacional: str):
    """
    Gera a imagem da árvore não-otimizada e salva em 'img/arvore_consulta_processada.png'.
    """
    from pathlib import Path
    Path("img").mkdir(exist_ok=True)
    arvore = converter_algebra_em_arvore(algebra_relacional)
    # Salva como 'img/arvore_consulta_processada.png'
    desenhar_arvore(arvore, "arvore_consulta_processada", nome_subpasta=None)

def gerar_grafo_otimizado(algebra_relacional: str):
    """
    Gera a imagem da árvore otimizada (selects + projeções) e salva em 'img/arvore_consulta_otimizada.png'.
    """
    from pathlib import Path
    Path("img").mkdir(exist_ok=True)
    arvore = converter_algebra_em_arvore(algebra_relacional)
    arvore_otimizada = otimizar_selects(arvore)
    arvore_otimizada = otimizar_projecoes(arvore_otimizada)
    # Salva como 'img/arvore_consulta_otimizada.png'
    desenhar_arvore(arvore_otimizada, "arvore_consulta_otimizada", nome_subpasta=None)


## ## ## ## ## ## ## ##
## TESTANDO O MÓDULO ##
## ## ## ## ## ## ## ##

if __name__ == "__main__":
    for i, teste in enumerate(test_cases, start=1):
        descricao = teste["description"]
        algebra = teste["expected_ra"]
        print(f"\n🧪 Testando {descricao}...")
        gerar_imagens(algebra, f"arvore_{descricao.lower()}")