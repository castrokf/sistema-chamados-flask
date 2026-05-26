from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import (
    buscar_usuario
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
                    usuario[3],
                    senha
                )

                session["usuario_id"] = usuario[0]
                session["usuario_nome"] = usuario[1]
                session["usuario_tipo"] = usuario[4]

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
