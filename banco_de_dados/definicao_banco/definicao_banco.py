"""
Módulo de gerenciamento do ciclo de vida do banco de dados para testes com dados sintéticos.

Este módulo permite:
- Criar as tabelas e índices do banco de dados `db_vendas.db`;
- Popular o banco com dados gerados artificialmente, de acordo com uma configuração de volume;
- Excluir registros e índices existentes;
- Verificar se o banco está vazio;
- Executar scripts SQL localizados em subpastas organizadas por tipo (`criacao/`, `exclusao/`, `configuracoes/`).

Esse fluxo automatizado é útil para testes de performance, simulações de carga e desenvolvimento de aplicações com banco de dados SQLite.

Requisitos:
- Os arquivos `.sql` devem estar nas subpastas corretas do diretório do script.
- Bibliotecas: tqdm
"""

from .geracao_dados import definir_configuracoes
import sqlite3
from pathlib import Path
from tqdm import tqdm

__base_dir: Path = Path(__file__).parent
__caminho_db: Path = __base_dir.parent / "db_vendas.db"

def executar_script_sql(nome_dir: str, nome_arquivo: str, ver_progresso: bool = True) -> None:
    """
    Executa um script SQL localizado em um subdiretório específico.

    Args:
        nome_dir (str): Nome do diretório onde está o script (ex: 'criacao', 'exclusao', 'configuracoes').
        nome_arquivo (str): Nome do arquivo SQL (sem extensão).
        ver_progresso (bool): Se True, exibe barra de progresso simbólica.

    Raises:
        FileNotFoundError: Se o arquivo .sql não for encontrado.
    """
    caminho_sql: Path = __base_dir / nome_dir.lower() / f"{nome_arquivo.lower()}.sql"

    if ver_progresso:
        tqdm.write(f"🚀 Executando: {nome_dir}/{nome_arquivo}.sql")
        with tqdm(total=1, desc=f"{nome_arquivo}", bar_format="{desc} [{elapsed} ✔]") as barra:
            with sqlite3.connect(__caminho_db) as conn:
                with caminho_sql.open("r", encoding="utf-8") as f:
                    script_sql: str = f.read()
                conn.executescript(script_sql)
                barra.update(1)
    else:
        with sqlite3.connect(__caminho_db) as conn:
            with caminho_sql.open("r", encoding="utf-8") as f:
                script_sql: str = f.read()
            conn.executescript(script_sql)

def criar_tabelas(ver_progresso: bool = True) -> None:
    """
    Cria as tabelas do banco de dados executando o script SQL correspondente.
    """
    executar_script_sql("criacao", "tabelas", ver_progresso)

def criar_indexes(ver_progresso: bool = True) -> None:
    """
    Cria os índices do banco de dados executando o script SQL correspondente.
    """
    executar_script_sql("criacao", "indexes", ver_progresso)

def excluir_registros(ver_progresso: bool = True) -> None:
    """
    Exclui todos os registros das tabelas do banco de dados.
    """
    executar_script_sql("exclusao", "registros", ver_progresso)

def excluir_indexes(ver_progresso: bool = True) -> None:
    """
    Remove os índices existentes do banco de dados.
    """
    executar_script_sql("exclusao", "indexes", ver_progresso)

def banco_esta_vazio() -> bool:
    """
    Verifica se o banco de dados está vazio, ou seja, se não possui nenhuma tabela.

    Returns:
        bool: True se não houver tabelas no banco, False caso contrário.
    """
    with sqlite3.connect(__caminho_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        return len(tabelas) == 0

def popular_db(configuracao: int, ver_progresso: bool = True) -> None:
    """
    Popula o banco de dados com dados sintéticos com base na configuração escolhida.

    Etapas:
    - Verifica se o script SQL correspondente à configuração existe e está preenchido;
    - Gera o script, se necessário, utilizando o módulo `geracao_dados`;
    - Cria as tabelas se o banco estiver vazio, ou limpa os dados e índices se não estiver;
    - Executa o script de inserção de dados com barra de progresso (opcional);
    - Recria os índices após a carga.

    Args:
        configuracao (int): Número da configuração (1 a 4).
        ver_progresso (bool): Se True, exibe barra de progresso durante a geração e execução do script.

    Raises:
        ValueError: Se o número da configuração estiver fora do intervalo permitido.
    """
    if not 1 <= configuracao <= 4:
        raise ValueError(f"O número da configuração deve ser entre 1 e 4. Configuração passada como argumento: {configuracao = }")

    nome_dir: str = "configuracoes"
    nome_arquivo: str = f"configuracao{configuracao}"
    caminho_sql = __base_dir / nome_dir / f"{nome_arquivo}.sql"

    if not caminho_sql.exists() or caminho_sql.stat().st_size == 0:
        definir_configuracoes(ver_progresso=ver_progresso)

    if banco_esta_vazio():
        criar_tabelas()
    else:
        excluir_indexes()
        excluir_registros()

    if ver_progresso:
        tqdm.write(f"📥 Executando script de inserção: {caminho_sql.name}")
        with sqlite3.connect(__caminho_db) as conn:
            with caminho_sql.open("r", encoding="utf-8") as f:
                linhas = f.readlines()
                for linha in tqdm(linhas, desc="Inserindo dados", unit="linha"):
                    conn.execute(linha)
            conn.commit()
    else:
        executar_script_sql(nome_dir, nome_arquivo)

    criar_indexes()

    if ver_progresso:
        tqdm.write("✅ Banco populado com sucesso!")