from .arvore import NoArvore
from .processamento_consultas import processar, desenhar_arvore
from pathlib import Path
import sqlite3
from graphviz import Digraph

# Diretório raiz e caminho do banco
__base_dir: Path = Path(__file__).resolve().parent
__raiz_projeto = __base_dir
while not (__raiz_projeto / "banco_de_dados").exists() and __raiz_projeto != __raiz_projeto.parent:
    __raiz_projeto = __raiz_projeto.parent

__caminho_db: Path = __raiz_projeto / "banco_de_dados" / "db_vendas.db"