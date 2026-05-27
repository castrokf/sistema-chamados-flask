import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    send_from_directory
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
    listar_chamados_recentes_usuario,
    listar_chamados_recentes_admin,
    salvar_anexo,
    listar_anexos,
    buscar_anexo,
    buscar_responsavel_chamado,
    contar_chamados_sem_responsavel,
    contar_chamados_responsavel,
    contar_chamados_atrasados
)

from datetime import datetime, timedelta
from services.storage import (
    arquivo_remoto,
    salvar_arquivo_chamado
)
from utils.decorators import login_required

chamados = Blueprint(
    "chamados",
    __name__
)

def calcular_data_limite(prioridade):

    horas_por_prioridade = {
        "Alta": 4,
        "Média": 24,
        "Baixa": 72
    }

    horas = horas_por_prioridade.get(
        prioridade,
        72
    )

    data_limite = datetime.now() + timedelta(
        hours=horas
    )

    return data_limite.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

EXTENSOES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "pdf"
}


def extensao_permitida(nome_arquivo):

    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )

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

        chamados_recentes = listar_chamados_recentes_admin(
            organizacao_id
        )

        sem_responsavel = contar_chamados_sem_responsavel(
            organizacao_id
        )

        meus_atendimentos = contar_chamados_responsavel(
            usuario_id,
            organizacao_id
        )

        atrasados = contar_chamados_atrasados(
            organizacao_id
        )

        return render_template(
            "dashboard.html",
            nome=session["usuario_nome"],
            tipo_usuario=usuario_tipo,
            total=total,
            abertos=abertos,
            andamento=andamento,
            resolvidos=resolvidos,
            chamados_recentes=chamados_recentes,
            sem_responsavel=sem_responsavel,
            meus_atendimentos=meus_atendimentos,
            atrasados=atrasados
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

    chamados_recentes = listar_chamados_recentes_usuario(
        usuario_id
    )

    return render_template(
        "dashboard.html",
        nome=session["usuario_nome"],
        tipo_usuario=usuario_tipo,
        total=total,
        abertos=abertos,
        andamento=andamento,
        resolvidos=resolvidos,
        chamados_recentes=chamados_recentes
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
        prioridade = request.form["prioridade"]
        usuario_id = session["usuario_id"]

        data_criacao = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        data_limite = calcular_data_limite(
            prioridade
        )

        id_chamado = criar_chamado(
            titulo,
            descricao,
            prioridade,
            usuario_id,
            data_criacao,
            data_limite,
            session["organizacao_id"]
        )

        registrar_historico(
            id_chamado,
            session["usuario_id"],
            "Chamado criado pelo usuário",
            data_criacao
        )

        arquivo = request.files.get("anexo")

        if arquivo and arquivo.filename:

            if extensao_permitida(arquivo.filename):

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

            else:

                flash(
                    "Formato de arquivo não permitido. Envie PNG, JPG, JPEG ou PDF.",
                    "warning"
                )

        flash(
            "Chamado aberto com sucesso.",
            "success"
        )

        return redirect("/meus_chamados")

    return render_template(
        "novo_chamado.html"
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
        pesquisa=pesquisa
    )


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

            status_permitidos = [
                "Aberto",
                "Em andamento",
                "Resolvido",
                "Encerrado"
            ]

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
        responsavel=responsavel
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
