from datetime import datetime, timedelta


SLA_POR_PRIORIDADE = {
    "Crítica": {
        "primeira_resposta_horas": 1,
        "resolucao_horas": 4
    },
    "Urgente": {
        "primeira_resposta_horas": 1,
        "resolucao_horas": 8
    },
    "Alta": {
        "primeira_resposta_horas": 4,
        "resolucao_horas": 24
    },
    "Média": {
        "primeira_resposta_horas": 8,
        "resolucao_horas": 48
    },
    "Baixa": {
        "primeira_resposta_horas": 24,
        "resolucao_horas": 120
    }
}

STATUS_PAUSAM_SLA = {
    "Aguardando cliente",
    "Aguardando terceiro",
    "Aguardando aprovação"
}

STATUS_FINAIS = {
    "Resolvido",
    "Encerrado",
    "Fechado",
    "Cancelado"
}


def agora():
    return datetime.now()


def formatar_data(data):
    return data.strftime("%Y-%m-%d %H:%M:%S")


def calcular_prazos(prioridade, base=None):
    base = base or agora()
    regra = SLA_POR_PRIORIDADE.get(
        prioridade,
        SLA_POR_PRIORIDADE["Média"]
    )

    return {
        "prazo_primeira_resposta": formatar_data(
            base + timedelta(hours=regra["primeira_resposta_horas"])
        ),
        "prazo_resolucao": formatar_data(
            base + timedelta(hours=regra["resolucao_horas"])
        )
    }


def status_sla(prazo, concluido_em=None, status_chamado=None):
    if status_chamado in STATUS_PAUSAM_SLA:
        return "pausado"

    if concluido_em:
        return "cumprido"

    if not prazo:
        return "dentro_do_prazo"

    prazo_dt = datetime.strptime(prazo, "%Y-%m-%d %H:%M:%S")
    restante = prazo_dt - agora()

    if restante.total_seconds() < 0:
        return "violado"

    if restante <= timedelta(hours=2):
        return "em_risco"

    return "dentro_do_prazo"


def calcular_status_chamado(chamado):
    return {
        "sla_primeira_resposta_status": status_sla(
            chamado.get("prazo_primeira_resposta"),
            chamado.get("primeira_resposta_em"),
            chamado.get("status")
        ),
        "sla_resolucao_status": status_sla(
            chamado.get("prazo_resolucao") or chamado.get("data_limite"),
            chamado.get("resolvido_em") or chamado.get("fechado_em"),
            chamado.get("status")
        )
    }
