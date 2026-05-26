import os
import sqlite3


# =========================
# CONEXÃO
# =========================
def conectar():

    conexao = sqlite3.connect(
        os.environ.get(
            "DATABASE_PATH",
            "chamados.db"
        ),
        timeout=10
    )

    conexao.row_factory = sqlite3.Row

    return conexao


def linha_para_dict(linha):

    if linha is None:
        return None

    return dict(linha)


def linhas_para_dict(linhas):

    return [
        dict(linha)
        for linha in linhas
    ]


# =========================
# TABELA USUÁRIOS
# =========================
def criar_tabela_usuarios():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        email TEXT NOT NULL UNIQUE,

        senha TEXT NOT NULL,

        tipo TEXT NOT NULL
    )
    """)

    conexao.commit()

    conexao.close()


# =========================
# TABELA RECUPERAÇÃO DE SENHA
# =========================
def criar_tabela_recuperacao_senha():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recuperacao_senha (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        usuario_id INTEGER NOT NULL,

        token TEXT NOT NULL UNIQUE,

        expira_em TEXT NOT NULL,

        usado INTEGER NOT NULL DEFAULT 0,

        data_criacao TEXT NOT NULL
    )
    """)

    conexao.commit()
    conexao.close()


# =========================
# CRIAR USUÁRIO
# =========================
def criar_usuario(nome, email, senha, tipo):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO usuarios (nome, email, senha, tipo)
    VALUES (?, ?, ?, ?)
    """, (nome, email, senha, tipo))

    conexao.commit()

    conexao.close()


def atualizar_senha_usuario(usuario_id, senha_hash):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE usuarios
    SET senha = ?
    WHERE id = ?
    """, (
        senha_hash,
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def criar_token_recuperacao(
    usuario_id,
    token,
    expira_em,
    data_criacao
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO recuperacao_senha (
        usuario_id,
        token,
        expira_em,
        data_criacao
    )
    VALUES (?, ?, ?, ?)
    """, (
        usuario_id,
        token,
        expira_em,
        data_criacao
    ))

    conexao.commit()
    conexao.close()


def buscar_token_recuperacao(token):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
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
    WHERE recuperacao_senha.token = ?
    """, (token,))

    recuperacao = cursor.fetchone()

    conexao.close()

    return linha_para_dict(recuperacao)


def marcar_token_recuperacao_usado(token):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE recuperacao_senha
    SET usado = 1
    WHERE token = ?
    """, (token,))

    conexao.commit()
    conexao.close()


# =========================
# BUSCAR USUÁRIO
# =========================
def buscar_usuario(email):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM usuarios
    WHERE email = ?
    """, (email,))

    usuario = cursor.fetchone()

    conexao.close()

    return linha_para_dict(usuario)


# =========================
# TABELA CHAMADOS
# =========================
def criar_tabela_chamados():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chamados (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        titulo TEXT NOT NULL,

        descricao TEXT NOT NULL,

        status TEXT NOT NULL,

        prioridade TEXT NOT NULL,

        usuario_id INTEGER NOT NULL,

        resposta TEXT,

        data_criacao TEXT NOT NULL
    )
    """)

    conexao.commit()

    conexao.close()

# =========================
# CRIAR CHAMADO
# =========================
def criar_chamado(
    titulo,
    descricao,
    prioridade,
    usuario_id,
    data_criacao,
    data_limite
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO chamados (
        titulo,
        descricao,
        status,
        prioridade,
        usuario_id,
        resposta,
        data_criacao,
        data_limite
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        titulo,
        descricao,
        "Aberto",
        prioridade,
        usuario_id,
        "",
        data_criacao,
        data_limite
    ))

    conexao.commit()

    id_chamado = cursor.lastrowid

    conexao.close()

    return id_chamado


# =========================
# LISTAR CHAMADOS
# =========================
def listar_chamados_usuario(usuario_id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM chamados
    WHERE usuario_id = ?
    ORDER BY id DESC
    """, (usuario_id,))

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)

