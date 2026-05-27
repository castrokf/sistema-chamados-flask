import os
from datetime import datetime, timedelta
from pathlib import Path

from argon2 import PasswordHasher

from database import (
    executar,
    inicializar_banco,
    inserir_e_retornar_id,
    obter_database_url,
    obter_organizacao_padrao_id,
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
    "Usuario relata comportamento diferente do esperado durante o uso da plataforma.",
    "Solicitacao registrada para avaliacao tecnica e retorno do suporte.",
    "Chamado criado para simular um atendimento real no ambiente de demonstracao.",
]

RESPOSTAS = {
    "Em andamento": "Atendimento iniciado. A equipe esta analisando as informacoes enviadas.",
    "Resolvido": "Solicitacao resolvida pela equipe de suporte. Usuario pode validar o atendimento.",
    "Encerrado": "Chamado encerrado apos conclusao e registro das informacoes do atendimento.",
}


def usando_sqlite_local():
    return obter_database_url().startswith("sqlite")


def limpar_tabelas_demo():
    for tabela in [
        "anexos_chamados",
        "comentarios_chamados",
        "historico_chamados",
        "recuperacao_senha",
        "chamados",
        "usuarios",
        "organizacoes",
    ]:
        executar(f"DELETE FROM {tabela}")


def preparar_banco(recriar=True):
    os.chdir(BASE_DIR)

    if recriar and usando_sqlite_local() and DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    inicializar_banco()

    if recriar and not usando_sqlite_local():
        limpar_tabelas_demo()

    return obter_organizacao_padrao_id()


def inserir_usuarios(organizacao_id):
    ph = PasswordHasher()
    ids = {}

    for nome, email, tipo in USUARIOS_EQUIPE:
        usuario_id = inserir_e_retornar_id("""
        INSERT INTO usuarios (
            organizacao_id,
            nome,
            email,
            senha,
            tipo,
            ativo,
            data_criacao
        )
        VALUES (
            :organizacao_id,
            :nome,
            :email,
            :senha,
            :tipo,
            1,
            :data_criacao
        )
        """, {
            "organizacao_id": organizacao_id,
            "nome": nome,
            "email": email,
            "senha": ph.hash(DEMO_PASSWORD),
            "tipo": tipo,
            "data_criacao": data_sql(datetime.now()),
        })
        ids[email] = usuario_id

    for nome, email in CLIENTES:
        usuario_id = inserir_e_retornar_id("""
        INSERT INTO usuarios (
            organizacao_id,
            nome,
            email,
            senha,
            tipo,
            ativo,
            data_criacao
        )
        VALUES (
            :organizacao_id,
            :nome,
            :email,
            :senha,
            'cliente',
            1,
            :data_criacao
        )
        """, {
            "organizacao_id": organizacao_id,
            "nome": nome,
            "email": email,
            "senha": ph.hash(DEMO_PASSWORD),
            "data_criacao": data_sql(datetime.now()),
        })
        ids[email] = usuario_id

    return ids


def data_formatada(data):
    return data.strftime("%d/%m/%Y %H:%M")


def data_sql(data):
    return data.strftime("%Y-%m-%d %H:%M:%S")


