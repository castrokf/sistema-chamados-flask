import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    send_from_directory,
    jsonify
)

from database import (
    criar_chamado,
    listar_chamados_usuario,
    buscar_chamado,
    atualizar_chamado,
    contar_chamados_usuario,
    contar_chamados_status,
    buscar_chamados_usuario,
    registrar_historico,
    listar_historico,
    adicionar_comentario,
    listar_comentarios,
    contar_todos_chamados,
    contar_todos_chamados_status,
    contar_todos_chamados_prioridade,
    listar_chamados_recentes_usuario,
    listar_chamados_recentes_admin,
    salvar_anexo,
    listar_anexos,
    buscar_anexo,
    buscar_responsavel_chamado,
    buscar_usuario_por_id,
    registrar_primeira_resposta_chamado,
    contar_chamados_sem_responsavel,
    contar_chamados_responsavel,
    contar_chamados_atrasados,
    adicionar_mensagem_chamado,
    listar_mensagens_chamado,
    contar_chamados_periodo,
    listar_chamados_admin
)

from datetime import datetime
from services.storage import (
    arquivo_remoto,
    salvar_arquivo_chamado,
    UploadInvalido
)
from utils.decorators import login_required
from services.ai_triage import (
    generate_ai_summary,
    generate_ai_triage_questions,
    suggest_category,
    suggest_priority
)
from services.sla import calcular_prazos

chamados = Blueprint(
    "chamados",
    __name__
)

def calcular_data_limite(prioridade):
    return calcular_prazos(prioridade)["prazo_resolucao"]

STATUS_IA = [
    "Em triagem pela IA",
    "Aguardando informações do cliente",
    "Pronto para suporte"
]

STATUS_PERMITIDOS = [
    "Aberto",
    "Em triagem pela IA",
    "Aguardando informações do cliente",
    "Pronto para suporte",
    "Em andamento",
    "Aguardando cliente",
    "Resolvido",
    "Encerrado",
    "Reaberto"
]


def item_grafico(rotulo, valor, classe, total):
    percentual = 0

    if total:
        percentual = round((valor / total) * 100)

    return {
        "rotulo": rotulo,
        "valor": valor,
        "classe": classe,
        "percentual": percentual
    }

