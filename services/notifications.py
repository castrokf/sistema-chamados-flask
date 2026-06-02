import logging
import os

import requests


logger = logging.getLogger(__name__)


def enviar_webhook(titulo, mensagem, payload=None):
    webhook_url = os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        logger.info("WEBHOOK_URL não configurada; alerta ignorado: %s", titulo)
        return False

    dados = payload or {
        "text": f"{titulo}\n{mensagem}"
    }

    try:
        resposta = requests.post(
            webhook_url,
            json=dados,
            timeout=8
        )
        resposta.raise_for_status()
        return True
    except Exception as erro:
        logger.warning("Falha ao enviar webhook: %s", erro)
        return False