# =========================
# BUSCAR CHAMADO
# =========================
def buscar_chamado(id_chamado):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM chamados
    WHERE id = ?
    """, (id_chamado,))

    chamado = cursor.fetchone()

    conexao.close()

    return linha_para_dict(chamado)

# =========================
# ATUALIZAR CHAMADO
# =========================
def atualizar_chamado(
    id_chamado,
    resposta,
    status
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE chamados

    SET
        resposta = ?,
        status = ?

    WHERE id = ?
    """, (
        resposta,
        status,
        id_chamado
    ))

    conexao.commit()

    conexao.close()

# =========================
# ESTATÍSTICAS
# =========================
def contar_chamados_usuario(usuario_id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE usuario_id = ?
    """, (usuario_id,))

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def contar_chamados_status(
    usuario_id,
    status
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE usuario_id = ?
    AND status = ?
    """, (
        usuario_id,
        status
    ))

    total = cursor.fetchone()[0]

    conexao.close()

    return total

# =========================
# BUSCAR CHAMADOS
# =========================
def buscar_chamados_usuario(
    usuario_id,
    pesquisa
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM chamados
    WHERE usuario_id = ?
    AND titulo LIKE ?
    ORDER BY id DESC
    """, (
        usuario_id,
        f"%{pesquisa}%"
    ))

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)

# =========================
# TABELA HISTÓRICO
# =========================
def criar_tabela_historico():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_chamados (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chamado_id INTEGER NOT NULL,

        mensagem TEXT NOT NULL,

        data TEXT NOT NULL

    )
    """)

    conexao.commit()

    conexao.close()


# =========================
# REGISTRAR HISTÓRICO
# =========================
def registrar_historico(
    chamado_id,
    usuario_id,
    mensagem,
    data
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO historico_chamados (
        chamado_id,
        usuario_id,
        mensagem,
        data
    )
    VALUES (?, ?, ?, ?)
    """, (
        chamado_id,
        usuario_id,
        mensagem,
        data
    ))

    conexao.commit()

    conexao.close()

# =========================
# LISTAR HISTÓRICO
# =========================
def listar_historico(
    chamado_id
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        historico_chamados.id AS id,
        historico_chamados.mensagem AS mensagem,
        historico_chamados.data AS data,
        usuarios.nome AS usuario_nome,
        usuarios.tipo AS usuario_tipo
    FROM historico_chamados
    LEFT JOIN usuarios
        ON historico_chamados.usuario_id = usuarios.id
    WHERE historico_chamados.chamado_id = ?
    ORDER BY historico_chamados.id DESC
    """, (chamado_id,))

    historico = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(historico)

# =========================
# TABELA COMENTÁRIOS
# =========================
def criar_tabela_comentarios():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios_chamados (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chamado_id INTEGER NOT NULL,

        usuario_id INTEGER NOT NULL,

        mensagem TEXT NOT NULL,

        data TEXT NOT NULL

    )
    """)

    conexao.commit()

    conexao.close()


# =========================
# ADICIONAR COMENTÁRIO
# =========================
def adicionar_comentario(
    chamado_id,
    usuario_id,
    mensagem,
    data
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO comentarios_chamados (
        chamado_id,
        usuario_id,
        mensagem,
        data
    )
    VALUES (?, ?, ?, ?)
    """, (
        chamado_id,
        usuario_id,
        mensagem,
        data
    ))

    conexao.commit()

    conexao.close()


# =========================
# LISTAR COMENTÁRIOS
# =========================
def listar_comentarios(chamado_id):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        comentarios_chamados.id AS id,
        usuarios.nome AS usuario_nome,
        usuarios.tipo AS usuario_tipo,
        comentarios_chamados.mensagem AS mensagem,
        comentarios_chamados.data AS data
    FROM comentarios_chamados
    INNER JOIN usuarios
        ON comentarios_chamados.usuario_id = usuarios.id
    WHERE comentarios_chamados.chamado_id = ?
    ORDER BY comentarios_chamados.id ASC
    """, (chamado_id,))

    comentarios = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(comentarios)

# =========================
# ESTATÍSTICAS ADMIN
# =========================
def contar_todos_chamados():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def contar_todos_chamados_status(status):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE status = ?
    """, (status,))

    total = cursor.fetchone()[0]

    conexao.close()

    return total


