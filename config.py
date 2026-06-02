import os
from dataclasses import dataclass


def _env_bool(nome, padrao=False):
    valor = os.environ.get(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    env: str
    secret_key: str
    max_content_length: int
    session_cookie_secure: bool
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "Lax"

    @property
    def production(self):
        return self.env == "production"


def carregar_configuracao():
    env = os.environ.get("FLASK_ENV", "development").strip().lower()

    if os.environ.get("RENDER", "").lower() == "true":
        env = "production"

    secret_key = os.environ.get("FLASK_SECRET_KEY")

    if env == "production" and not secret_key:
        raise RuntimeError(
            "FLASK_SECRET_KEY precisa estar definida em produção. "
            "Configure a variável no ambiente do Render antes de iniciar a aplicação."
        )

    if not secret_key:
        secret_key = "dev-only-change-me"

    max_mb = int(os.environ.get("MAX_UPLOAD_MB", "8"))
    session_cookie_secure = _env_bool(
        "SESSION_COOKIE_SECURE",
        padrao=env == "production"
    )

    return AppConfig(
        env=env,
        secret_key=secret_key,
        max_content_length=max_mb * 1024 * 1024,
        session_cookie_secure=session_cookie_secure
    )
