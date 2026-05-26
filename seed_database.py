import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from argon2 import PasswordHasher

from database import (
    adicionar_coluna_data_limite,
    adicionar_coluna_responsavel_chamado,
    adicionar_coluna_usuario_historico,
    criar_tabela_anexos,
    criar_tabela_chamados,
    criar_tabela_comentarios,
    criar_tabela_historico,
    criar_tabela_usuarios,
)


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(
    os.environ.get(
        "DATABASE_PATH",
        BASE_DIR / "chamados.db"
    )
)
DEMO_PASSWORD = "Demo@1234"


USUARIOS_EQUIPE = [
    ("Administrador Demo", "admin@demo.com", "admin"),
    ("Marina Suporte", "suporte1@demo.com", "suporte"),
    ("Rafael Suporte", "suporte2@demo.com", "suporte"),
]

CLIENTES = [
    ("Ana Martins", "ana.martins@demo.com"),
    ("Bruno Almeida", "bruno.almeida@demo.com"),
    ("Carla Souza", "carla.souza@demo.com"),
    ("Diego Pereira", "diego.pereira@demo.com"),
    ("Elisa Fernandes", "elisa.fernandes@demo.com"),
    ("Fabio Rocha", "fabio.rocha@demo.com"),
    ("Gabriela Lima", "gabriela.lima@demo.com"),
    ("Henrique Costa", "henrique.costa@demo.com"),
    ("Isabela Ramos", "isabela.ramos@demo.com"),
    ("Joao Carvalho", "joao.carvalho@demo.com"),
    ("Larissa Gomes", "larissa.gomes@demo.com"),
    ("Marcelo Nunes", "marcelo.nunes@demo.com"),
    ("Natalia Ribeiro", "natalia.ribeiro@demo.com"),
    ("Otavio Mendes", "otavio.mendes@demo.com"),
    ("Patricia Castro", "patricia.castro@demo.com"),
    ("Renato Barbosa", "renato.barbosa@demo.com"),
    ("Sofia Teixeira", "sofia.teixeira@demo.com"),
    ("Tiago Moreira", "tiago.moreira@demo.com"),
    ("Vanessa Cardoso", "vanessa.cardoso@demo.com"),
    ("William Araujo", "william.araujo@demo.com"),
]

TITULOS = [
    "Erro ao acessar o sistema",
    "Solicitacao de troca de senha",
    "Tela carregando lentamente",
    "Divergencia em informacoes do cadastro",
    "Falha ao anexar documento",
    "Pedido de ajuste de permissao",
    "Notificacao nao recebida",
    "Relatorio com dados incompletos",
    "Duvida sobre acompanhamento do chamado",
    "Problema ao atualizar dados pessoais",
]

DESCRICOES = [
    "Usuario informa que a acao nao foi concluida e solicita verificacao da equipe.",
    "Cliente relata comportamento diferente do esperado durante o uso da plataforma.",
    "Solicitacao registrada para avaliacao tecnica e retorno do suporte.",
    "Chamado criado para simular um atendimento real no ambiente de demonstracao.",
]

RESPOSTAS = {
    "Em andamento": "Atendimento iniciado. A equipe esta analisando as informacoes enviadas.",
    "Resolvido": "Solicitacao resolvida pela equipe de suporte. Cliente pode validar o atendimento.",
    "Encerrado": "Chamado encerrado apos conclusao e registro das informacoes do atendimento.",
}


def preparar_banco():
    os.chdir(BASE_DIR)

    if DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    criar_tabela_usuarios()
    criar_tabela_chamados()
    criar_tabela_historico()
    criar_tabela_comentarios()
    adicionar_coluna_data_limite()
    criar_tabela_anexos()
    adicionar_coluna_usuario_historico()
    adicionar_coluna_responsavel_chamado()


def inserir_usuarios(cursor):
    ph = PasswordHasher()
    ids = {}

    for nome, email, tipo in USUARIOS_EQUIPE:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
            """,
            (nome, email, ph.hash(DEMO_PASSWORD), tipo),
        )
        ids[email] = cursor.lastrowid

    for nome, email in CLIENTES:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
            """,
            (nome, email, ph.hash(DEMO_PASSWORD), "cliente"),
        )
        ids[email] = cursor.lastrowid

    return ids


def data_formatada(data):
    return data.strftime("%d/%m/%Y %H:%M")


