import os  # Operações com o sistema de arquivos
from pathlib import Path  # Manipulação de caminhos de arquivos de forma multiplataforma
import random  # Geração de números aleatórios
from faker import Faker  # Geração de dados fictícios realistas
from datetime import datetime, date  # Manipulação de datas
from typing import Any  # Tipagem genérica para maior legibilidade e segurança
from tqdm import tqdm  # Barra de progresso para feedback visual durante execuções demoradas

# Criação do diretório para armazenar os arquivos de configuração gerados
os.makedirs("configuracoes", exist_ok=True)

# Inicialização do gerador de dados fictícios com localização brasileira
fake: Faker = Faker(locale='pt_BR')

# Dicionário contendo as configurações de volume de dados para diferentes cenários de testes
configuracoes: dict[str, dict[str, int]] = {
    "configuracao1": {"Categoria": 20, "Produto": 50000, "TipoCliente": 5, "Cliente": 50000,
                      "TipoEndereco": 5, "Endereco": 50000, "Telefone": 50000, "Status": 5,
                      "Pedido": 100000, "Pedido_has_Produto": 200000},
    "configuracao2": {"Categoria": 30, "Produto": 30000, "TipoCliente": 6, "Cliente": 80000,
                      "TipoEndereco": 6, "Endereco": 80000, "Telefone": 80000, "Status": 6,
                      "Pedido": 150000, "Pedido_has_Produto": 300000},
    "configuracao3": {"Categoria": 15, "Produto": 40000, "TipoCliente": 4, "Cliente": 40000,
                      "TipoEndereco": 4, "Endereco": 40000, "Telefone": 40000, "Status": 4,
                      "Pedido": 300000, "Pedido_has_Produto": 500000},
    "configuracao4": {"Categoria": 10, "Produto": 100000, "TipoCliente": 3, "Cliente": 10000,
                      "TipoEndereco": 2, "Endereco": 10000, "Telefone": 10000, "Status": 3,
                      "Pedido": 50000, "Pedido_has_Produto": 150000},
}

def sql_str(val: Any) -> str:
    """
    Converte valores em representações seguras para uso em instruções SQL.

    Args:
        val (Any): Valor a ser convertido.

    Returns:
        str: Representação segura do valor, com aspas se for string.
    """
    return f"'{val}'" if isinstance(val, str) else str(val)


