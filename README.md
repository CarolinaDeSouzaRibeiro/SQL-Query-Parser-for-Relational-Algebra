# ProcConsultas

## Introduction

This project was developed as part of the Database subject, fulfilling the challenge proposed by the teacher: Implement an SQL query processor capable of analizing, validating, optimizing and vizualizing queries about a relational database on sales. The system parses restricted SQL commands, converts them into relational algebra, builds its corresponding operation tree, applies optimization heuristics(such as selection pushdown and projections) and generates gera graphic vizualizations of the trees before and after optimization. 

The objective is to demonstrate, in a practical and visual manner, the inner working of a query processor, as per the proposed requirements.

## Index

- [ProcConsultas](#procconsultas)
  - [Introdução](#introdução)
  - [Índice](#índice)
  - [Instalação](#instalação)
  - [Uso](#uso)
  - [Estrutura do Diretório](#estrutura-do-diretório)
  - [Contribuindo](#contribuindo)
  - [Licença](#licença)

## Installation

To install and configure the project, follow the following steps: 

1. Clone the repository:
   ```sh
   git clone https://github.com/C-dS-R/ProcConsultas.git
   cd ProcConsultas
   ```

2. Create a virtual ambient and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
   ```

3. Install its dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Use

Here are some exemples and explainations on using this project:

1. In order to generate synthetic data, to populate the database:
   ```sh
   python banco_de_dados/definicao_banco/definicao_banco.py
   ```

2. To process an SQL query and generate a relational algebra tree:
   ```sh
   python main.py
   ```

## Folder Structure

An overview of the project directory's structure:

```
ProcConsultas/
├── banco_de_dados/
│   ├── db_vendas.db
│   └── definicao_banco/
│       ├── configuracoes/
│       ├── criacao/
│       ├── exclusao/
│       ├── geracao_dados.py
│       └── definicao_banco.py
├── docs/
│   ├── README.md
│   ├── definicao_banco.md
│   ├── geracao_dados.md
│   ├── main.md
│   ├── parser.md
│   ├── arvore.md
│   ├── desmatamento.md
│   ├── otimizacao_consultas.md
│   └── processamento_consultas.md
├── main.py
├── parser.py
├── plantando_arvores/
│   ├── arvore.py
│   ├── desmatamento.py
│   ├── otimizacao_consultas.py
│   └── processamento_consultas.py
└── requirements.txt
```

## Introdução

Este projeto foi desenvolvido como parte da disciplina de Banco de Dados, atendendo ao desafio proposto pelo professor: implementar um processador de consultas SQL capaz de analisar, validar, otimizar e visualizar consultas sobre um banco de dados relacional de vendas. O sistema realiza o parsing de comandos SQL restritos, converte-os para álgebra relacional, constrói a árvore de operadores correspondente, aplica heurísticas de otimização (como pushdown de seleções e projeções) e gera visualizações gráficas das árvores antes e depois da otimização.

O objetivo é demonstrar, de forma prática e visual, o funcionamento interno de um processador de consultas, conforme os requisitos do projeto 2 da disciplina.

## Índice

- [ProcConsultas](#procconsultas)
  - [Introdução](#introdução)
  - [Índice](#índice)
  - [Instalação](#instalação)
  - [Uso](#uso)
  - [Estrutura do Diretório](#estrutura-do-diretório)
  - [Contribuindo](#contribuindo)
  - [Licença](#licença)

## Instalação

Para instalar e configurar o projeto, siga os passos abaixo:

1. Clone o repositório:
   ```sh
   git clone https://github.com/C-dS-R/ProcConsultas.git
   cd ProcConsultas
   ```

2. Crie um ambiente virtual e ative-o:
   ```sh
   python -m venv venv
   source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
   ```

3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

## Uso

Aqui estão alguns exemplos e explicações sobre como usar o projeto:

1. Para gerar dados sintéticos e popular o banco de dados:
   ```sh
   python banco_de_dados/definicao_banco/definicao_banco.py
   ```

2. Para processar uma consulta SQL e gerar a árvore de álgebra relacional:
   ```sh
   python main.py
   ```

## Estrutura do Diretório

Uma visão geral da estrutura do diretório do projeto:

```
ProcConsultas/
├── banco_de_dados/
│   ├── db_vendas.db
│   └── definicao_banco/
│       ├── configuracoes/
│       ├── criacao/
│       ├── exclusao/
│       ├── geracao_dados.py
│       └── definicao_banco.py
├── docs/
│   ├── README.md
│   ├── definicao_banco.md
│   ├── geracao_dados.md
│   ├── main.md
│   ├── parser.md
│   ├── arvore.md
│   ├── desmatamento.md
│   ├── otimizacao_consultas.md
│   └── processamento_consultas.md
├── main.py
├── parser.py
├── plantando_arvores/
│   ├── arvore.py
│   ├── desmatamento.py
│   ├── otimizacao_consultas.py
│   └── processamento_consultas.py
└── requirements.txt
```