# =========================
# DASHBOARD
# =========================
@chamados.route("/dashboard")
@login_required
def dashboard():

    usuario_id = session["usuario_id"]
    usuario_tipo = session["usuario_tipo"]
    organizacao_id = session["organizacao_id"]

    if usuario_tipo in ["admin", "suporte"]:

        total = contar_todos_chamados(
            organizacao_id
        )

        abertos = contar_todos_chamados_status(
            "Aberto",
            organizacao_id
        )

        andamento = contar_todos_chamados_status(
            "Em andamento",
            organizacao_id
        )

        resolvidos = contar_todos_chamados_status(
            "Resolvido",
            organizacao_id
        )

        triagem_ia = contar_todos_chamados_status(
            "Em triagem pela IA",
            organizacao_id
        )

        prontos_suporte = contar_todos_chamados_status(
            "Pronto para suporte",
            organizacao_id
        )

        encerrados = contar_todos_chamados_status(
            "Encerrado",
            organizacao_id
        )

        urgentes = contar_todos_chamados_prioridade(
            "Urgente",
            organizacao_id
        )

        chamados_recentes = listar_chamados_recentes_admin(
            organizacao_id
        )

        sem_responsavel = contar_chamados_sem_responsavel(
            organizacao_id
        )

        meus_atendimentos = 0

        if usuario_tipo == "suporte":

            meus_atendimentos = contar_chamados_responsavel(
                usuario_id,
                organizacao_id
            )

        atrasados = contar_chamados_atrasados(
            organizacao_id
        )

        status_grafico = [
            item_grafico("Abertos", abertos, "status-open", total),
            item_grafico("Em andamento", andamento, "status-progress", total),
            item_grafico("Resolvidos", resolvidos, "status-solved", total),
            item_grafico("Em triagem IA", triagem_ia, "status-ai", total),
            item_grafico("Prontos suporte", prontos_suporte, "status-ready", total),
            item_grafico("Encerrados", encerrados, "status-closed", total),
        ]

        operacao_total = sem_responsavel + meus_atendimentos + atrasados
        operacao_grafico = [
            item_grafico("Sem responsável", sem_responsavel, "risk-attention", operacao_total),
            item_grafico("Meus atendimentos", meus_atendimentos, "risk-owned", operacao_total),
            item_grafico("Fora do prazo", atrasados, "risk-late", operacao_total),
        ]

        return render_template(
            "dashboard.html",
            nome=session["usuario_nome"],
            tipo_usuario=usuario_tipo,
            page_title="Dashboard - Nortia",
            page_heading="Centro de controle",
            page_subtitle=f"Bem-vindo, {session['usuario_nome']}.",
            total=total,
            abertos=abertos,
            andamento=andamento,
            resolvidos=resolvidos,
            triagem_ia=triagem_ia,
            prontos_suporte=prontos_suporte,
            encerrados=encerrados,
            chamados_recentes=chamados_recentes,
            sem_responsavel=sem_responsavel,
            meus_atendimentos=meus_atendimentos,
            atrasados=atrasados,
            urgentes=urgentes,
            status_grafico=status_grafico,
            operacao_grafico=operacao_grafico
        )

    total = contar_chamados_usuario(
        usuario_id
    )

    abertos = contar_chamados_status(
        usuario_id,
        "Aberto"
    )

    andamento = contar_chamados_status(
        usuario_id,
        "Em andamento"
    )

    resolvidos = contar_chamados_status(
        usuario_id,
        "Resolvido"
    )

    triagem_ia = contar_chamados_status(
        usuario_id,
        "Em triagem pela IA"
    )

    prontos_suporte = contar_chamados_status(
        usuario_id,
        "Pronto para suporte"
    )

    encerrados = contar_chamados_status(
        usuario_id,
        "Encerrado"
    )

    chamados_recentes = listar_chamados_recentes_usuario(
        usuario_id
    )

    status_grafico = [
        item_grafico("Abertos", abertos, "status-open", total),
        item_grafico("Em andamento", andamento, "status-progress", total),
        item_grafico("Resolvidos", resolvidos, "status-solved", total),
        item_grafico("Em triagem IA", triagem_ia, "status-ai", total),
        item_grafico("Prontos suporte", prontos_suporte, "status-ready", total),
        item_grafico("Encerrados", encerrados, "status-closed", total),
    ]

    return render_template(
        "dashboard.html",
        nome=session["usuario_nome"],
        tipo_usuario=usuario_tipo,
        page_title="Dashboard - Nortia",
        page_heading="Centro de controle",
        page_subtitle=f"Bem-vindo, {session['usuario_nome']}.",
        total=total,
        abertos=abertos,
        andamento=andamento,
        resolvidos=resolvidos,
        triagem_ia=triagem_ia,
        prontos_suporte=prontos_suporte,
        chamados_recentes=chamados_recentes,
        status_grafico=status_grafico
    )


