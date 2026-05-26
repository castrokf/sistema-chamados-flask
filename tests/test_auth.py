import re


def test_paginas_publicas_renderizam(client):
    for caminho in ["/", "/login", "/recuperar-senha"]:
        resposta = client.get(caminho)

        assert resposta.status_code == 200


def test_cadastro_publico_redireciona_para_login(client, db_module):
    resposta = client.get("/register", follow_redirects=False)

    usuario = db_module.buscar_usuario("cliente.novo@teste.com")

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"
    assert usuario is None


def test_login_com_senha_correta_redireciona_para_dashboard(client, create_user):
    create_user(
        nome="Admin Teste",
        email="admin@teste.com",
        senha="Senha@123",
        tipo="admin",
    )

    resposta = client.post(
        "/login",
        data={
            "email": "admin@teste.com",
            "senha": "Senha@123",
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/dashboard"


def test_login_com_senha_incorreta_volta_para_login(client, create_user):
    create_user(
        nome="Cliente Teste",
        email="cliente@teste.com",
        senha="Senha@123",
        tipo="cliente",
    )

    resposta = client.post(
        "/login",
        data={
            "email": "cliente@teste.com",
            "senha": "senha-incorreta",
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"


def test_recuperacao_de_senha_redefine_acesso(client, create_user):
    create_user(
        nome="Usuário Recuperação",
        email="recuperacao@teste.com",
        senha="Senha@123",
        tipo="cliente",
    )

    resposta = client.post(
        "/recuperar-senha",
        data={
            "email": "recuperacao@teste.com",
        },
        follow_redirects=True,
    )

    html = resposta.get_data(as_text=True)
    resultado = re.search(r"/redefinir-senha/([A-Za-z0-9_-]+)", html)

    assert resposta.status_code == 200
    assert resultado is not None

    token = resultado.group(1)

    resposta_redefinicao = client.post(
        f"/redefinir-senha/{token}",
        data={
            "senha": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123",
        },
        follow_redirects=False,
    )

    assert resposta_redefinicao.status_code == 302
    assert resposta_redefinicao.headers["Location"] == "/login"

    resposta_login = client.post(
        "/login",
        data={
            "email": "recuperacao@teste.com",
            "senha": "NovaSenha@123",
        },
        follow_redirects=False,
    )

    assert resposta_login.status_code == 302
    assert resposta_login.headers["Location"] == "/dashboard"
