import gradio as gr

# def test(name):
#     return f"Hello {name}"

####OBS: Esta é uma funcionalidade extra que não necessita ser implementada

#usando objeto de teste para representar as tables. TODO: ver como melhorar, e se deve utilizar POO
tabelas = [
    {
        'table_name': "table1",
        'table_params': [
            {'param_name': 'param1', 'param_type':'type', 'param_value': 'description1'},
        ]
    },

    {
        'table_name': "table2",
        'table_params': [
            {'param_name': 'param1', 'param_type':'type', 'param_value': 'value1'},
            {'param_name': 'param2', 'param_type':'type', 'param_value': 'value2'},
            {'param_name': 'param3', 'param_type':'type', 'param_value': 'value2'},
        ]
    },
    {
        'table_name': "table3",
        'table_params': [
            {'param_name': 'param1', 'param_type':'type', 'param_value': 'value1'},
            {'param_name': 'param2', 'param_type':'type', 'param_value': 'value2'},
            {'param_name': 'param3', 'param_type':'type', 'param_value': 'value3'},
            {'param_name': 'param4', 'param_type':'type', 'param_value': 'value4'},
            {'param_name': 'param5', 'param_type':'type', 'param_value': 'value5'},
        ]
    },
    {
        'table_name': "table4",
        'table_params': [
            {'param_name': 'param1', 'param_type':'type', 'param_value': 'value1'},
            {'param_name': 'param2', 'param_type':'type', 'param_value': 'value2'},
        ]
    }
]

with gr.Blocks() as demo:
    gr.Markdown("## Config de Tabelas")
    for i in range(len(tabelas)):
        #mostra o widget em tabela['table_name_textbot'], para cada tabela
        with gr.Row():
            with gr.Column():
                gr.Markdown(f"# Tabela {i+1}")
                tabela = tabelas[i]
                tabela['table_name_textbot'] = gr.Textbox(label='Nome da tabela', placeholder=tabela['table_name'])

                #mostra cada parametro da tabela, na mesma coluna
                for j in range(len(tabelas[i]['table_params'])):
                    gr.Markdown(f"#### Parametro {j+1}")
                    param = tabelas[i]['table_params'][j]
                    param['param_name_textbot'] = gr.Textbox(label='Nome do parametro', placeholder=tabelas[i]['table_params'][j]['param_name'])
                    param['param_type_textbot'] = gr.Textbox(label='Tipo do parametro', placeholder=tabelas[i]['table_params'][j]['param_type'])
                    param['param_value_textbot'] = gr.Textbox(label='Valor do parametro', placeholder=tabelas[i]['table_params'][j]['param_value'])

                #quebra de linha entre tabelas
                gr.Markdown("<br><br>")

    # btn = gr.Button("Test")
    # btn.click(test, inputs=[table_name])


demo.launch()