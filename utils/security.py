import secrets
from hmac import compare_digest

from flask import session


def csrf_token():
    token = session.get("_csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token

    return token


def validar_csrf_token(token_enviado):
    token_sessao = session.get("_csrf_token")

    if not token_sessao or not token_enviado:
        return False

    return compare_digest(
        token_sessao,
        token_enviado
    )
