from re import sub

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session
)

from database import (
    criar_artigo_conhecimento,
    listar_artigos_conhecimento
)
from utils.decorators import equipe_required, login_required


knowledge = Blueprint("knowledge", __name__)


def slugificar(texto):
    slug = texto.strip().lower()
    slug = sub(r"[^a-z0-9áàâãéêíóôõúç]+", "-", slug)
    slug = sub(r"-+", "-", slug).strip("-")
    return slug or "artigo"


@knowledge.route("/central-ajuda")
@login_required
def central_ajuda():
    pesquisa = request.args.get("q", "").strip()
    incluir_internos = session.get("usuario_tipo") in ["admin", "suporte"]
    artigos = listar_artigos_conhecimento(
        session["organizacao_id"],
        pesquisa,
        incluir_internos
    )

    return render_template(
        "central_ajuda.html",
        artigos=artigos,
        pesquisa=pesquisa,
        page_title="Central de Ajuda - Nortia",
        page_heading="Central de Ajuda",
        page_subtitle="Base de conhecimento para orientar usuários e equipe de atendimento"
    )


@knowledge.route("/central-ajuda/novo", methods=["POST"])
@equipe_required
def criar_artigo():
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    category = request.form.get("category", "Geral").strip() or "Geral"
    visibility = request.form.get("visibility", "public")

    if visibility not in ["public", "internal"]:
        visibility = "public"

    if not title or not content:
        flash("Informe título e conteúdo para criar o artigo.", "warning")
        return redirect("/central-ajuda")

    criar_artigo_conhecimento(
        session["organizacao_id"],
        title,
        slugificar(title),
        content,
        category,
        visibility,
        session["usuario_id"]
    )

    flash("Artigo publicado na base de conhecimento.", "success")
    return redirect("/central-ajuda")