# =========================
# CHAMADOS RECENTES
# =========================
def listar_chamados_recentes_usuario(usuario_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        id,
        titulo,
        status,
        prioridade,
        data_criacao
    FROM chamados
    WHERE usuario_id = ?
    ORDER BY id DESC
    LIMIT 5
    """, (usuario_id,))

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)

# =========================
# LISTAR CHAMADOS ADMIN
# =========================
def listar_chamados_recentes_admin():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
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
    ORDER BY chamados.id DESC
    LIMIT 5
    """)

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)

# =========================
# LISTAR CHAMADOS ADMIN
# =========================
def listar_chamados_admin(
    status="",
    prioridade="",
    responsavel_id=""
):

    conexao = conectar()
    cursor = conexao.cursor()

    query = """
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
            AND datetime(chamados.data_limite) < datetime('now', 'localtime')
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
    WHERE 1 = 1
    """

    parametros = []

    if status:
        query += " AND chamados.status = ?"
        parametros.append(status)

    if prioridade:
        query += " AND chamados.prioridade = ?"
        parametros.append(prioridade)

    if responsavel_id == "sem_responsavel":

        query += " AND chamados.responsavel_id IS NULL"

    elif responsavel_id:

        query += " AND chamados.responsavel_id = ?"

        parametros.append(responsavel_id)

    query += " ORDER BY chamados.id DESC"

    cursor.execute(query, parametros)

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)


# =========================
# MIGRAÇÃO - DATA LIMITE
# =========================
def adicionar_coluna_data_limite():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    PRAGMA table_info(chamados)
    """)

    colunas = cursor.fetchall()

    nomes_colunas = [
        coluna[1]
        for coluna in colunas
    ]

    if "data_limite" not in nomes_colunas:

        cursor.execute("""
        ALTER TABLE chamados
        ADD COLUMN data_limite TEXT
        """)

        conexao.commit()

    conexao.close()

# =========================
# TABELA ANEXOS
# =========================
def criar_tabela_anexos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anexos_chamados (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chamado_id INTEGER NOT NULL,

        nome_arquivo TEXT NOT NULL,

        caminho_arquivo TEXT NOT NULL,

        data_envio TEXT NOT NULL

    )
    """)

    conexao.commit()
    conexao.close()


# =========================
# SALVAR ANEXO
# =========================
def salvar_anexo(
    chamado_id,
    nome_arquivo,
    caminho_arquivo,
    data_envio
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO anexos_chamados (
        chamado_id,
        nome_arquivo,
        caminho_arquivo,
        data_envio
    )
    VALUES (?, ?, ?, ?)
    """, (
        chamado_id,
        nome_arquivo,
        caminho_arquivo,
        data_envio
    ))

    conexao.commit()
    conexao.close()


# =========================
# LISTAR ANEXOS
# =========================
def listar_anexos(chamado_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT *
    FROM anexos_chamados
    WHERE chamado_id = ?
    ORDER BY id DESC
    """, (chamado_id,))

    anexos = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(anexos)
# =========================
# BUSCAR ANEXO
# =========================
def buscar_anexo(id_anexo):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT *
    FROM anexos_chamados
    WHERE id = ?
    """, (id_anexo,))

    anexo = cursor.fetchone()

    conexao.close()

    return linha_para_dict(anexo)

# =========================
# MIGRAÇÃO - USUÁRIO NO HISTÓRICO
# =========================
def adicionar_coluna_usuario_historico():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    PRAGMA table_info(historico_chamados)
    """)

    colunas = cursor.fetchall()

    nomes_colunas = [
        coluna[1]
        for coluna in colunas
    ]

    if "usuario_id" not in nomes_colunas:

        cursor.execute("""
        ALTER TABLE historico_chamados
        ADD COLUMN usuario_id INTEGER
        """)

        conexao.commit()

    conexao.close()