# =========================
# NOVO CHAMADO
# =========================
@chamados.route(
    "/novo_chamado",
    methods=["GET", "POST"]
)
@login_required
def novo_chamado():

    if request.method == "POST":

        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        urgencia_extrema = request.form.get("urgencia_extrema") == "on"
        usuario_id = session["usuario_id"]

        ticket_preview = {
            "titulo": titulo,
            "descricao": descricao
        }

        categoria_ia = suggest_category(ticket_preview)
        prioridade_ia = suggest_priority(ticket_preview)
        prioridade = "Urgente" if urgencia_extrema else prioridade_ia
        resumo_ia = generate_ai_summary(ticket_preview)

        data_criacao = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        prazos_sla = calcular_prazos(prioridade)
        data_limite = prazos_sla["prazo_resolucao"]

        id_chamado = criar_chamado(
            titulo,
            descricao,
            prioridade,
            usuario_id,
            data_criacao,
            data_limite,
            session["organizacao_id"],
            status_inicial="Em triagem pela IA",
            ai_summary=resumo_ia,
            ai_suggested_category=categoria_ia,
            ai_suggested_priority=prioridade_ia,
            ai_confidence=92,
            ai_status="em_triagem",
            triage_started_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            categoria=categoria_ia,
            tipo="Solicitação",
            prazo_primeira_resposta=prazos_sla["prazo_primeira_resposta"],
            prazo_resolucao=prazos_sla["prazo_resolucao"]
        )

        registrar_historico(
            id_chamado,
            session["usuario_id"],
            "Chamado criado pelo usuário",
            data_criacao
        )

        adicionar_mensagem_chamado(
            id_chamado,
            None,
            "ai",
            "Olá! Vou coletar algumas informações para agilizar seu atendimento.",
            data_criacao
        )

        for pergunta in generate_ai_triage_questions(ticket_preview):
            adicionar_mensagem_chamado(
                id_chamado,
                None,
                "ai",
                pergunta,
                data_criacao
            )

        if urgencia_extrema:

            registrar_historico(
                id_chamado,
                session["usuario_id"],
                "Solicitação marcada como urgência extrema pelo usuário",
                data_criacao
            )

        arquivo = request.files.get("anexo")

        if arquivo and arquivo.filename:

            try:
                anexo_salvo = salvar_arquivo_chamado(
                    arquivo,
                    id_chamado
                )

                salvar_anexo(
                    id_chamado,
                    anexo_salvo["nome_arquivo"],
                    anexo_salvo["caminho_arquivo"],
                    data_criacao
                )

                registrar_historico(
                    id_chamado,
                    session["usuario_id"],
                    "Anexo enviado pelo usuário",
                    data_criacao
                )

            except UploadInvalido as erro:
                flash(
                    str(erro),
                    "warning"
                )

        flash(
            "Solicitação registrada com sucesso. A triagem inteligente já foi iniciada.",
            "success"
        )

        return redirect("/meus_chamados")

    return render_template(
        "novo_chamado.html",
        page_title="Nova solicitação - Nortia",
        page_heading="Nova solicitação",
        page_subtitle="Descreva o contexto para iniciar a triagem inteligente e acelerar o atendimento"
    )


# =========================
# MEUS CHAMADOS
# =========================
@chamados.route("/meus_chamados")
@login_required
def meus_chamados():

    usuario_id = session["usuario_id"]

    pesquisa = request.args.get(
        "pesquisa",
        ""
    )

    if pesquisa:

        lista_chamados = buscar_chamados_usuario(
            usuario_id,
            pesquisa
        )

    else:

        lista_chamados = listar_chamados_usuario(
            usuario_id
        )

    return render_template(
        "meus_chamados.html",
        chamados=lista_chamados,
        pesquisa=pesquisa,
        page_title="Minhas solicitações - Nortia",
        page_heading="Minhas solicitações",
        page_subtitle="Acompanhe solicitações, prazos e atualizações da equipe de atendimento"
    )


@chamados.route("/chamados")
@login_required
def chamados_alias():
    if session["usuario_tipo"] in ["admin", "suporte"]:
        return redirect("/admin")

    return redirect("/meus_chamados")


@chamados.route("/chamados/novo")
@login_required
def novo_chamado_alias():
    return redirect("/novo_chamado")


