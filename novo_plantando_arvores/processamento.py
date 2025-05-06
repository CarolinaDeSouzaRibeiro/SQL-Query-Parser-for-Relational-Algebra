from .arvore import NoArvore, Arvore, ArvoreDrawer
from .relational_algebra_parser import construir_arvore
from .algebra_utils_clause import remover_joins, formatar_algebra_relacional

def gerar_imagem_arvore_processada(
    consulta: str, 
    nome_arquivo: str = "arvore_processada"
) -> None:
    """
    Gera uma imagem da árvore de operações a partir de uma consulta SQL.

    Args:
        consulta (str): Consulta SQL a ser processada.
        nome_arquivo (str): Nome do arquivo de saída (padrão: "arvore_processada.png").
        formato (str): Formato da imagem de saída (padrão: "png").
    """
    consulta = formatar_algebra_relacional(consulta)
    print(f"Consulta formatada: \n{consulta}")
    # consulta = remover_joins(consulta)
    # print(f"Consulta sem joins: \n{consulta}")
    arvore = construir_arvore(consulta)
    arvore_desenho = ArvoreDrawer(arvore)
    arvore_desenho.desenhar(nome_arquivo)
    
if __name__ == "__main__":
    consulta = expr = '''𝝿[C.Nome, E.CEP, P.Status](
       𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
            (
              (Cliente[C]) ⨝[C.idCliente = P.Cliente_idCliente] (Pedido[P])
            ) ⨝[C.idCliente = E.Cliente_idCliente] (Endereco[E])
       )
    )'''
    gerar_imagem_arvore_processada(consulta, "arvore_consulta_processada.png")
