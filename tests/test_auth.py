def test_paginas_publicas_renderizam(client):
    for caminho in ["/", "/login", "/register"]:
        resposta = client.get(caminho)

        assert resposta.status_code == 200


def test_cadastro_cria_usuario_cliente(client, db_module):
    resposta = client.post(
        "/register",
        data={
            "nome": "Cliente Novo",
            "email": "cliente.novo@teste.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123",
        },
        follow_redirects=False,
    )

    usuario = db_module.buscar_usuario("cliente.novo@teste.com")

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"
    assert usuario is not None
    assert usuario[4] == "cliente"


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
