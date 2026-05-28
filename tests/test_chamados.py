def test_cliente_cria_chamado(client, login, db_module, csrf_token):
    usuario, _ = login(
        nome="Cliente Teste",
        email="cliente@teste.com",
        tipo="cliente",
    )

    resposta = client.post(
        "/novo_chamado",
        data={
            "titulo": "Erro de acesso",
            "descricao": "Não consigo acessar uma área do sistema.",
            "csrf_token": csrf_token("/novo_chamado"),
        },
        follow_redirects=False,
    )

    chamados = db_module.listar_chamados_usuario(usuario["id"])
    historico = db_module.listar_historico(chamados[0]["id"])

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/meus_chamados"
    assert len(chamados) == 1
    assert chamados[0]["titulo"] == "Erro de acesso"
    assert chamados[0]["status"] == "Em triagem pela IA"
    assert chamados[0]["prioridade"] == "Média"
    assert len(historico) == 1


def test_cliente_solicita_urgencia_extrema(client, login, db_module, csrf_token):
    usuario, _ = login(
        nome="Cliente Teste",
        email="cliente.urgente@teste.com",
        tipo="cliente",
    )

    resposta = client.post(
        "/novo_chamado",
        data={
            "titulo": "Sistema parado",
            "descricao": "A operação crítica está totalmente indisponível.",
            "urgencia_extrema": "on",
            "csrf_token": csrf_token("/novo_chamado"),
        },
        follow_redirects=False,
    )

    chamados = db_module.listar_chamados_usuario(usuario["id"])
    historico = db_module.listar_historico(chamados[0]["id"])

    assert resposta.status_code == 302
    assert chamados[0]["prioridade"] == "Urgente"
    assert len(historico) == 2


def test_cliente_adiciona_comentario(client, login, db_module, csrf_token):
    usuario, _ = login(
        nome="Cliente Teste",
        email="cliente@teste.com",
        tipo="cliente",
    )

    chamado_id = db_module.criar_chamado(
        "Chamado com comentário",
        "Descrição do chamado.",
        "Baixa",
        usuario["id"],
        "01/01/2026 10:00",
        "2026-01-04 10:00:00",
    )

    resposta = client.post(
        f"/chamado/{chamado_id}",
        data={
            "acao": "comentario",
            "mensagem": "Comentário de acompanhamento.",
            "csrf_token": csrf_token(f"/chamado/{chamado_id}"),
        },
        follow_redirects=False,
    )

    comentarios = db_module.listar_comentarios(chamado_id)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == f"/chamado/{chamado_id}"
    assert len(comentarios) == 1
    assert comentarios[0]["mensagem"] == "Comentário de acompanhamento."


def test_admin_atualiza_status_do_chamado(client, login, create_user, db_module, csrf_token):
    cliente = create_user(
        nome="Cliente Teste",
        email="cliente@teste.com",
        tipo="cliente",
    )

    chamado_id = db_module.criar_chamado(
        "Chamado para atualizar",
        "Descrição do chamado.",
        "Média",
        cliente["id"],
        "01/01/2026 10:00",
        "2026-01-02 10:00:00",
    )

    login(
        nome="Admin Teste",
        email="admin@teste.com",
        tipo="admin",
    )

    resposta = client.post(
        f"/chamado/{chamado_id}",
        data={
            "acao": "atualizar_chamado",
            "resposta": "Chamado resolvido pela equipe.",
            "status": "Resolvido",
            "csrf_token": csrf_token(f"/chamado/{chamado_id}"),
        },
        follow_redirects=False,
    )

    chamado = db_module.buscar_chamado(chamado_id)
    historico = db_module.listar_historico(chamado_id)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == f"/chamado/{chamado_id}"
    assert chamado["status"] == "Resolvido"
    assert chamado["resposta"] == "Chamado resolvido pela equipe."
    assert len(historico) == 1


def test_suporte_assume_chamado_aberto(client, login, create_user, db_module, csrf_token):
    cliente = create_user(
        nome="Cliente Teste",
        email="cliente@teste.com",
        tipo="cliente",
    )

    chamado_id = db_module.criar_chamado(
        "Chamado aberto",
        "Descrição do chamado.",
        "Alta",
        cliente["id"],
        "01/01/2026 10:00",
        "2026-01-01 14:00:00",
    )

    suporte, _ = login(
        nome="Suporte Teste",
        email="suporte@teste.com",
        tipo="suporte",
    )

    resposta = client.post(
        f"/admin/chamado/{chamado_id}/assumir",
        data={
            "csrf_token": csrf_token(f"/chamado/{chamado_id}"),
        },
        follow_redirects=False,
    )

    chamado = db_module.buscar_chamado(chamado_id)
    responsavel = db_module.buscar_responsavel_chamado(chamado_id)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == f"/chamado/{chamado_id}"
    assert chamado["status"] == "Em andamento"
    assert chamado["responsavel_id"] == suporte["id"]
    assert responsavel == "Suporte Teste"
