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

from routes.auth import auth
from routes.chamados import chamados
from routes.admin import admin
from utils.security import csrf_token, validar_csrf_token


def auto_seed_demo():
    if os.environ.get("AUTO_SEED_DEMO", "").lower() != "true":
        return

    from seed_database import criar_banco_demo

    if contar_usuarios_total() == 0:
        criar_banco_demo(recriar=False)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "sistema_chamados"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get(
    "SESSION_COOKIE_SECURE",
    "false"
).lower() == "true"

os.makedirs(
    "uploads",
    exist_ok=True
)

app.register_blueprint(auth)
app.register_blueprint(chamados)
app.register_blueprint(admin)


inicializar_banco()
auto_seed_demo()


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
