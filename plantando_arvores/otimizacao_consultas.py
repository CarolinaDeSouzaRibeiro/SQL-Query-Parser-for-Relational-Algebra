from .arvore import NoArvore
from .processamento_consultas import processar, desenhar_arvore
from pathlib import Path
import sqlite3
from graphviz import Digraph
from pathlib import Path

__base_dir: Path = Path(__file__).resolve().parent
__raiz_projeto = __base_dir
while not (__raiz_projeto / "banco_de_dados").exists() and __raiz_projeto != __raiz_projeto.parent:
    __raiz_projeto = __raiz_projeto.parent

__caminho_db: Path = __raiz_projeto / "banco_de_dados" / "db_vendas.db"


def obter_tabelas_env_uma_cond(cond: str) -> set[str]:
    """
    Extrai os aliases das tabelas utilizados numa condição.
    Exemplo: "W.ESSN=E.SSN" → {"W", "E"}
    """
    import re
    return set(re.findall(r"\b([A-Z])\.", cond))

def reorganizar_selecoes(raiz: NoArvore) -> NoArvore:
    """
    Move seleções (σ) o mais próximo possível das tabelas às quais pertencem.
    """
    if raiz.operacao.startswith("σ "):
        cond = raiz.operacao[2:].strip()
        tabelas_usadas = obter_tabelas_env_uma_cond(cond)

        # Se a condição depende de apenas uma tabela, devemos descer essa seleção
        if len(tabelas_usadas) == 1:
            filho = raiz.filhos[0]
            filho_otimizado = reorganizar_selecoes(filho)
            for i, neto in enumerate(filho_otimizado.filhos):
                if isinstance(neto, NoArvore):
                    neto_tabelas = coletar_tabelas(neto)
                    if tabelas_usadas.issubset(neto_tabelas):
                        raiz.filhos = [neto]
                        filho_otimizado.filhos[i] = raiz
                        return filho_otimizado
        else:
            # Não pode descer: depende de múltiplas tabelas
            raiz.filhos[0] = reorganizar_selecoes(raiz.filhos[0])
    else:
        # Aplicar recursivamente nos filhos
        raiz.filhos = [reorganizar_selecoes(f) for f in raiz.filhos]
    return raiz

def coletar_tabelas(no: NoArvore) -> set[str]:
    """
    Retorna um conjunto com os aliases das tabelas presentes em uma subárvore.
    """
    if '[' in no.operacao and ']' in no.operacao:
        try:
            alias = no.operacao.split('[')[1].split(']')[0]
            return {alias}
        except IndexError:
            return set()
    tabelas = set()
    for f in no.filhos:
        tabelas.update(coletar_tabelas(f))
    return tabelas

def estimar_tamanho_subarvore(no: NoArvore, conn: sqlite3.Connection) -> int:
    """
    Estima o número de tuplas envolvidas em uma subárvore.
    """
    if '[' in no.operacao and ']' in no.operacao:
        tabela = no.operacao.split('[')[0]
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            return cursor.fetchone()[0]
        except sqlite3.Error:
            return 100000  # fallback alto em caso de erro
    return sum(estimar_tamanho_subarvore(f, conn) for f in no.filhos)

def ordenar_joins_por_tamanho(raiz: NoArvore, conn: sqlite3.Connection) -> NoArvore:
    """
    Reorganiza os filhos das operações de junção (X) com base no tamanho estimado das subárvores.
    """
    if raiz.operacao == "X":
        raiz.filhos = [ordenar_joins_por_tamanho(f, conn) for f in raiz.filhos]
        raiz.filhos.sort(key=lambda no: estimar_tamanho_subarvore(no, conn))
    else:
        raiz.filhos = [ordenar_joins_por_tamanho(f, conn) for f in raiz.filhos]
    return raiz

def otimizar_arvore(raiz: NoArvore) -> NoArvore:
    """
    Aplica os passos de otimização na árvore de álgebra relacional.
    """
    conn = sqlite3.connect(__caminho_db)
    try:
        raiz = reorganizar_selecoes(raiz)
        raiz = ordenar_joins_por_tamanho(raiz, conn)
    finally:
        conn.close()
    return raiz

def gerar_imagem_arvore_otimizada(
    algebra_relacional: str,
    nome_arquivo: str = "arvore_consulta_otimizada",
    formato: str = "png"
) -> None:
    """
    Processa e otimiza uma expressão de álgebra relacional, salvando a árvore visual.

    Args:
        algebra_relacional (str): A expressão de álgebra relacional.
        nome_arquivo (str): Nome do arquivo gerado (sem extensão).
        formato (str): Formato do arquivo de imagem.
    """
    raiz_original = processar(algebra_relacional)
    raiz_otimizada = otimizar_arvore(raiz_original)

    grafico_otimizado: Digraph = desenhar_arvore(raiz_otimizada)
    grafico_otimizado.render(nome_arquivo, format=formato, cleanup=True)

    caminho = Path(__file__).parent / f"{nome_arquivo}.{formato}"
    print(f"✅ Árvore otimizada gerada com sucesso: {caminho}")


if __name__ == "__main__":
    algebra = """
    𝝿[E.LNAME](
       𝛔[(P.PNAME='AQUARIUS') ∧ (P.PNUMBER=W.PNO) ∧ (W.ESSN=E.SSN)](
          (EMPLOYEE[E] ⨝ WORKS_ON[W]) ⨝ PROJECT[P]
       )
    )
    """
    print(__caminho_db)
    gerar_imagem_arvore_otimizada(algebra)