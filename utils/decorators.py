from functools import wraps

from flask import (
    session,
    redirect,
    flash
)


def login_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login para acessar esta página.",
                "warning"
            )

            return redirect("/login")

        return funcao(*args, **kwargs)

    return wrapper


def admin_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login para acessar esta página.",
                "warning"
            )

            return redirect("/login")

        if session.get("usuario_tipo") != "admin":

            flash(
                "Acesso permitido apenas para administradores.",
                "danger"
            )

            return redirect("/dashboard")

        return funcao(*args, **kwargs)

    return wrapper


def equipe_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login para acessar esta página.",
                "warning"
            )

            return redirect("/login")

        if session.get("usuario_tipo") not in ["admin", "suporte"]:

            flash(
                "Acesso permitido apenas para a equipe de atendimento.",
                "danger"
            )

            return redirect("/dashboard")

        return funcao(*args, **kwargs)

    return wrapper