from flask import (
    Blueprint,
    render_template,
    request
)

from database import listar_chamados_admin

from utils.decorators import admin_required


admin = Blueprint(
    "admin",
    __name__
)


@admin.route("/admin")
@admin_required
def painel_admin():

    status = request.args.get("status", "")

    prioridade = request.args.get("prioridade", "")

    chamados = listar_chamados_admin(
        status,
        prioridade
    )

    return render_template(
        "admin.html",
        chamados=chamados,
        status=status,
        prioridade=prioridade
    )
