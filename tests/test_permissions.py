def test_dashboard_exige_login(client):
    resposta = client.get("/dashboard", follow_redirects=False)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"


def test_sessao_antiga_sem_organizacao_redireciona_login(client):
    with client.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["usuario_nome"] = "Usuario Antigo"
        sessao["usuario_tipo"] = "admin"

    resposta = client.get("/dashboard", follow_redirects=False)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"


def test_cliente_nao_acessa_painel_admin(client, login):
    login(
        nome="Cliente Teste",
        email="cliente@teste.com",
        tipo="cliente",
    )

    resposta = client.get("/admin", follow_redirects=False)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/dashboard"


def test_admin_acessa_painel_admin(client, login):
    login(
        nome="Admin Teste",
        email="admin@teste.com",
        tipo="admin",
    )

    resposta = client.get("/admin")

    assert resposta.status_code == 200
    assert "Painel Administrativo" in resposta.get_data(as_text=True)


def test_admin_cria_acesso_interno(client, login, db_module, csrf_token):
    login(
        nome="Admin Teste",
        email="admin@teste.com",
        tipo="admin",
    )

    resposta = client.post(
        "/admin/usuarios/criar",
        data={
            "nome": "Usuário Interno",
            "email": "usuario.interno@teste.com",
            "senha": "Senha@123",
            "tipo": "cliente",
            "csrf_token": csrf_token("/admin/usuarios"),
        },
        follow_redirects=False,
    )

    usuario = db_module.buscar_usuario("usuario.interno@teste.com")

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/admin/usuarios"
    assert usuario is not None
    assert usuario["tipo"] == "cliente"


def test_cliente_nao_acessa_chamado_de_outro_usuario(client, login, create_user, db_module):
    dono = create_user(
        nome="Dono do Chamado",
        email="dono@teste.com",
        tipo="cliente",
    )

    chamado_id = db_module.criar_chamado(
        "Chamado restrito",
        "Chamado criado para testar permissão.",
        "Alta",
        dono["id"],
        "01/01/2026 10:00",
        "2026-01-01 14:00:00",
    )

    login(
        nome="Outro Cliente",
        email="outro@teste.com",
        tipo="cliente",
    )

    resposta = client.get(f"/chamado/{chamado_id}", follow_redirects=False)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/dashboard"


def test_admin_nao_acessa_chamado_de_outra_organizacao(client, login, create_user, db_module):
    outra_organizacao_id = db_module.criar_organizacao(
        "Outra Empresa",
        "outra-empresa",
    )

    dono = create_user(
        nome="Usuário Outra Empresa",
        email="usuario.outra@teste.com",
        tipo="cliente",
        organizacao_id=outra_organizacao_id,
    )

    chamado_id = db_module.criar_chamado(
        "Chamado de outra organização",
        "Este chamado não deve aparecer para a empresa demo.",
        "Alta",
        dono["id"],
        "01/01/2026 10:00",
        "2026-01-01 14:00:00",
        outra_organizacao_id,
    )

    login(
        nome="Admin Empresa Demo",
        email="admin.demo@teste.com",
        tipo="admin",
    )

    resposta = client.get(f"/chamado/{chamado_id}", follow_redirects=False)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/dashboard"


def test_post_sem_csrf_e_bloqueado(client, create_user):
    create_user(
        nome="Usuário CSRF",
        email="csrf@teste.com",
        senha="Senha@123",
        tipo="cliente",
    )

    resposta = client.post(
        "/login",
        data={
            "email": "csrf@teste.com",
            "senha": "Senha@123",
        },
    )

    assert resposta.status_code == 400
