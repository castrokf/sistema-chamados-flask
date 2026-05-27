import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
DEFAULT_ORG_NAME = "Nortia Operações"
DEFAULT_ORG_SLUG = "nortia-operacoes"

_engine = None
_engine_url = None


def obter_database_url():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )

        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

        return database_url

    database_path = Path(
        os.environ.get(
            "DATABASE_PATH",
            "chamados.db"
        )
    )

    return f"sqlite:///{database_path}"


def obter_engine():
    global _engine
    global _engine_url

    database_url = obter_database_url()

    if _engine is None or _engine_url != database_url:
        connect_args = {}

        if database_url.startswith("sqlite"):
            connect_args = {
                "check_same_thread": False
            }

        _engine = create_engine(
            database_url,
            connect_args=connect_args,
            future=True,
            pool_pre_ping=True
        )
        _engine_url = database_url

    return _engine


def banco_postgres():
    return obter_engine().dialect.name == "postgresql"


def id_sql():
    if banco_postgres():
        return "SERIAL PRIMARY KEY"

    return "INTEGER PRIMARY KEY AUTOINCREMENT"


def executar(sql, parametros=None):
    with obter_engine().begin() as conexao:
        return conexao.execute(
            text(sql),
            parametros or {}
        )


def consultar_um(sql, parametros=None):
    with obter_engine().connect() as conexao:
        resultado = conexao.execute(
            text(sql),
            parametros or {}
        ).mappings().first()

    if resultado is None:
        return None

    return dict(resultado)


def consultar_lista(sql, parametros=None):
    with obter_engine().connect() as conexao:
        resultado = conexao.execute(
            text(sql),
            parametros or {}
        ).mappings().all()

    return [
        dict(linha)
        for linha in resultado
    ]


def consultar_scalar(sql, parametros=None):
    with obter_engine().connect() as conexao:
        return conexao.execute(
            text(sql),
            parametros or {}
        ).scalar()


def inserir_e_retornar_id(sql, parametros=None):
    with obter_engine().begin() as conexao:
        if banco_postgres():
            resultado = conexao.execute(
                text(f"{sql} RETURNING id"),
                parametros or {}
            )

            return resultado.scalar_one()

        resultado = conexao.execute(
            text(sql),
            parametros or {}
        )

        return resultado.lastrowid


def tabela_tem_coluna(tabela, coluna):
    inspetor = inspect(obter_engine())

    if not inspetor.has_table(tabela):
        return False

    return coluna in [
        item["name"]
        for item in inspetor.get_columns(tabela)
    ]


def adicionar_coluna(tabela, coluna, definicao):
    if tabela_tem_coluna(tabela, coluna):
        return

    executar(
        f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
    )


def criar_tabela_organizacoes():
    executar(f"""
    CREATE TABLE IF NOT EXISTS organizacoes (
        id {id_sql()},
        nome TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        ativo INTEGER NOT NULL DEFAULT 1,
        data_criacao TEXT NOT NULL
    )
    """)


def buscar_organizacao_por_slug(slug):
    return consultar_um("""
    SELECT *
    FROM organizacoes
    WHERE slug = :slug
    """, {
        "slug": slug
    })


