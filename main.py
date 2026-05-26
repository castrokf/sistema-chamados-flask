import os

from flask import (
    Flask,
    render_template,
    redirect,
    session,
    flash,
    request
)

from database import (
    criar_tabela_usuarios,
    criar_tabela_chamados,
    criar_tabela_historico,
    criar_tabela_comentarios,
    adicionar_coluna_data_limite,
    criar_tabela_anexos,
    adicionar_coluna_usuario_historico,
    adicionar_coluna_responsavel_chamado
)

from routes.auth import auth
from routes.chamados import chamados
from routes.admin import admin


def auto_seed_demo():
    if os.environ.get("AUTO_SEED_DEMO", "").lower() != "true":
        return

    from database import conectar
    from seed_database import criar_banco_demo

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM usuarios
    """)

    total_usuarios = cursor.fetchone()[0]

    conexao.close()

    if total_usuarios == 0:
        criar_banco_demo()


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "sistema_chamados"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(
    "uploads",
    exist_ok=True
)

app.register_blueprint(auth)
app.register_blueprint(chamados)
app.register_blueprint(admin)


# Criar tabelas
criar_tabela_usuarios()
criar_tabela_chamados()
criar_tabela_historico()
criar_tabela_comentarios()
adicionar_coluna_data_limite()
criar_tabela_anexos()
adicionar_coluna_usuario_historico()
adicionar_coluna_responsavel_chamado()
auto_seed_demo()

@app.route("/")
def home():

    if "usuario_id" in session:
        return redirect("/dashboard")

    return render_template("home.html")

@app.errorhandler(413)
def arquivo_muito_grande(error):

    flash(
        "Arquivo muito grande. Envie arquivos de até 5 MB.",
        "warning"
    )

    return redirect(
        request.referrer or "/dashboard"
    )

if __name__ == "__main__":
    app.run(debug=True)