def data_sql(data):
    return data.strftime("%Y-%m-%d %H:%M:%S")


def inserir_chamados(cursor, ids):
    suporte_ids = [
        ids["suporte1@demo.com"],
        ids["suporte2@demo.com"],
        ids["admin@demo.com"],
    ]

    status_opcoes = [
        "Aberto",
        "Em andamento",
        "Resolvido",
        "Encerrado",
    ]
    prioridade_opcoes = [
        "Baixa",
        "M\u00e9dia",
        "Alta",
    ]

    agora = datetime.now().replace(second=0, microsecond=0)

    for indice, (_, email_cliente) in enumerate(CLIENTES, start=1):
        quantidade = 2 if indice <= 10 else 1

        for extra in range(quantidade):
            ticket_numero = indice + extra
            status = status_opcoes[(indice + extra) % len(status_opcoes)]
            prioridade = prioridade_opcoes[(indice + extra) % len(prioridade_opcoes)]
            data_abertura = agora - timedelta(days=indice + extra, hours=extra * 3)

            if prioridade == "Alta":
                data_limite = data_abertura + timedelta(hours=4)
            elif prioridade == "M\u00e9dia":
                data_limite = data_abertura + timedelta(hours=24)
            else:
                data_limite = data_abertura + timedelta(hours=72)

            responsavel_id = None
            if status != "Aberto" or indice % 3 == 0:
                responsavel_id = suporte_ids[(indice + extra) % len(suporte_ids)]

            resposta = RESPOSTAS.get(status, "")

            cursor.execute(
                """
                INSERT INTO chamados (
                    titulo,
                    descricao,
                    status,
                    prioridade,
                    usuario_id,
                    resposta,
                    data_criacao,
                    data_limite,
                    responsavel_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    TITULOS[(ticket_numero - 1) % len(TITULOS)],
                    DESCRICOES[(ticket_numero - 1) % len(DESCRICOES)],
                    status,
                    prioridade,
                    ids[email_cliente],
                    resposta,
                    data_formatada(data_abertura),
                    data_sql(data_limite),
                    responsavel_id,
                ),
            )

            chamado_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO historico_chamados (chamado_id, usuario_id, mensagem, data)
                VALUES (?, ?, ?, ?)
                """,
                (
                    chamado_id,
                    ids[email_cliente],
                    "Chamado criado pelo usuario",
                    data_formatada(data_abertura),
                ),
            )

            if responsavel_id:
                cursor.execute(
                    """
                    INSERT INTO historico_chamados (chamado_id, usuario_id, mensagem, data)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        chamado_id,
                        responsavel_id,
                        "Atendimento assumido pela equipe de suporte",
                        data_formatada(data_abertura + timedelta(hours=1)),
                    ),
                )

            if resposta:
                cursor.execute(
                    """
                    INSERT INTO historico_chamados (chamado_id, usuario_id, mensagem, data)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        chamado_id,
                        responsavel_id,
                        f"Status atualizado para {status}",
                        data_formatada(data_abertura + timedelta(hours=2)),
                    ),
                )

            if indice % 2 == 0:
                cursor.execute(
                    """
                    INSERT INTO comentarios_chamados (chamado_id, usuario_id, mensagem, data)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        chamado_id,
                        ids[email_cliente],
                        "Comentario ficticio do cliente para complementar o atendimento.",
                        data_formatada(data_abertura + timedelta(minutes=30)),
                    ),
                )

            if responsavel_id and indice % 2 == 0:
                cursor.execute(
                    """
                    INSERT INTO comentarios_chamados (chamado_id, usuario_id, mensagem, data)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        chamado_id,
                        responsavel_id,
                        "Retorno ficticio da equipe com orientacoes ao cliente.",
                        data_formatada(data_abertura + timedelta(hours=2, minutes=20)),
                    ),
                )


def criar_banco_demo():
    preparar_banco()

    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    ids = inserir_usuarios(cursor)
    inserir_chamados(cursor, ids)

    conexao.commit()
    conexao.close()

    return DB_PATH


def main():
    criar_banco_demo()

    print("Banco ficticio criado com sucesso.")
    print("Usuarios: 1 admin, 2 suportes e 20 clientes.")
    print("Senha de todos os usuarios demo: Demo@1234")
    print("Admin: admin@demo.com")
    print("Suporte 1: suporte1@demo.com")
    print("Suporte 2: suporte2@demo.com")


if __name__ == "__main__":
    main()