def definir_configuracoes(ver_progresso: bool = True) -> None:
    """
    Gera arquivos SQL contendo comandos de inserção de dados para diferentes configurações de volume.

    Cada configuração especifica a quantidade de registros por tabela.
    Os arquivos gerados são salvos na pasta `configuracoes/`.

    Args:
        ver_progresso (bool): Se True, exibe barra de progresso durante a geração.
    """
    global fake, configuracoes

    # Iterador que pode ou não exibir barra de progresso dependendo do parâmetro
    iterador_config: Any = tqdm(configuracoes.items(), desc="Configurações", leave=True) if ver_progresso else configuracoes.items()

    for nome_cfg, cfg in iterador_config:
        # Determina o caminho do arquivo de saída .sql
        base_dir: Path = Path(__file__).parent
        caminho: Path = base_dir / "configuracoes" / f"{nome_cfg}.sql"
        conteudos_arquivo: list[str] = []

        if ver_progresso:
            tqdm.write(f"🔧 Gerando arquivo: {caminho}")

        conteudos_arquivo.append("BEGIN TRANSACTION;\n\n")

        # Função interna que encapsula o uso de barra de progresso opcional
        def range_progress(total: int, desc: str) -> Any:
            return tqdm(range(total), desc=desc, leave=False) if ver_progresso else range(total)

        # ========== GERAÇÃO DE DADOS PARA CADA TABELA ==========

        for i in range_progress(cfg["TipoCliente"], "TipoCliente"):
            conteudos_arquivo.append(f"INSERT INTO TipoCliente VALUES ({i + 1}, 'Tipo {i + 1}');\n")

        for i in range_progress(cfg["TipoEndereco"], "TipoEndereco"):
            conteudos_arquivo.append(f"INSERT INTO TipoEndereco VALUES ({i + 1}, 'Tipo {i + 1}');\n")

        for i in range_progress(cfg["Categoria"], "Categoria"):
            conteudos_arquivo.append(f"INSERT INTO Categoria VALUES ({i + 1}, 'Categoria {i + 1}');\n")

        for i in range_progress(cfg["Status"], "Status"):
            conteudos_arquivo.append(f"INSERT INTO Status VALUES ({i + 1}, 'Status {i + 1}');\n")

        for i in range_progress(cfg["Produto"], "Produto"):
            preco: float = round(random.uniform(10, 1000), 2)
            estoque_max: int = 200
            estoque: int = random.randint(1, estoque_max)
            cat: int = random.randint(1, cfg["Categoria"])
            conteudos_arquivo.append(
                f"INSERT INTO Produto VALUES ({i + 1}, 'Produto {i + 1}', 'Descricao do produto {i + 1}', {preco}, {estoque}, {cat});\n"
            )

        for i in range_progress(cfg["Cliente"], "Cliente"):
            nome: str = fake.name().replace("'", "''")
            email: str = fake.email()
            nascimento: date = fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
            senha: str = fake.password(length=10)
            tipo: int = random.randint(1, cfg["TipoCliente"])
            data_reg: str = datetime.now().isoformat()
            conteudos_arquivo.append(
                f"INSERT INTO Cliente VALUES ({i + 1}, '{nome}', '{email}', '{nascimento}', '{senha}', {tipo}, '{data_reg}');\n"
            )

        for i in range_progress(cfg["Endereco"], "Endereco"):
            cliente: int = random.randint(1, cfg["Cliente"])
            tipo_end: int = random.randint(1, cfg["TipoEndereco"])
            logradouro: str = fake.street_name().replace("'", "''")
            numero: str = fake.building_number()
            complemento: str = ""  # foi decidido que ninguém terá complemento
            bairro: str = fake.bairro().replace("'", "''")
            cidade: str = fake.city().replace("'", "''")
            uf: str = fake.estado_sigla()
            cep: str = fake.postcode().replace("-", "")
            conteudos_arquivo.append(
                f"INSERT INTO Endereco VALUES ({i + 1}, {random.randint(0, 1)}, '{logradouro}', '{numero}', '{complemento}', '{bairro}', '{cidade}', '{uf}', '{cep}', {tipo_end}, {cliente});\n"
            )

        for i in range_progress(cfg["Telefone"], "Telefone"):
            cliente: int = random.randint(1, cfg["Cliente"])
            telefone: str = fake.msisdn()[:11]
            conteudos_arquivo.append(f"INSERT INTO Telefone VALUES ('{telefone}', {cliente});\n")

        for i in range_progress(cfg["Pedido"], "Pedido"):
            status: int = random.randint(1, cfg["Status"])
            cliente: int = random.randint(1, cfg["Cliente"])
            data: str = datetime.now().isoformat()
            total: float = round(random.uniform(50, 2000), 2)
            conteudos_arquivo.append(
                f"INSERT INTO Pedido VALUES ({i + 1}, {status}, '{data}', {total}, {cliente});\n"
            )

        for i in range_progress(cfg["Pedido_has_Produto"], "Pedido_has_Produto"):
            pedido: int = random.randint(1, cfg["Pedido"])
            produto: int = random.randint(1, cfg["Produto"])
            quantidade: float = round(random.uniform(1, 5), 2)
            preco_unit: float = round(random.uniform(10, 1000), 2)
            conteudos_arquivo.append(
                f"INSERT INTO Pedido_has_Produto (Pedido_idPedido, Produto_idProduto, Quantidade, PrecoUnitario) VALUES ({pedido}, {produto}, {quantidade}, {preco_unit});\n"
            )

        # Finalização da transação SQL
        conteudos_arquivo.append("\nCOMMIT;\n")

        # Escrita no arquivo .sql
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(''.join(conteudos_arquivo))

        # Feedback visual de sucesso
        if ver_progresso:
            total_linhas: int = len(conteudos_arquivo)
            tqdm.write(f"✅ Arquivo salvo: {caminho} ({total_linhas:,} linhas)\n")

    if ver_progresso:
        tqdm.write("🟢 Todos os arquivos foram gerados com sucesso!\n")


# Ponto de entrada principal: executa a função somente quando o script é chamado diretamente
if __name__ == '__main__':
    definir_configuracoes()