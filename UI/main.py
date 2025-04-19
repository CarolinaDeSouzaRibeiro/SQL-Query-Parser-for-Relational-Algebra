import gradio as gr

def test(comando):
    return f"Seu comando: {comando}",f"Seu comando: {comando}", '<div id="grafo"></div>','<div id="grafo"></div>'


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
            grafo_otim = gr.HTML('')
            grafo = gr.HTML('')

        #comando do botao
        btn.click(test, inputs=[cmd_sql], outputs=[algeb_relac_otim, algeb_relac, grafo_otim, grafo])

demo.launch()