# =========================
# VISUALIZAR CHAMADO
# =========================
@chamados.route(
    "/chamado/<int:id_chamado>",
    methods=["GET", "POST"]
)
@login_required
def visualizar_chamado(id_chamado):

    chamado = buscar_chamado(
        id_chamado,
        session["organizacao_id"]
    )

    responsavel = buscar_responsavel_chamado(
        id_chamado
    )

    if not chamado:

        flash(
            "Chamado não encontrado.",
            "danger"
        )

        return redirect("/dashboard")

    usuario_logado = session["usuario_id"]
    tipo_usuario = session["usuario_tipo"]
    dono_chamado = chamado["usuario_id"]

    if tipo_usuario not in ["admin", "suporte"] and usuario_logado != dono_chamado:

        flash(
            "Você não tem permissão para acessar este chamado.",
            "danger"
        )

        return redirect("/dashboard")

    historico = listar_historico(
        id_chamado
    )

    comentarios = listar_comentarios(
        id_chamado
    )

    anexos = listar_anexos(
        id_chamado
    )

    mensagens = listar_mensagens_chamado(
        id_chamado,
        tipo_usuario in ["admin", "suporte"]
    )

    solicitante = buscar_usuario_por_id(
        chamado["usuario_id"]
    )

    perguntas_ia = generate_ai_triage_questions(chamado)

    if request.method == "POST":

        acao = request.form.get("acao")

        if acao == "comentario":

            if chamado["status"] == "Encerrado":

                flash(
                    "Não é possível comentar em um chamado encerrado.",
                    "warning"
                )

                return redirect(
                    f"/chamado/{id_chamado}"
                )

            mensagem = request.form["mensagem"].strip()

            if not mensagem:

                flash(
                    "O comentário não pode estar vazio.",
                    "warning"
                )

                return redirect(
                    f"/chamado/{id_chamado}"
                )

            data_comentario = datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

            adicionar_comentario(
                id_chamado,
                usuario_logado,
                mensagem,
                data_comentario
            )

            adicionar_mensagem_chamado(
                id_chamado,
                usuario_logado,
                "support" if tipo_usuario in ["admin", "suporte"] else "user",
                mensagem,
                data_comentario
            )

            registrar_historico(
                id_chamado,
                usuario_logado,
                "Novo comentário adicionado",
                data_comentario
            )

            if tipo_usuario not in ["admin", "suporte"] and chamado["status"] == "Resolvido":

                atualizar_chamado(
                    id_chamado,
                    chamado["resposta"],
                    "Em andamento",
                    session["organizacao_id"]
                )

                registrar_historico(
                    id_chamado,
                    usuario_logado,
                    "Chamado reaberto pelo usuário",
                    data_comentario
                )

            flash(
                "Comentário adicionado com sucesso.",
                "success"
            )

            return redirect(
                f"/chamado/{id_chamado}"
            )

        if acao == "atualizar_chamado":

            if tipo_usuario not in ["admin", "suporte"]:

                flash(
                    "Apenas administradores podem atualizar chamados.",
                    "danger"
                )

                return redirect(
                    f"/chamado/{id_chamado}"
                )

            status_permitidos = STATUS_PERMITIDOS

            resposta = request.form["resposta"].strip()
            status = request.form["status"]

            if status not in status_permitidos:

                flash(
                    "Status inválido.",
                    "danger"
                )

                return redirect(
                    f"/chamado/{id_chamado}"
                )

            atualizar_chamado(
                id_chamado,
                resposta,
                status,
                session["organizacao_id"]
            )

            if resposta:
                registrar_primeira_resposta_chamado(
                    id_chamado,
                    session["organizacao_id"]
                )

            data_atualizacao = datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

            if chamado["status"] != status:

                registrar_historico(
                    id_chamado,
                    usuario_logado,
                    f"Status alterado de {chamado['status']} para {status}",
                    data_atualizacao
                )

            else:

                registrar_historico(
                    id_chamado,
                    usuario_logado,
                    "Resposta administrativa atualizada",
                    data_atualizacao
                )

            flash(
                "Chamado atualizado com sucesso.",
                "success"
            )

            return redirect(
                f"/chamado/{id_chamado}"
            )

    return render_template(
        "visualizar_chamado.html",
        chamado=chamado,
        historico=historico,
        comentarios=comentarios,
        anexos=anexos,
        responsavel=responsavel,
        solicitante=solicitante,
        mensagens=mensagens,
        perguntas_ia=perguntas_ia,
        page_title=f"Chamado CH-{id_chamado:04d} - Nortia",
        page_heading=f"Chamado CH-{id_chamado:04d}",
        page_subtitle="Resumo executivo, tratativa e apoio da triagem inteligente"
    )

