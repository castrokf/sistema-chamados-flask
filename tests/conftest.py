import importlib
import sys

import pytest
from argon2 import PasswordHasher


MODULES_TO_RELOAD = [
    "main",
    "database",
    "routes.admin",
    "routes.auth",
    "routes.chamados",
    "routes.knowledge",
    "config",
    "utils.security",
    "utils.decorators",
]


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_chamados.db"))
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret-key")

    for module_name in MODULES_TO_RELOAD:
        sys.modules.pop(module_name, None)

    main = importlib.import_module("main")
    main.app.config.update(TESTING=True)

    return main.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_module(app):
    return importlib.import_module("database")


@pytest.fixture()
def csrf_token(client):
    def _csrf_token(caminho="/login"):
        client.get(caminho)

        with client.session_transaction() as sessao:
            return sessao["_csrf_token"]

    return _csrf_token


@pytest.fixture()
def create_user(db_module):
    ph = PasswordHasher()

    def _create_user(
        nome="Usuário Teste",
        email="usuario@teste.com",
        senha="Senha@123",
        tipo="cliente",
        organizacao_id=None,
    ):
        db_module.criar_usuario(
            nome,
            email,
            ph.hash(senha),
            tipo,
            organizacao_id,
        )

        return db_module.buscar_usuario(email)

    return _create_user


@pytest.fixture()
def login(client, create_user, csrf_token):
    def _login(
        email="usuario@teste.com",
        senha="Senha@123",
        tipo="cliente",
        nome="Usuário Teste",
    ):
        usuario = create_user(
            nome=nome,
            email=email,
            senha=senha,
            tipo=tipo,
        )

        resposta = client.post(
            "/login",
            data={
                "email": email,
                "senha": senha,
                "csrf_token": csrf_token("/login"),
            },
            follow_redirects=False,
        )

        return usuario, resposta

    return _login
