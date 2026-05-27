from functools import wraps

from flask import (
    session,
    redirect,
    flash
)


def sessao_autenticada():
    campos_obrigatorios = [
        "usuario_id",
        "usuario_nome",
        "usuario_tipo",
        "organizacao_id",
        "organizacao_nome"
    ]

    return all(
        campo in session
        for campo in campos_obrigatorios
    )


def redirecionar_login_sessao_invalida():
    session.clear()

    flash(
        "Faça login novamente para continuar.",
        "warning"
    )

    return redirect("/login")


def login_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if not sessao_autenticada():

            return redirecionar_login_sessao_invalida()

        return funcao(*args, **kwargs)

    return wrapper


def admin_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if not sessao_autenticada():

            return redirecionar_login_sessao_invalida()

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

        if not sessao_autenticada():

            return redirecionar_login_sessao_invalida()

        if session.get("usuario_tipo") not in ["admin", "suporte"]:

            flash(
                "Acesso permitido apenas para a equipe de atendimento.",
                "danger"
            )

            return redirect("/dashboard")

        return funcao(*args, **kwargs)

    return wrapper


def suporte_required(funcao):

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if not sessao_autenticada():

            return redirecionar_login_sessao_invalida()

        if session.get("usuario_tipo") != "suporte":

            flash(
                "Acesso permitido apenas para suporte.",
                "danger"
            )

            return redirect("/dashboard")

        return funcao(*args, **kwargs)

    return wrapper
