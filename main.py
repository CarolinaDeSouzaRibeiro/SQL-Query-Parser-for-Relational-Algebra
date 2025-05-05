import gradio as gr
from plantando_arvores.processamento_consultas import gerar_imagem_arvore_processada
from parser import process_sql_query

def funcao_btn(comando):
    #CHECAGEM DA VALIDADE DO COMANDO SQL
    try:
        algebra_relacional = process_sql_query(comando)

        print(f'\nalgebra relacional tipo: {type(algebra_relacional)}\n\n')

        #se o resultado for um erro:
        if type(algebra_relacional) in [ValueError,KeyError]:
            raise gr.Error()
    except Exception as e:
        raise gr.Error(f'Comando SQL inválido: {str(algebra_relacional)}')

    #GRAFOS
    try:
        gerar_imagem_arvore_processada(algebra_relacional)#prepara grafos
    except Exception as e:
        raise gr.Error('Erro na geração do grafo.\nCertifique-se que os executáveis do Graphviz estão instalados e no seu PATH') from e

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
            grafo = gr.Image(label="Não-Otimizado")
            grafo_otim = gr.Image(label="Otimizado")

        #comando do botao
        btn.click(funcao_btn, inputs=[cmd_sql], outputs=[algeb_relac, grafo, grafo_otim])

demo.launch()