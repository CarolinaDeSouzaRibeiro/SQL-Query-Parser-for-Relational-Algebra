# ProcConsultas

## Descrição

Este repositório contém um conjunto de scripts em Python para gerenciamento de um banco de dados de vendas, geração de dados sintéticos, processamento de consultas SQL e visualização de árvores de álgebra relacional. O objetivo principal é fornecer uma ferramenta para testes de performance, simulações de carga e desenvolvimento de aplicações com banco de dados SQLite.

## Índice

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

## Contribuindo

Se você deseja contribuir com o projeto, siga as diretrizes abaixo:

1. Faça um fork do repositório.
2. Crie uma nova branch para sua feature ou correção de bug:
   ```sh
   git checkout -b minha-feature
   ```
3. Faça commit das suas alterações:
   ```sh
   git commit -m 'Adiciona minha feature'
   ```
4. Envie para o branch original:
   ```sh
   git push origin minha-feature
   ```
5. Crie um pull request.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
