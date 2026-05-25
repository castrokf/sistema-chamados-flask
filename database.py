import sqlite3


# =========================
# CONEXÃO
# =========================
def conectar():

    conexao = sqlite3.connect(
        "chamados.db",
        timeout=10
    )

    return conexao


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

    return usuario


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

    return chamados

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

    return chamado

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

    return chamados

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
    mensagem,
    data
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO historico_chamados (
        chamado_id,
        mensagem,
        data
    )
    VALUES (?, ?, ?)
    """, (
        chamado_id,
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
    SELECT *
    FROM historico_chamados
    WHERE chamado_id = ?
    ORDER BY id DESC
    """, (chamado_id,))

    historico = cursor.fetchall()

    conexao.close()

    return historico


# =========================
# LISTAR CHAMADOS
# =========================
def listar_todos_chamados():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM chamados
    ORDER BY id DESC
    """)

    chamados = cursor.fetchall()

    conexao.close()

    return chamados

# =========================
# LISTAR CHAMADOS ADMIN
# =========================
def listar_chamados_admin(status="", prioridade=""):

    conexao = conectar()
    cursor = conexao.cursor()

    query = """
    SELECT
        chamados.id,
        chamados.titulo,
        chamados.status,
        chamados.prioridade,
        usuarios.nome,
        chamados.data_criacao,
        chamados.data_limite,
        CASE
            WHEN chamados.data_limite IS NOT NULL
            AND datetime(chamados.data_limite) < datetime('now', 'localtime')
            AND chamados.status NOT IN ('Resolvido', 'Encerrado')
            THEN 1
            ELSE 0
        END AS atrasado
    FROM chamados
    INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    WHERE 1 = 1
    """

    parametros = []

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

    return chamados

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
        comentarios_chamados.id,
        usuarios.nome,
        usuarios.tipo,
        comentarios_chamados.mensagem,
        comentarios_chamados.data
    FROM comentarios_chamados
    INNER JOIN usuarios
        ON comentarios_chamados.usuario_id = usuarios.id
    WHERE comentarios_chamados.chamado_id = ?
    ORDER BY comentarios_chamados.id ASC
    """, (chamado_id,))

    comentarios = cursor.fetchall()

    conexao.close()

    return comentarios

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

    return chamados


def listar_chamados_recentes_admin():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        chamados.id,
        chamados.titulo,
        chamados.status,
        chamados.prioridade,
        usuarios.nome,
        chamados.data_criacao
    FROM chamados
    INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    ORDER BY chamados.id DESC
    LIMIT 5
    """)

    chamados = cursor.fetchall()

    conexao.close()

    return chamados

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

    return anexos
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

    return anexo