# =========================
# VISUALIZAR ANEXOS
# =========================
@chamados.route("/anexo/<int:id_anexo>")
@login_required
def visualizar_anexo(id_anexo):

    anexo = buscar_anexo(id_anexo)

    if not anexo:

        flash(
            "Anexo não encontrado.",
            "danger"
        )

        return redirect("/dashboard")

    chamado_id = anexo["chamado_id"]

    chamado = buscar_chamado(
        chamado_id,
        session["organizacao_id"]
    )

    if not chamado:

        flash(
            "Chamado não encontrado.",
            "danger"
        )

        return redirect("/dashboard")

    if (
        session.get("usuario_tipo") not in ["admin", "suporte"]
        and session.get("usuario_id") != chamado["usuario_id"]
    ):

        flash(
            "Você não tem permissão para acessar este anexo.",
            "danger"
        )

        return redirect("/dashboard")

    caminho_arquivo = anexo["caminho_arquivo"]

    if arquivo_remoto(caminho_arquivo):

        return redirect(caminho_arquivo)

    nome_arquivo = os.path.basename(caminho_arquivo)

    return send_from_directory(
        "uploads",
        nome_arquivo
    )


@chamados.route("/api/dashboard/stats")
@login_required
def dashboard_stats():
    organizacao_id = session["organizacao_id"]
    tipo_usuario = session["usuario_tipo"]

    if tipo_usuario in ["admin", "suporte"]:
        total = contar_todos_chamados(organizacao_id)
        abertos = contar_todos_chamados_status("Aberto", organizacao_id)
        andamento = contar_todos_chamados_status("Em andamento", organizacao_id)
        resolvidos = contar_todos_chamados_status("Resolvido", organizacao_id)
        triagem = contar_todos_chamados_status("Em triagem pela IA", organizacao_id)
        prontos = contar_todos_chamados_status("Pronto para suporte", organizacao_id)
        periodo = contar_chamados_periodo(organizacao_id)
    else:
        usuario_id = session["usuario_id"]
        total = contar_chamados_usuario(usuario_id)
        abertos = contar_chamados_status(usuario_id, "Aberto")
        andamento = contar_chamados_status(usuario_id, "Em andamento")
        resolvidos = contar_chamados_status(usuario_id, "Resolvido")
        triagem = contar_chamados_status(usuario_id, "Em triagem pela IA")
        prontos = contar_chamados_status(usuario_id, "Pronto para suporte")
        periodo = []

    periodo = list(reversed(periodo))

    return jsonify({
        "cards": {
            "total": total,
            "abertos": abertos,
            "andamento": andamento,
            "resolvidos": resolvidos,
            "triagem": triagem,
            "prontos": prontos
        },
        "period": {
            "labels": [item["dia"] for item in periodo] or ["D-6", "D-5", "D-4", "D-3", "D-2", "Ontem", "Hoje"],
            "values": [item["total"] for item in periodo] or [0, 0, 0, 0, 0, 0, total]
        },
        "status": {
            "labels": ["Abertos", "Em andamento", "Resolvidos", "Em triagem IA", "Prontos para suporte"],
            "values": [abertos, andamento, resolvidos, triagem, prontos]
        }
    })


