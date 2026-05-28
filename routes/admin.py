from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import (
    criar_usuario,
    listar_chamados_admin,
    listar_usuarios,
    atualizar_tipo_usuario,
    listar_suportes,
    atribuir_responsavel_chamado,
    registrar_historico,
    listar_chamados_responsavel,
    buscar_chamado,
    atualizar_chamado
)

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError

from utils.decorators import (
    admin_required,
    equipe_required,
    suporte_required
)


admin = Blueprint(
    "admin",
    __name__
)

ph = PasswordHasher()


@admin.route("/admin")
@equipe_required
def painel_admin():

    status = request.args.get("status", "")
    prioridade = request.args.get("prioridade", "")
    responsavel_id = request.args.get("responsavel_id", "")
    organizacao_id = session["organizacao_id"]

    chamados = listar_chamados_admin(
        status,
        prioridade,
        responsavel_id,
        organizacao_id
    )

    administradores = listar_suportes(
        organizacao_id
    )

    return render_template(
        "admin.html",
        chamados=chamados,
        status=status,
        prioridade=prioridade,
        responsavel_id=responsavel_id,
        administradores=administradores
    )

@admin.route("/admin/usuarios")
@admin_required
def usuarios_admin():

    usuarios = listar_usuarios(
        session["organizacao_id"]
    )

    return render_template(
        "usuarios_admin.html",
        usuarios=usuarios,
        page_title="Usuários - Nortia",
        page_heading="Usuários",
        page_subtitle="Gerencie acessos internos da organização"
    )


@admin.route("/usuarios")
@admin_required
def usuarios_alias():
    return redirect("/admin/usuarios")


@admin.route(
    "/admin/usuarios/criar",
    methods=["POST"]
)
@admin_required
def criar_usuario_admin():

    nome = request.form["nome"].strip()
    email = request.form["email"].strip()
    senha = request.form["senha"]
    tipo = request.form["tipo"]

    tipos_permitidos = [
        "cliente",
        "suporte",
        "admin"
    ]

    if not nome or not email or not senha:

        flash(
            "Preencha nome, email e senha para criar o acesso.",
            "warning"
        )

        return redirect("/admin/usuarios")

    if len(senha) < 8:

        flash(
            "A senha temporária deve ter pelo menos 8 caracteres.",
            "warning"
        )

        return redirect("/admin/usuarios")

    if tipo not in tipos_permitidos:

        flash(
            "Tipo de usuário inválido.",
            "danger"
        )

        return redirect("/admin/usuarios")

    try:

        criar_usuario(
            nome,
            email.lower(),
            ph.hash(senha),
            tipo,
            session["organizacao_id"]
        )

        flash(
            "Acesso interno criado com sucesso.",
            "success"
        )

    except IntegrityError:

        flash(
            "Este email já está cadastrado.",
            "danger"
        )

    return redirect("/admin/usuarios")


@admin.route(
    "/admin/usuarios/<int:usuario_id>/tipo",
    methods=["POST"]
)
@admin_required
def alterar_tipo_usuario(usuario_id):

    novo_tipo = request.form["tipo"]

    tipos_permitidos = [
    "cliente",
    "suporte",
    "admin"
    ]

    if novo_tipo not in tipos_permitidos:

        flash(
            "Tipo de usuário inválido.",
            "danger"
        )

        return redirect("/admin/usuarios")

    if usuario_id == session["usuario_id"]:

        flash(
            "Você não pode alterar o tipo da própria conta.",
            "warning"
        )

        return redirect("/admin/usuarios")

    atualizar_tipo_usuario(
        usuario_id,
        novo_tipo,
        session["organizacao_id"]
    )

    flash(
        "Tipo de usuário atualizado com sucesso.",
        "success"
    )

    return redirect("/admin/usuarios")

@admin.route(
    "/admin/chamado/<int:chamado_id>/responsavel",
    methods=["POST"]
)
@equipe_required
def alterar_responsavel_chamado(chamado_id):

    responsavel_id = request.form["responsavel_id"]

    if not responsavel_id:

        flash(
            "Selecione um responsável.",
            "warning"
        )

        return redirect("/admin")

    suportes = listar_suportes(
        session["organizacao_id"]
    )

    suporte_ids = [
        str(suporte["id"])
        for suporte in suportes
    ]

    if responsavel_id not in suporte_ids:

        flash(
            "Selecione um usuário de suporte para assumir o atendimento.",
            "danger"
        )

        return redirect("/admin")

    atribuir_responsavel_chamado(
        chamado_id,
        responsavel_id,
        session["organizacao_id"]
    )

    data_atualizacao = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    registrar_historico(
        chamado_id,
        session["usuario_id"],
        "Responsável atribuído ao chamado",
        data_atualizacao
    )

    flash(
        "Responsável atualizado com sucesso.",
        "success"
    )

    return redirect("/admin")

@admin.route("/admin/meus-atendimentos")
@suporte_required
def meus_atendimentos():

    status = request.args.get("status", "")

    prioridade = request.args.get("prioridade", "")

    chamados = listar_chamados_responsavel(
        session["usuario_id"],
        status,
        prioridade,
        session["organizacao_id"]
    )

    administradores = listar_suportes(
        session["organizacao_id"]
    )

    return render_template(
    "admin.html",
    chamados=chamados,
    status=status,
    prioridade=prioridade,
    responsavel_id="",
    administradores=administradores
)

@admin.route(
    "/admin/chamado/<int:chamado_id>/assumir",
    methods=["POST"]
)
@suporte_required
def assumir_chamado(chamado_id):

    chamado = buscar_chamado(
        chamado_id,
        session["organizacao_id"]
    )

    if not chamado:

        flash(
            "Chamado não encontrado.",
            "danger"
        )

        return redirect("/admin")

    atribuir_responsavel_chamado(
        chamado_id,
        session["usuario_id"],
        session["organizacao_id"]
    )

    data_atualizacao = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    registrar_historico(
        chamado_id,
        session["usuario_id"],
        "Atendimento assumido pelo suporte",
        data_atualizacao
    )

    if chamado["status"] in ["Aberto", "Em triagem pela IA", "Pronto para suporte"]:

        atualizar_chamado(
            chamado_id,
            chamado["resposta"],
            "Em andamento",
            session["organizacao_id"]
        )

        registrar_historico(
            chamado_id,
            session["usuario_id"],
            f"Status alterado de {chamado['status']} para Em andamento",
            data_atualizacao
        )

    flash(
        "Atendimento assumido com sucesso.",
        "success"
    )

    return redirect(
        f"/chamado/{chamado_id}"
    )
