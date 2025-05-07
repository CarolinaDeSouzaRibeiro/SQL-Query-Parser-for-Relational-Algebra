import gradio as gr
import graphviz as gv
from plantando_arvores.processamento_consultas import processar, gerar_imagem_arvore_processada, desenhar_arvore
from plantando_arvores.teste_otimizador import gerar_grafo_otimizado
# from novo_plantando_arvores.processamento import gerar_imagem_arvore_processada
from parser import process_sql_query

def funcao_btn(comando):
    #CHECAGEM DA VALIDADE DO COMANDO SQL
    try:
        algebra_relacional = process_sql_query(comando)

        #se o resultado for um erro:
        if type(algebra_relacional) in [ValueError,KeyError]:
            raise gr.Error()
    except Exception as e:
        raise gr.Error(f'Comando SQL inválido: {str(algebra_relacional)}')

    ### GRAFOS
    #não-otimizado
    try:
        gerar_imagem_arvore_processada(algebra_relacional)#prepara grafos
    except Exception as e:
        raise gr.Error('Erro na geração do grafo não-otimizado.\nCertifique-se que os executáveis do Graphviz estão instalados e no seu PATH') from e
    #otimizado
    try:
        gerar_grafo_otimizado(algebra_relacional)
    except Exception as e:
        raise gr.Error('Erro na geração do grafo otimizado.\nCertifique-se que os executáveis do Graphviz estão instalados e no seu PATH') from e

    # return algebra_relacional, 'img/arvore_processada.png', 'img/arvore_otimizada.png'
    return algebra_relacional, 'arvore_consulta_processada.png', 'arvore_consulta_otimizada.png'

with gr.Blocks() as demo:
    gr.Markdown("## Processador de consultas")
    with gr.Row():
        with gr.Column():
            cmd_sql = gr.Textbox(label="Comando SQL")
            btn = gr.Button("Submit")
        with gr.Column():
            gr.Markdown("## Algebra Relacional")
            algeb_relac = gr.Textbox(label="Algebra Relacional")
            algeb_relac.interactive = False # desabilita edição do campo de algebra relacional

            gr.Markdown("## Grafos")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("Grafo não-otimizado")
                    grafo = gr.Image(label="Não-Otimizado")
                with gr.Column():
                    gr.Markdown("Grafo otimizado")
                    grafo_otim = gr.Image(label="Otimizado")
            # grafo = gr.Image(label="Não-Otimizado")
            # grafo_otim = gr.Image(label="Otimizado")

        #comando do botao
        btn.click(funcao_btn, inputs=[cmd_sql], outputs=[algeb_relac, grafo, grafo_otim])

demo.launch()