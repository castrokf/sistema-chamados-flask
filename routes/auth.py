import os
import secrets
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import (
    atualizar_senha_usuario,
    buscar_token_recuperacao,
    buscar_usuario,
    criar_token_recuperacao,
    marcar_token_recuperacao_usado
)

from argon2 import PasswordHasher

auth = Blueprint(
    "auth",
    __name__
)

ph = PasswordHasher()
# =========================
# CADASTRO
# =========================
@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    flash(
        "O cadastro público está desativado. Solicite acesso à equipe responsável.",
        "warning"
    )

    return redirect("/login")


# =========================
# LOGIN
# =========================
@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        usuario = buscar_usuario(email)

        if usuario:

            try:

                ph.verify(
                    usuario["senha"],
                    senha
                )

                session["usuario_id"] = usuario["id"]
                session["usuario_nome"] = usuario["nome"]
                session["usuario_tipo"] = usuario["tipo"]

                return redirect("/dashboard")

            except:

                flash(
                    "Email ou senha incorretos.",
                    "danger"
                )

                return redirect("/login")

        flash(
            "Usuário não encontrado.",
            "danger"
        )

        return redirect("/login")

    return render_template(
        "login.html"
    )


@auth.route(
    "/recuperar-senha",
    methods=["GET", "POST"]
)
def recuperar_senha():

    link_recuperacao = None

    if request.method == "POST":

        email = request.form["email"].strip()

        usuario = buscar_usuario(email)

        if usuario:

            token = secrets.token_urlsafe(32)

            data_criacao = datetime.now()
            expira_em = data_criacao + timedelta(minutes=30)

            criar_token_recuperacao(
                usuario["id"],
                token,
                expira_em.strftime("%Y-%m-%d %H:%M:%S"),
                data_criacao.strftime("%Y-%m-%d %H:%M:%S")
            )

            link_recuperacao = request.url_root.rstrip("/") + f"/redefinir-senha/{token}"

            if os.environ.get("SHOW_RESET_LINK", "true").lower() == "true":

                flash(
                    "Link de recuperação gerado para ambiente de demonstração.",
                    "info"
                )

            else:

                link_recuperacao = None

        flash(
            "Se o email estiver cadastrado, as instruções de recuperação serão disponibilizadas.",
            "success"
        )

    return render_template(
        "recuperar_senha.html",
        link_recuperacao=link_recuperacao
    )


@auth.route(
    "/redefinir-senha/<token>",
    methods=["GET", "POST"]
)
def redefinir_senha(token):

    recuperacao = buscar_token_recuperacao(token)

    if not recuperacao or recuperacao["usado"]:

        flash(
            "Link de recuperação inválido ou já utilizado.",
            "danger"
        )

        return redirect("/login")

    expira_em = datetime.strptime(
        recuperacao["expira_em"],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expira_em:

        flash(
            "Link de recuperação expirado. Solicite um novo acesso.",
            "warning"
        )

        return redirect("/recuperar-senha")

    if request.method == "POST":

        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if senha != confirmar_senha:

            flash(
                "As senhas não coincidem.",
                "danger"
            )

            return redirect(f"/redefinir-senha/{token}")

        if len(senha) < 8:

            flash(
                "A nova senha deve ter pelo menos 8 caracteres.",
                "warning"
            )

            return redirect(f"/redefinir-senha/{token}")

        atualizar_senha_usuario(
            recuperacao["usuario_id"],
            ph.hash(senha)
        )

        marcar_token_recuperacao_usado(token)

        flash(
            "Senha redefinida com sucesso. Acesse o portal com a nova senha.",
            "success"
        )

        return redirect("/login")

    return render_template(
        "redefinir_senha.html",
        token=token,
        email=recuperacao["usuario_email"]
    )



# =========================
# LOGOUT
# =========================
@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "Você saiu do sistema com segurança.",
        "success"
    )

    return redirect("/login")