# =========================
# LISTAR USUÁRIOS
# =========================
def listar_usuarios():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        id,
        nome,
        email,
        tipo
    FROM usuarios
    ORDER BY id DESC
    """)

    usuarios = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(usuarios)


# =========================
# ATUALIZAR TIPO DE USUÁRIO
# =========================
def atualizar_tipo_usuario(
    usuario_id,
    novo_tipo
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE usuarios
    SET tipo = ?
    WHERE id = ?
    """, (
        novo_tipo,
        usuario_id
    ))

    conexao.commit()

    conexao.close()

    # =========================
# MIGRAÇÃO - RESPONSÁVEL DO CHAMADO
# =========================
def adicionar_coluna_responsavel_chamado():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    PRAGMA table_info(chamados)
    """)

    colunas = cursor.fetchall()

    nomes_colunas = [
        coluna[1]
        for coluna in colunas
    ]

    if "responsavel_id" not in nomes_colunas:

        cursor.execute("""
        ALTER TABLE chamados
        ADD COLUMN responsavel_id INTEGER
        """)

        conexao.commit()

    conexao.close()


# =========================
# LISTAR ADMINS
# =========================
def listar_administradores():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        id,
        nome,
        email,
        tipo
    FROM usuarios
    WHERE tipo IN ('admin', 'suporte')
    ORDER BY nome ASC
    """)

    administradores = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(administradores)


# =========================
# ATRIBUIR RESPONSÁVEL
# =========================
def atribuir_responsavel_chamado(
    chamado_id,
    responsavel_id
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE chamados
    SET responsavel_id = ?
    WHERE id = ?
    """, (
        responsavel_id,
        chamado_id
    ))

    conexao.commit()

    conexao.close()

# =========================
# LISTAR CHAMADOS DO RESPONSÁVEL
# =========================
def listar_chamados_responsavel(
    responsavel_id,
    status="",
    prioridade=""
):

    conexao = conectar()
    cursor = conexao.cursor()

    query = """
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
            AND datetime(chamados.data_limite) < datetime('now', 'localtime')
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
    WHERE chamados.responsavel_id = ?
    """

    parametros = [
        responsavel_id
    ]

    if status:
        query += " AND chamados.status = ?"
        parametros.append(status)

    if prioridade:
        query += " AND chamados.prioridade = ?"
        parametros.append(prioridade)

    query += " ORDER BY chamados.id DESC"

    cursor.execute(query, parametros)

    chamados = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(chamados)

# =========================
# BUSCAR RESPONSÁVEL DO CHAMADO
# =========================
def buscar_responsavel_chamado(chamado_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        usuarios.nome
    FROM chamados
    LEFT JOIN usuarios
        ON chamados.responsavel_id = usuarios.id
    WHERE chamados.id = ?
    """, (chamado_id,))

    responsavel = cursor.fetchone()

    conexao.close()

    if responsavel:
        return responsavel["nome"]

    return None

# =========================
# CHAMADOS SEM RESPONSÁVEL
# =========================
def contar_chamados_sem_responsavel():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE responsavel_id IS NULL
    AND status NOT IN ('Resolvido', 'Encerrado')
    """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total


# =========================
# CHAMADOS DO RESPONSÁVEL
# =========================
def contar_chamados_responsavel(responsavel_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE responsavel_id = ?
    AND status NOT IN ('Resolvido', 'Encerrado')
    """, (responsavel_id,))

    total = cursor.fetchone()[0]

    conexao.close()

    return total


# =========================
# CHAMADOS ATRASADOS
# =========================
def contar_chamados_atrasados():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chamados
    WHERE data_limite IS NOT NULL
    AND datetime(data_limite) < datetime('now', 'localtime')
    AND status NOT IN ('Resolvido', 'Encerrado')
    """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total

def listar_atendentes():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        id,
        nome,
        email,
        tipo
    FROM usuarios
    WHERE tipo IN ('admin', 'suporte')
    ORDER BY nome ASC
    """)

    atendentes = cursor.fetchall()

    conexao.close()

    return linhas_para_dict(atendentes)