def criar_organizacao(nome, slug):
    existente = buscar_organizacao_por_slug(slug)

    if existente:
        return existente["id"]

    return inserir_e_retornar_id("""
    INSERT INTO organizacoes (
        nome,
        slug,
        ativo,
        data_criacao
    )
    VALUES (
        :nome,
        :slug,
        1,
        :data_criacao
    )
    """, {
        "nome": nome,
        "slug": slug,
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def obter_organizacao_padrao_id():
    criar_tabela_organizacoes()

    organizacao_legada = buscar_organizacao_por_slug("empresa-demo")

    if organizacao_legada:
        return organizacao_legada["id"]

    return criar_organizacao(
        DEFAULT_ORG_NAME,
        DEFAULT_ORG_SLUG
    )


def aplicar_identidade_corporativa_padrao():
    organizacao_antiga = buscar_organizacao_por_slug("empresa-demo")
    organizacao_atual = buscar_organizacao_por_slug(DEFAULT_ORG_SLUG)
    senha_inicial = None

    if organizacao_antiga and not organizacao_atual:
        executar("""
        UPDATE organizacoes
        SET nome = :nome,
            slug = :slug
        WHERE id = :organizacao_id
        """, {
            "nome": DEFAULT_ORG_NAME,
            "slug": DEFAULT_ORG_SLUG,
            "organizacao_id": organizacao_antiga["id"]
        })
    elif organizacao_antiga and organizacao_atual:
        executar("""
        UPDATE usuarios
        SET organizacao_id = :organizacao_atual_id
        WHERE organizacao_id = :organizacao_antiga_id
        """, {
            "organizacao_atual_id": organizacao_atual["id"],
            "organizacao_antiga_id": organizacao_antiga["id"]
        })

        executar("""
        UPDATE chamados
        SET organizacao_id = :organizacao_atual_id
        WHERE organizacao_id = :organizacao_antiga_id
        """, {
            "organizacao_atual_id": organizacao_atual["id"],
            "organizacao_antiga_id": organizacao_antiga["id"]
        })

        executar("""
        UPDATE organizacoes
        SET nome = :nome
        WHERE id = :organizacao_id
        """, {
            "nome": DEFAULT_ORG_NAME,
            "organizacao_id": organizacao_atual["id"]
        })

        executar("""
        UPDATE organizacoes
        SET nome = :nome,
            slug = :slug,
            ativo = 0
        WHERE id = :organizacao_id
        """, {
            "nome": "Nortia Arquivo",
            "slug": f"empresa-demo-arquivo-{organizacao_antiga['id']}",
            "organizacao_id": organizacao_antiga["id"]
        })
    elif organizacao_antiga:
        executar("""
        UPDATE organizacoes
        SET nome = :nome
        WHERE id = :organizacao_id
        """, {
            "nome": DEFAULT_ORG_NAME,
            "organizacao_id": organizacao_antiga["id"]
        })

    for email_antigo, email_novo, nome_novo in [
        ("admin@demo.com", "admin@nortia.internal", "Administrador Nortia"),
        ("suporte1@demo.com", "marina.atendimento@nortia.internal", "Marina Atendimento"),
        ("suporte2@demo.com", "rafael.operacoes@nortia.internal", "Rafael Operações"),
        ("ana.martins@demo.com", "ana.martins@nortia.internal", "Ana Martins"),
        ("bruno.almeida@demo.com", "bruno.almeida@nortia.internal", "Bruno Almeida"),
        ("carla.souza@demo.com", "carla.souza@nortia.internal", "Carla Souza"),
        ("diego.pereira@demo.com", "diego.pereira@nortia.internal", "Diego Pereira"),
        ("elisa.fernandes@demo.com", "elisa.fernandes@nortia.internal", "Elisa Fernandes"),
        ("fabio.rocha@demo.com", "fabio.rocha@nortia.internal", "Fabio Rocha"),
        ("gabriela.lima@demo.com", "gabriela.lima@nortia.internal", "Gabriela Lima"),
        ("henrique.costa@demo.com", "henrique.costa@nortia.internal", "Henrique Costa"),
        ("isabela.ramos@demo.com", "isabela.ramos@nortia.internal", "Isabela Ramos"),
        ("joao.carvalho@demo.com", "joao.carvalho@nortia.internal", "Joao Carvalho"),
        ("larissa.gomes@demo.com", "larissa.gomes@nortia.internal", "Larissa Gomes"),
        ("marcelo.nunes@demo.com", "marcelo.nunes@nortia.internal", "Marcelo Nunes"),
        ("natalia.ribeiro@demo.com", "natalia.ribeiro@nortia.internal", "Natalia Ribeiro"),
        ("otavio.mendes@demo.com", "otavio.mendes@nortia.internal", "Otavio Mendes"),
        ("patricia.castro@demo.com", "patricia.castro@nortia.internal", "Patricia Castro"),
        ("renato.barbosa@demo.com", "renato.barbosa@nortia.internal", "Renato Barbosa"),
        ("sofia.teixeira@demo.com", "sofia.teixeira@nortia.internal", "Sofia Teixeira"),
        ("tiago.moreira@demo.com", "tiago.moreira@nortia.internal", "Tiago Moreira"),
        ("vanessa.cardoso@demo.com", "vanessa.cardoso@nortia.internal", "Vanessa Cardoso"),
        ("william.araujo@demo.com", "william.araujo@nortia.internal", "William Araujo"),
    ]:
        usuario_novo = consultar_um("""
        SELECT id
        FROM usuarios
        WHERE email = :email
        """, {
            "email": email_novo
        })

        if usuario_novo:
            executar("""
            UPDATE usuarios
            SET nome = :nome
            WHERE email = :email
            """, {
                "nome": nome_novo,
                "email": email_novo
            })
            continue

        if senha_inicial is None:
            from argon2 import PasswordHasher

            senha_inicial = PasswordHasher().hash("Nortia@2026")

        executar("""
        UPDATE usuarios
        SET nome = :nome,
            email = :email_novo,
            senha = :senha
        WHERE email = :email_antigo
        """, {
            "nome": nome_novo,
            "email_novo": email_novo,
            "email_antigo": email_antigo,
            "senha": senha_inicial
        })


def criar_tabela_usuarios():
    executar(f"""
    CREATE TABLE IF NOT EXISTS usuarios (
        id {id_sql()},
        organizacao_id INTEGER,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        data_criacao TEXT
    )
    """)


def adicionar_coluna_organizacao_usuarios():
    adicionar_coluna(
        "usuarios",
        "organizacao_id",
        "INTEGER"
    )
    adicionar_coluna(
        "usuarios",
        "ativo",
        "INTEGER NOT NULL DEFAULT 1"
    )
    adicionar_coluna(
        "usuarios",
        "data_criacao",
        "TEXT"
    )

    organizacao_id = obter_organizacao_padrao_id()

    executar("""
    UPDATE usuarios
    SET organizacao_id = :organizacao_id
    WHERE organizacao_id IS NULL
    """, {
        "organizacao_id": organizacao_id
    })


def criar_tabela_recuperacao_senha():
    executar(f"""
    CREATE TABLE IF NOT EXISTS recuperacao_senha (
        id {id_sql()},
        usuario_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expira_em TEXT NOT NULL,
        usado INTEGER NOT NULL DEFAULT 0,
        data_criacao TEXT NOT NULL
    )
    """)


def criar_usuario(
    nome,
    email,
    senha,
    tipo,
    organizacao_id=None
):
    organizacao_id = organizacao_id or obter_organizacao_padrao_id()

    executar("""
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
        "senha": senha,
        "tipo": tipo,
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def atualizar_senha_usuario(usuario_id, senha_hash):
    executar("""
    UPDATE usuarios
    SET senha = :senha
    WHERE id = :usuario_id
    """, {
        "senha": senha_hash,
        "usuario_id": usuario_id
    })


def criar_token_recuperacao(
    usuario_id,
    token,
    expira_em,
    data_criacao
):
    executar("""
    INSERT INTO recuperacao_senha (
        usuario_id,
        token,
        expira_em,
        data_criacao
    )
    VALUES (
        :usuario_id,
        :token,
        :expira_em,
        :data_criacao
    )
    """, {
        "usuario_id": usuario_id,
        "token": token,
        "expira_em": expira_em,
        "data_criacao": data_criacao
    })


def buscar_token_recuperacao(token):
    return consultar_um("""
    SELECT
        recuperacao_senha.id AS id,
        recuperacao_senha.usuario_id AS usuario_id,
        recuperacao_senha.token AS token,
        recuperacao_senha.expira_em AS expira_em,
        recuperacao_senha.usado AS usado,
        usuarios.email AS usuario_email
    FROM recuperacao_senha
    INNER JOIN usuarios
        ON recuperacao_senha.usuario_id = usuarios.id
    WHERE recuperacao_senha.token = :token
    """, {
        "token": token
    })


def marcar_token_recuperacao_usado(token):
    executar("""
    UPDATE recuperacao_senha
    SET usado = 1
    WHERE token = :token
    """, {
        "token": token
    })


def buscar_usuario(email):
    return consultar_um("""
    SELECT
        usuarios.id AS id,
        usuarios.organizacao_id AS organizacao_id,
        organizacoes.nome AS organizacao_nome,
        usuarios.nome AS nome,
        usuarios.email AS email,
        usuarios.senha AS senha,
        usuarios.tipo AS tipo,
        usuarios.ativo AS ativo
    FROM usuarios
    INNER JOIN organizacoes
        ON usuarios.organizacao_id = organizacoes.id
    WHERE usuarios.email = :email
    AND usuarios.ativo = 1
    """, {
        "email": email
    })


def contar_usuarios_total():
    return consultar_scalar("""
    SELECT COUNT(*)
    FROM usuarios
    """) or 0


def criar_tabela_chamados():
    executar(f"""
    CREATE TABLE IF NOT EXISTS chamados (
        id {id_sql()},
        organizacao_id INTEGER,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        status TEXT NOT NULL,
        prioridade TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        resposta TEXT,
        data_criacao TEXT NOT NULL,
        data_limite TEXT,
        responsavel_id INTEGER
    )
    """)


def adicionar_coluna_organizacao_chamados():
    adicionar_coluna(
        "chamados",
        "organizacao_id",
        "INTEGER"
    )

    executar("""
    UPDATE chamados
    SET organizacao_id = (
        SELECT usuarios.organizacao_id
        FROM usuarios
        WHERE usuarios.id = chamados.usuario_id
    )
    WHERE organizacao_id IS NULL
    """)


def criar_chamado(
    titulo,
    descricao,
    prioridade,
    usuario_id,
    data_criacao,
    data_limite,
    organizacao_id=None
):
    if organizacao_id is None:
        usuario = buscar_usuario_por_id(usuario_id)
        organizacao_id = usuario["organizacao_id"]

    return inserir_e_retornar_id("""
    INSERT INTO chamados (
        organizacao_id,
        titulo,
        descricao,
        status,
        prioridade,
        usuario_id,
        resposta,
        data_criacao,
        data_limite
    )
    VALUES (
        :organizacao_id,
        :titulo,
        :descricao,
        'Aberto',
        :prioridade,
        :usuario_id,
        '',
        :data_criacao,
        :data_limite
    )
    """, {
        "organizacao_id": organizacao_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade,
        "usuario_id": usuario_id,
        "data_criacao": data_criacao,
        "data_limite": data_limite
    })


def buscar_usuario_por_id(usuario_id):
    return consultar_um("""
    SELECT *
    FROM usuarios
    WHERE id = :usuario_id
    """, {
        "usuario_id": usuario_id
    })


def listar_chamados_usuario(usuario_id):
    return consultar_lista("""
    SELECT *
    FROM chamados
    WHERE usuario_id = :usuario_id
    ORDER BY id DESC
    """, {
        "usuario_id": usuario_id
    })


def buscar_chamado(id_chamado, organizacao_id=None):
    parametros = {
        "id_chamado": id_chamado
    }

    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_um(f"""
    SELECT *
    FROM chamados
    WHERE id = :id_chamado
    {filtro_org}
    """, parametros)


def atualizar_chamado(
    id_chamado,
    resposta,
    status,
    organizacao_id=None
):
    parametros = {
        "id_chamado": id_chamado,
        "resposta": resposta,
        "status": status
    }

    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    executar(f"""
    UPDATE chamados
    SET resposta = :resposta,
        status = :status
    WHERE id = :id_chamado
    {filtro_org}
    """, parametros)


def contar_chamados_usuario(usuario_id):
    return consultar_scalar("""
    SELECT COUNT(*)
    FROM chamados
    WHERE usuario_id = :usuario_id
    """, {
        "usuario_id": usuario_id
    }) or 0


def contar_chamados_status(
    usuario_id,
    status
):
    return consultar_scalar("""
    SELECT COUNT(*)
    FROM chamados
    WHERE usuario_id = :usuario_id
    AND status = :status
    """, {
        "usuario_id": usuario_id,
        "status": status
    }) or 0


def buscar_chamados_usuario(
    usuario_id,
    pesquisa
):
    return consultar_lista("""
    SELECT *
    FROM chamados
    WHERE usuario_id = :usuario_id
    AND titulo LIKE :pesquisa
    ORDER BY id DESC
    """, {
        "usuario_id": usuario_id,
        "pesquisa": f"%{pesquisa}%"
    })


def criar_tabela_historico():
    executar(f"""
    CREATE TABLE IF NOT EXISTS historico_chamados (
        id {id_sql()},
        chamado_id INTEGER NOT NULL,
        usuario_id INTEGER,
        mensagem TEXT NOT NULL,
        data TEXT NOT NULL
    )
    """)


def registrar_historico(
    chamado_id,
    usuario_id,
    mensagem,
    data
):
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
        "usuario_id": usuario_id,
        "mensagem": mensagem,
        "data": data
    })


def listar_historico(chamado_id):
    return consultar_lista("""
    SELECT
        historico_chamados.id AS id,
        historico_chamados.mensagem AS mensagem,
        historico_chamados.data AS data,
        usuarios.nome AS usuario_nome,
        usuarios.tipo AS usuario_tipo
    FROM historico_chamados
    LEFT JOIN usuarios
        ON historico_chamados.usuario_id = usuarios.id
    WHERE historico_chamados.chamado_id = :chamado_id
    ORDER BY historico_chamados.id DESC
    """, {
        "chamado_id": chamado_id
    })


def criar_tabela_comentarios():
    executar(f"""
    CREATE TABLE IF NOT EXISTS comentarios_chamados (
        id {id_sql()},
        chamado_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        mensagem TEXT NOT NULL,
        data TEXT NOT NULL
    )
    """)


def adicionar_comentario(
    chamado_id,
    usuario_id,
    mensagem,
    data
):
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
        "usuario_id": usuario_id,
        "mensagem": mensagem,
        "data": data
    })


def listar_comentarios(chamado_id):
    return consultar_lista("""
    SELECT
        comentarios_chamados.id AS id,
        usuarios.nome AS usuario_nome,
        usuarios.tipo AS usuario_tipo,
        comentarios_chamados.mensagem AS mensagem,
        comentarios_chamados.data AS data
    FROM comentarios_chamados
    INNER JOIN usuarios
        ON comentarios_chamados.usuario_id = usuarios.id
    WHERE comentarios_chamados.chamado_id = :chamado_id
    ORDER BY comentarios_chamados.id ASC
    """, {
        "chamado_id": chamado_id
    })


def contar_todos_chamados(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = "WHERE organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    {filtro_org}
    """, parametros) or 0


def contar_todos_chamados_status(status, organizacao_id=None):
    parametros = {
        "status": status
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    WHERE status = :status
    {filtro_org}
    """, parametros) or 0


def contar_todos_chamados_prioridade(prioridade, organizacao_id=None):
    parametros = {
        "prioridade": prioridade
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    WHERE prioridade = :prioridade
    {filtro_org}
    """, parametros) or 0


def listar_chamados_recentes_usuario(usuario_id):
    return consultar_lista("""
    SELECT
        id,
        titulo,
        status,
        prioridade,
        data_criacao
    FROM chamados
    WHERE usuario_id = :usuario_id
    ORDER BY id DESC
    LIMIT 5
    """, {
        "usuario_id": usuario_id
    })


def listar_chamados_recentes_admin(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = "WHERE chamados.organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_lista(f"""
    SELECT
        chamados.id AS id,
        chamados.titulo AS titulo,
        chamados.status AS status,
        chamados.prioridade AS prioridade,
        usuarios.nome AS usuario_nome,
        chamados.data_criacao AS data_criacao
    FROM chamados
    INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    {filtro_org}
    ORDER BY chamados.id DESC
    LIMIT 5
    """, parametros)


def listar_chamados_admin(
    status="",
    prioridade="",
    responsavel_id="",
    organizacao_id=None
):
    parametros = {
        "agora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    filtros = [
        "1 = 1"
    ]

    if organizacao_id is not None:
        filtros.append("chamados.organizacao_id = :organizacao_id")
        parametros["organizacao_id"] = organizacao_id

    if status:
        filtros.append("chamados.status = :status")
        parametros["status"] = status

    if prioridade:
        filtros.append("chamados.prioridade = :prioridade")
        parametros["prioridade"] = prioridade

    if responsavel_id == "sem_responsavel":
        filtros.append("chamados.responsavel_id IS NULL")
    elif responsavel_id:
        filtros.append("chamados.responsavel_id = :responsavel_id")
        parametros["responsavel_id"] = responsavel_id

    return consultar_lista(f"""
    SELECT
        chamados.id AS id,
        chamados.titulo AS titulo,
        chamados.status AS status,
        chamados.prioridade AS prioridade,
        usuarios.nome AS usuario_nome,
        chamados.data_criacao AS data_criacao,
        chamados.data_limite AS data_limite,
        CASE
            WHEN chamados.data_limite IS NOT NULL
            AND chamados.data_limite < :agora
            AND chamados.status NOT IN ('Resolvido', 'Encerrado')
            THEN 1
            ELSE 0
        END AS atrasado,
        responsavel.nome AS responsavel_nome
    FROM chamados
    INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    LEFT JOIN usuarios AS responsavel
        ON chamados.responsavel_id = responsavel.id
    WHERE {" AND ".join(filtros)}
    ORDER BY chamados.id DESC
    """, parametros)


def adicionar_coluna_data_limite():
    adicionar_coluna(
        "chamados",
        "data_limite",
        "TEXT"
    )


def criar_tabela_anexos():
    executar(f"""
    CREATE TABLE IF NOT EXISTS anexos_chamados (
        id {id_sql()},
        chamado_id INTEGER NOT NULL,
        nome_arquivo TEXT NOT NULL,
        caminho_arquivo TEXT NOT NULL,
        data_envio TEXT NOT NULL
    )
    """)


def salvar_anexo(
    chamado_id,
    nome_arquivo,
    caminho_arquivo,
    data_envio
):
    executar("""
    INSERT INTO anexos_chamados (
        chamado_id,
        nome_arquivo,
        caminho_arquivo,
        data_envio
    )
    VALUES (
        :chamado_id,
        :nome_arquivo,
        :caminho_arquivo,
        :data_envio
    )
    """, {
        "chamado_id": chamado_id,
        "nome_arquivo": nome_arquivo,
        "caminho_arquivo": caminho_arquivo,
        "data_envio": data_envio
    })


def listar_anexos(chamado_id):
    return consultar_lista("""
    SELECT *
    FROM anexos_chamados
    WHERE chamado_id = :chamado_id
    ORDER BY id DESC
    """, {
        "chamado_id": chamado_id
    })


def buscar_anexo(id_anexo):
    return consultar_um("""
    SELECT *
    FROM anexos_chamados
    WHERE id = :id_anexo
    """, {
        "id_anexo": id_anexo
    })


def adicionar_coluna_usuario_historico():
    adicionar_coluna(
        "historico_chamados",
        "usuario_id",
        "INTEGER"
    )


def listar_usuarios(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = "WHERE usuarios.organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_lista(f"""
    SELECT
        usuarios.id AS id,
        usuarios.nome AS nome,
        usuarios.email AS email,
        usuarios.tipo AS tipo,
        usuarios.ativo AS ativo,
        organizacoes.nome AS organizacao_nome
    FROM usuarios
    INNER JOIN organizacoes
        ON usuarios.organizacao_id = organizacoes.id
    {filtro_org}
    ORDER BY usuarios.id DESC
    """, parametros)


def atualizar_tipo_usuario(
    usuario_id,
    novo_tipo,
    organizacao_id=None
):
    parametros = {
        "usuario_id": usuario_id,
        "novo_tipo": novo_tipo
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    executar(f"""
    UPDATE usuarios
    SET tipo = :novo_tipo
    WHERE id = :usuario_id
    {filtro_org}
    """, parametros)


def adicionar_coluna_responsavel_chamado():
    adicionar_coluna(
        "chamados",
        "responsavel_id",
        "INTEGER"
    )


def listar_administradores(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = "AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_lista(f"""
    SELECT
        id,
        nome,
        email,
        tipo
    FROM usuarios
    WHERE tipo IN ('admin', 'suporte')
    AND ativo = 1
    {filtro_org}
    ORDER BY nome ASC
    """, parametros)


def listar_suportes(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = "AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_lista(f"""
    SELECT
        id,
        nome,
        email,
        tipo
    FROM usuarios
    WHERE tipo = 'suporte'
    AND ativo = 1
    {filtro_org}
    ORDER BY nome ASC
    """, parametros)


def atribuir_responsavel_chamado(
    chamado_id,
    responsavel_id,
    organizacao_id=None
):
    parametros = {
        "chamado_id": chamado_id,
        "responsavel_id": responsavel_id
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    executar(f"""
    UPDATE chamados
    SET responsavel_id = :responsavel_id
    WHERE id = :chamado_id
    {filtro_org}
    """, parametros)


def listar_chamados_responsavel(
    responsavel_id,
    status="",
    prioridade="",
    organizacao_id=None
):
    parametros = {
        "responsavel_id": responsavel_id,
        "agora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    filtros = [
        "chamados.responsavel_id = :responsavel_id"
    ]

    if organizacao_id is not None:
        filtros.append("chamados.organizacao_id = :organizacao_id")
        parametros["organizacao_id"] = organizacao_id

    if status:
        filtros.append("chamados.status = :status")
        parametros["status"] = status

    if prioridade:
        filtros.append("chamados.prioridade = :prioridade")
        parametros["prioridade"] = prioridade

    return consultar_lista(f"""
    SELECT
        chamados.id AS id,
        chamados.titulo AS titulo,
        chamados.status AS status,
        chamados.prioridade AS prioridade,
        usuarios.nome AS usuario_nome,
        chamados.data_criacao AS data_criacao,
        chamados.data_limite AS data_limite,
        CASE
            WHEN chamados.data_limite IS NOT NULL
            AND chamados.data_limite < :agora
            AND chamados.status NOT IN ('Resolvido', 'Encerrado')
            THEN 1
            ELSE 0
        END AS atrasado,
        responsavel.nome AS responsavel_nome
    FROM chamados
    INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    LEFT JOIN usuarios AS responsavel
        ON chamados.responsavel_id = responsavel.id
    WHERE {" AND ".join(filtros)}
    ORDER BY chamados.id DESC
    """, parametros)


def buscar_responsavel_chamado(chamado_id):
    responsavel = consultar_um("""
    SELECT
        usuarios.nome AS nome
    FROM chamados
    LEFT JOIN usuarios
        ON chamados.responsavel_id = usuarios.id
    WHERE chamados.id = :chamado_id
    """, {
        "chamado_id": chamado_id
    })

    if responsavel:
        return responsavel["nome"]

    return None


def contar_chamados_sem_responsavel(organizacao_id=None):
    parametros = {}
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    WHERE responsavel_id IS NULL
    AND status NOT IN ('Resolvido', 'Encerrado')
    {filtro_org}
    """, parametros) or 0


def contar_chamados_responsavel(responsavel_id, organizacao_id=None):
    parametros = {
        "responsavel_id": responsavel_id
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    WHERE responsavel_id = :responsavel_id
    AND status NOT IN ('Resolvido', 'Encerrado')
    {filtro_org}
    """, parametros) or 0


def contar_chamados_atrasados(organizacao_id=None):
    parametros = {
        "agora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    filtro_org = ""

    if organizacao_id is not None:
        filtro_org = " AND organizacao_id = :organizacao_id"
        parametros["organizacao_id"] = organizacao_id

    return consultar_scalar(f"""
    SELECT COUNT(*)
    FROM chamados
    WHERE data_limite IS NOT NULL
    AND data_limite < :agora
    AND status NOT IN ('Resolvido', 'Encerrado')
    {filtro_org}
    """, parametros) or 0


def listar_atendentes(organizacao_id=None):
    return listar_administradores(organizacao_id)


def inicializar_banco():
    criar_tabela_organizacoes()
    criar_tabela_usuarios()
    adicionar_coluna_organizacao_usuarios()
    aplicar_identidade_corporativa_padrao()
    criar_tabela_recuperacao_senha()
    criar_tabela_chamados()
    adicionar_coluna_data_limite()
    adicionar_coluna_responsavel_chamado()
    adicionar_coluna_organizacao_chamados()
    criar_tabela_historico()
    adicionar_coluna_usuario_historico()
    criar_tabela_comentarios()
    criar_tabela_anexos()
