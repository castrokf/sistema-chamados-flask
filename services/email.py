import logging
import os
import smtplib
from email.message import EmailMessage


logger = logging.getLogger(__name__)


def smtp_configurado():
    obrigatorias = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_FROM"
    ]

    return all(os.environ.get(item) for item in obrigatorias)


def enviar_email(destinatario, assunto, corpo):
    if not smtp_configurado():
        logger.info(
            "SMTP não configurado; email não enviado para %s: %s",
            destinatario,
            assunto
        )
        return False

    mensagem = EmailMessage()
    mensagem["From"] = os.environ["SMTP_FROM"]
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(corpo)

    host = os.environ["SMTP_HOST"]
    porta = int(os.environ.get("SMTP_PORT", "587"))
    usuario = os.environ.get("SMTP_USER")
    senha = os.environ.get("SMTP_PASSWORD")
    usar_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    try:
        with smtplib.SMTP(host, porta, timeout=10) as smtp:
            if usar_tls:
                smtp.starttls()

            if usuario and senha:
                smtp.login(usuario, senha)

            smtp.send_message(mensagem)
    except Exception as erro:
        logger.warning("Falha ao enviar email para %s: %s", destinatario, erro)
        return False

    return True
