"""helpdesk foundation

Revision ID: 0001_helpdesk_foundation
Revises:
Create Date: 2026-06-02
"""

from alembic import op


revision = "0001_helpdesk_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS categorias_chamados (
        id INTEGER PRIMARY KEY,
        organizacao_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS tipos_chamados (
        id INTEGER PRIMARY KEY,
        organizacao_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS regras_sla (
        id INTEGER PRIMARY KEY,
        organizacao_id INTEGER NOT NULL,
        prioridade TEXT NOT NULL,
        horas_primeira_resposta INTEGER NOT NULL,
        horas_resolucao INTEGER NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS ticket_sla_pauses (
        id INTEGER PRIMARY KEY,
        ticket_id INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        reason TEXT NOT NULL,
        created_by INTEGER
    )
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_articles (
        id INTEGER PRIMARY KEY,
        organizacao_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        slug TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        visibility TEXT NOT NULL DEFAULT 'public',
        created_by INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_organizacao ON chamados (organizacao_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_usuario ON chamados (usuario_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_responsavel ON chamados (responsavel_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados (status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_prioridade ON chamados (prioridade)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_data_criacao ON chamados (data_criacao)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_chamados_data_limite ON chamados (data_limite)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_anexos_chamado ON anexos_chamados (chamado_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_mensagens_ticket ON ticket_messages (ticket_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_historico_chamado ON historico_chamados (chamado_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kb_organizacao ON knowledge_articles (organizacao_id)")


def downgrade():
    pass
