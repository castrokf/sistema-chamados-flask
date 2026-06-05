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
ACCESS_PASSWORD = "Nortia@2026"


USUARIOS_EQUIPE = [
    ("Luan Castro", "admin@nortia.internal", "admin"),
    ("Marina Atendimento", "marina.atendimento@nortia.internal", "suporte"),
    ("Rafael Operações", "rafael.operacoes@nortia.internal", "suporte"),
]

CLIENTES = [
    ("Ana Martins", "ana.martins@nortia.internal"),
    ("Bruno Almeida", "bruno.almeida@nortia.internal"),
    ("Carla Souza", "carla.souza@nortia.internal"),
    ("Diego Pereira", "diego.pereira@nortia.internal"),
    ("Elisa Fernandes", "elisa.fernandes@nortia.internal"),
    ("Fabio Rocha", "fabio.rocha@nortia.internal"),
    ("Gabriela Lima", "gabriela.lima@nortia.internal"),
    ("Henrique Costa", "henrique.costa@nortia.internal"),
    ("Isabela Ramos", "isabela.ramos@nortia.internal"),
    ("Joao Carvalho", "joao.carvalho@nortia.internal"),
    ("Larissa Gomes", "larissa.gomes@nortia.internal"),
    ("Marcelo Nunes", "marcelo.nunes@nortia.internal"),
    ("Natalia Ribeiro", "natalia.ribeiro@nortia.internal"),
    ("Otavio Mendes", "otavio.mendes@nortia.internal"),
    ("Patricia Castro", "patricia.castro@nortia.internal"),
    ("Renato Barbosa", "renato.barbosa@nortia.internal"),
    ("Sofia Teixeira", "sofia.teixeira@nortia.internal"),
    ("Tiago Moreira", "tiago.moreira@nortia.internal"),
    ("Vanessa Cardoso", "vanessa.cardoso@nortia.internal"),
    ("William Araujo", "william.araujo@nortia.internal"),
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
    "Chamado registrado para validar o fluxo operacional de atendimento.",
]

RESPOSTAS = {
    "Em andamento": "Atendimento iniciado. A equipe esta analisando as informacoes enviadas.",
    "Resolvido": "Solicitacao resolvida pela equipe de suporte. Usuario pode validar o atendimento.",
    "Encerrado": "Chamado encerrado apos conclusao e registro das informacoes do atendimento.",
}


def usando_sqlite_local():
    return obter_database_url().startswith("sqlite")


def limpar_tabelas_iniciais():
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
        limpar_tabelas_iniciais()

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
            "senha": ph.hash(ACCESS_PASSWORD),
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
            "senha": ph.hash(ACCESS_PASSWORD),
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
        ids["marina.atendimento@nortia.internal"],
        ids["rafael.operacoes@nortia.internal"],
        ids["admin@nortia.internal"],
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
        "Urgente",
    ]

    agora = datetime.now().replace(second=0, microsecond=0)

    for indice, (_, email_cliente) in enumerate(CLIENTES, start=1):
        quantidade = 2 if indice <= 10 else 1

        for extra in range(quantidade):
            ticket_numero = indice + extra
            status = status_opcoes[(indice + extra) % len(status_opcoes)]
            prioridade = prioridade_opcoes[(indice + extra) % len(prioridade_opcoes)]
            data_abertura = agora - timedelta(days=indice + extra, hours=extra * 3)

            if prioridade == "Urgente":
                data_limite = data_abertura + timedelta(hours=1)
            elif prioridade == "Alta":
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
                    "mensagem": "Comentario do usuario para complementar o atendimento.",
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
                    "mensagem": "Retorno da equipe com orientacoes ao cliente.",
                    "data": data_formatada(data_abertura + timedelta(hours=2, minutes=20)),
                })


def criar_banco_inicial(recriar=True):
    organizacao_id = preparar_banco(recriar)
    ids = inserir_usuarios(organizacao_id)
    inserir_chamados(ids, organizacao_id)

    return DB_PATH


def main():
    criar_banco_inicial()

    print("Banco inicial criado com sucesso.")
    print("Organizacao: Nortia Operações")
    print("Usuarios: 1 admin, 2 suportes e 20 usuarios internos.")
    print("Senha inicial de todos os usuarios: Nortia@2026")
    print("Admin: admin@nortia.internal")
    print("Suporte 1: marina.atendimento@nortia.internal")
    print("Suporte 2: rafael.operacoes@nortia.internal")


if __name__ == "__main__":
    main()
