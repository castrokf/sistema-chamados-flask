from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import (
    criar_usuario,
    buscar_usuario
)

from argon2 import PasswordHasher

from sqlite3 import IntegrityError

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

    if request.method == "POST":

        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if not nome or not email or not senha:

            flash(
                "Preencha todos os campos.",
                "warning"
            )

            return redirect("/register")

        if senha != confirmar_senha:

            flash(
                "As senhas não coincidem.",
                "danger"
            )

            return redirect("/register")

        if len(senha) < 8:

            flash(
                "A senha deve ter pelo menos 8 caracteres.",
                "warning"
            )

            return redirect("/register")

        senha_hash = ph.hash(senha)

        try:

            criar_usuario(
                nome,
                email,
                senha_hash,
                "cliente"
            )

            flash(
                "Conta criada com sucesso. Faça login para continuar.",
                "success"
            )

            return redirect("/login")

        except IntegrityError:

            flash(
                "Este email já está cadastrado.",
                "danger"
            )

            return redirect("/register")

    return render_template(
        "register.html"
    )


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
        "Logout realizado",
        "info"
    )

    return redirect("/")