@chamados.route("/triagem-inteligente")
@login_required
def triagem_inteligente():
    organizacao_id = session["organizacao_id"]
    status = request.args.get("status", "")

    if status and status not in STATUS_IA:
        status = ""

    chamados_triagem = []

    if session["usuario_tipo"] in ["admin", "suporte"]:
        for status_ia in ([status] if status else STATUS_IA):
            chamados_triagem.extend(
                listar_chamados_admin(
                    status_ia,
                    "",
                    "",
                    organizacao_id
                )
            )
    else:
        chamados_triagem = [
            chamado
            for chamado in listar_chamados_usuario(session["usuario_id"])
            if chamado["status"] in STATUS_IA
        ]

    return render_template(
        "triagem_inteligente.html",
        chamados=chamados_triagem,
        status=status,
        status_ia=STATUS_IA,
        page_title="Triagem Inteligente - Nortia",
        page_heading="Triagem Inteligente",
        page_subtitle="Monitore solicitações analisadas pela IA antes da atuação do suporte"
    )


@chamados.route("/relatorios")
@login_required
def relatorios():
    return render_template(
        "relatorios.html",
        page_title="Relatórios - Nortia",
        page_heading="Relatórios",
        page_subtitle="Acompanhe tendências, status e indicadores de atendimento"
    )


@chamados.route("/configuracoes")
@login_required
def configuracoes():
    return render_template(
        "configuracoes.html",
        page_title="Configurações - Nortia",
        page_heading="Configurações",
        page_subtitle="Parâmetros operacionais, integrações e preparação para automações"
    )


@chamados.route("/perfil")
@login_required
def perfil():
    usuario = buscar_usuario_por_id(
        session["usuario_id"]
    )

    return render_template(
        "perfil.html",
        usuario=usuario,
        page_title="Perfil corporativo - Nortia",
        page_heading="Perfil corporativo",
        page_subtitle="Dados do usuário, perfil de acesso e atalhos administrativos"
    )


@chamados.route("/chamado/<int:id_chamado>/messages", methods=["GET", "POST"])
@login_required
def mensagens_chamado(id_chamado):
    chamado = buscar_chamado(
        id_chamado,
        session["organizacao_id"]
    )

    if not chamado:
        return jsonify({
            "error": "Chamado não encontrado"
        }), 404

    if (
        session["usuario_tipo"] not in ["admin", "suporte"]
        and session["usuario_id"] != chamado["usuario_id"]
    ):
        return jsonify({
            "error": "Sem permissão"
        }), 403

    if request.method == "POST":
        mensagem = request.form.get("message", "").strip()
        is_internal = request.form.get("is_internal") == "true"

        if not mensagem:
            return jsonify({
                "error": "Mensagem vazia"
            }), 400

        if is_internal and session["usuario_tipo"] not in ["admin", "suporte"]:
            return jsonify({
                "error": "Notas internas são restritas à equipe de atendimento"
            }), 403

        sender_type = "support" if session["usuario_tipo"] in ["admin", "suporte"] else "user"

        adicionar_mensagem_chamado(
            id_chamado,
            session["usuario_id"],
            sender_type,
            mensagem,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            is_internal=1 if is_internal else 0
        )

        registrar_historico(
            id_chamado,
            session["usuario_id"],
            "Nota interna adicionada" if is_internal else "Resposta pública enviada",
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )

        if sender_type == "support":
            registrar_primeira_resposta_chamado(
                id_chamado,
                session["organizacao_id"]
            )

    mensagens = listar_mensagens_chamado(
        id_chamado,
        session["usuario_tipo"] in ["admin", "suporte"]
    )

    labels = {
        "user": "Cliente",
        "support": "Suporte",
        "admin": "Administrador",
        "ai": "Assistente Nortia",
        "system": "Sistema"
    }

    return jsonify([
        {
            "id": mensagem["id"],
            "sender_type": mensagem["sender_type"],
            "sender_label": mensagem["sender_name"] or labels.get(mensagem["sender_type"], "Sistema"),
            "message": mensagem["message"],
            "created_at": mensagem["created_at"],
            "is_internal": mensagem["is_internal"]
        }
        for mensagem in mensagens
    ])
