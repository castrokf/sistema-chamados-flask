import os

from flask import (
    Flask,
    render_template,
    redirect,
    session,
    flash,
    request,
    abort
)

from database import (
    contar_usuarios_total,
    inicializar_banco
)

from config import carregar_configuracao
from routes.auth import auth
from routes.chamados import chamados
from routes.admin import admin
from routes.knowledge import knowledge
from utils.decorators import sessao_autenticada
from utils.security import csrf_token, validar_csrf_token


def auto_seed_initial_data():
    seed_ativo = (
        os.environ.get("AUTO_SEED_INITIAL_DATA", "").lower() == "true"
        or os.environ.get("AUTO_SEED_DEMO", "").lower() == "true"
    )

    if not seed_ativo:
        return

    from seed_database import criar_banco_inicial

    if contar_usuarios_total() == 0:
        criar_banco_inicial(recriar=False)


configuracao = carregar_configuracao()

app = Flask(__name__)

app.secret_key = configuracao.secret_key
app.config["APP_ENV"] = configuracao.env
app.config["MAX_CONTENT_LENGTH"] = configuracao.max_content_length
app.config["SESSION_COOKIE_HTTPONLY"] = configuracao.session_cookie_httponly
app.config["SESSION_COOKIE_SAMESITE"] = configuracao.session_cookie_samesite
app.config["SESSION_COOKIE_SECURE"] = configuracao.session_cookie_secure

os.makedirs(
    "uploads",
    exist_ok=True
)

app.register_blueprint(auth)
app.register_blueprint(chamados)
app.register_blueprint(admin)
app.register_blueprint(knowledge)


inicializar_banco()
auto_seed_initial_data()


@app.context_processor
def injetar_csrf_token():
    return {
        "csrf_token": csrf_token
    }


@app.before_request
def proteger_requisicoes_post():
    if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
        return

    if app.config.get("TESTING") and os.environ.get("DISABLE_CSRF_TESTS") == "true":
        return

    token_enviado = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")

    if not validar_csrf_token(token_enviado):
        abort(400)

@app.route("/")
def home():

    if sessao_autenticada():
        return redirect("/dashboard")

    if "usuario_id" in session:
        session.clear()

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