def inserir_chamados(ids, organizacao_id):
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
        "Média",
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
            elif prioridade == "Média":
                data_limite = data_abertura + timedelta(hours=24)
            else:
                data_limite = data_abertura + timedelta(hours=72)

            responsavel_id = None

            if status != "Aberto" or indice % 3 == 0:
                responsavel_id = suporte_ids[(indice + extra) % len(suporte_ids)]

            resposta = RESPOSTAS.get(status, "")

            chamado_id = inserir_e_retornar_id("""
            INSERT INTO chamados (
                organizacao_id,
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
            VALUES (
                :organizacao_id,
                :titulo,
                :descricao,
                :status,
                :prioridade,
                :usuario_id,
                :resposta,
                :data_criacao,
                :data_limite,
                :responsavel_id
            )
            """, {
                "organizacao_id": organizacao_id,
                "titulo": TITULOS[(ticket_numero - 1) % len(TITULOS)],
                "descricao": DESCRICOES[(ticket_numero - 1) % len(DESCRICOES)],
                "status": status,
                "prioridade": prioridade,
                "usuario_id": ids[email_cliente],
                "resposta": resposta,
                "data_criacao": data_formatada(data_abertura),
                "data_limite": data_sql(data_limite),
                "responsavel_id": responsavel_id,
            })

            executar("""
            INSERT INTO historico_chamados (
                chamado_id,
                usuario_id,
                mensagem,
                data
            )
            VALUES (
                :chamado_id,
                :usuario_id,
                :mensagem,
                :data
            )
            """, {
                "chamado_id": chamado_id,
                "usuario_id": ids[email_cliente],
                "mensagem": "Chamado criado pelo usuario",
                "data": data_formatada(data_abertura),
            })

            if responsavel_id:
                executar("""
                INSERT INTO historico_chamados (
                    chamado_id,
                    usuario_id,
                    mensagem,
                    data
                )
                VALUES (
                    :chamado_id,
                    :usuario_id,
                    :mensagem,
                    :data
                )
                """, {
                    "chamado_id": chamado_id,
                    "usuario_id": responsavel_id,
                    "mensagem": "Atendimento assumido pela equipe de suporte",
                    "data": data_formatada(data_abertura + timedelta(hours=1)),
                })

            if resposta:
                executar("""
                INSERT INTO historico_chamados (
                    chamado_id,
                    usuario_id,
                    mensagem,
                    data
                )
                VALUES (
                    :chamado_id,
                    :usuario_id,
                    :mensagem,
                    :data
                )
                """, {
                    "chamado_id": chamado_id,
                    "usuario_id": responsavel_id,
                    "mensagem": f"Status atualizado para {status}",
                    "data": data_formatada(data_abertura + timedelta(hours=2)),
                })

            if indice % 2 == 0:
                executar("""
                INSERT INTO comentarios_chamados (
                    chamado_id,
                    usuario_id,
                    mensagem,
                    data
                )
                VALUES (
                    :chamado_id,
                    :usuario_id,
                    :mensagem,
                    :data
                )
                """, {
                    "chamado_id": chamado_id,
                    "usuario_id": ids[email_cliente],
                    "mensagem": "Comentario ficticio do usuario para complementar o atendimento.",
                    "data": data_formatada(data_abertura + timedelta(minutes=30)),
                })

            if responsavel_id and indice % 2 == 0:
                executar("""
                INSERT INTO comentarios_chamados (
                    chamado_id,
                    usuario_id,
                    mensagem,
                    data
                )
                VALUES (
                    :chamado_id,
                    :usuario_id,
                    :mensagem,
                    :data
                )
                """, {
                    "chamado_id": chamado_id,
                    "usuario_id": responsavel_id,
                    "mensagem": "Retorno ficticio da equipe com orientacoes ao cliente.",
                    "data": data_formatada(data_abertura + timedelta(hours=2, minutes=20)),
                })


def criar_banco_demo(recriar=True):
    organizacao_id = preparar_banco(recriar)
    ids = inserir_usuarios(organizacao_id)
    inserir_chamados(ids, organizacao_id)

    return DB_PATH


def main():
    criar_banco_demo()

    print("Banco ficticio criado com sucesso.")
    print("Organizacao demo: Empresa Demo")
    print("Usuarios: 1 admin, 2 suportes e 20 usuarios internos.")
    print("Senha de todos os usuarios demo: Demo@1234")
    print("Admin: admin@demo.com")
    print("Suporte 1: suporte1@demo.com")
    print("Suporte 2: suporte2@demo.com")


if __name__ == "__main__":
    main()
