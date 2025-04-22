import gradio as gr

def test(comando):
    comando_ordenado = comando
    grafo_otimizado = '<div id="grafo">A</div>'
    grafo = '<div id="grafo">B</div>'
    ordem_execucao = '<div id="ordem"><ol><li>aaa</li><li>bbb</li></ol></div>'

    return f"Seu comando: {comando}", comando_ordenado, grafo_otimizado, grafo, ordem_execucao

with gr.Blocks() as demo:
    gr.Markdown("## Processador de consultas")
    with gr.Row():
        with gr.Column():
            cmd_sql = gr.Textbox(label="Comando SQL")
            btn = gr.Button("Submit")
        with gr.Column():
            gr.Markdown("## Algebra Relacional")
            algeb_relac_otim = gr.Textbox(label="Algebra Relacional (Otimizado)")
            algeb_relac = gr.Textbox(label="Algebra Relacional (Não otimizado)")

            gr.Markdown("## Grafos")
            grafo_otim = gr.HTML()
            grafo = gr.HTML()

            gr.Markdown("## Ordem de execução")
            ordem_exec = gr.HTML()

        #comando do botao
        btn.click(test, inputs=[cmd_sql], outputs=[algeb_relac_otim, algeb_relac, grafo_otim, grafo, ordem_exec])

demo.launch()