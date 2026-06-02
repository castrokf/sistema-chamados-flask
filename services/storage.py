import os
import uuid
from pathlib import Path

from werkzeug.utils import secure_filename


UPLOAD_DIR = Path("uploads")
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_MB", "8")) * 1024 * 1024
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "pdf",
    "txt",
    "doc",
    "docx",
    "xls",
    "xlsx"
}
ALLOWED_MIME_TYPES = {
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "pdf": {"application/pdf"},
    "txt": {"text/plain"},
    "doc": {"application/msword", "application/octet-stream"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/octet-stream"},
    "xls": {"application/vnd.ms-excel", "application/octet-stream"},
    "xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream"}
}


class UploadInvalido(ValueError):
    pass


def usar_cloudinary():

    return bool(os.environ.get("CLOUDINARY_URL"))


def extensao_arquivo(nome_arquivo):
    if not nome_arquivo or "." not in nome_arquivo:
        return ""

    return nome_arquivo.rsplit(".", 1)[1].lower()


def validar_arquivo_chamado(arquivo):
    nome_seguro = secure_filename(arquivo.filename or "")
    extensao = extensao_arquivo(nome_seguro)

    if not nome_seguro or not extensao:
        raise UploadInvalido("Envie um arquivo com nome e extensão válidos.")

    if extensao not in ALLOWED_EXTENSIONS:
        raise UploadInvalido(
            "Formato não permitido. Envie PNG, JPG, PDF, TXT, DOC, DOCX, XLS ou XLSX."
        )

    content_type = (arquivo.content_type or "").split(";")[0].lower()
    tipos_permitidos = ALLOWED_MIME_TYPES.get(extensao, set())

    if content_type and content_type not in tipos_permitidos:
        raise UploadInvalido("O tipo do arquivo não corresponde à extensão informada.")

    posicao_atual = arquivo.stream.tell()
    arquivo.stream.seek(0, os.SEEK_END)
    tamanho = arquivo.stream.tell()
    arquivo.stream.seek(posicao_atual)

    if tamanho > MAX_UPLOAD_BYTES:
        raise UploadInvalido("Arquivo muito grande para envio.")

    return nome_seguro, extensao


def salvar_arquivo_chamado(arquivo, chamado_id):

    nome_seguro, extensao = validar_arquivo_chamado(arquivo)

    identificador = uuid.uuid4().hex
    nome_final = f"{chamado_id}_{identificador}_{Path(nome_seguro).stem}.{extensao}"

    if usar_cloudinary():
        import cloudinary.uploader

        resultado = cloudinary.uploader.upload(
            arquivo,
            resource_type="auto",
            folder=os.environ.get(
                "CLOUDINARY_FOLDER",
                "nortia-atendimentos"
            ),
            public_id=Path(nome_final).stem,
            use_filename=True,
            unique_filename=True
        )

        return {
            "nome_arquivo": nome_seguro,
            "caminho_arquivo": resultado["secure_url"]
        }

    UPLOAD_DIR.mkdir(
        exist_ok=True
    )

    caminho = (UPLOAD_DIR / nome_final).resolve()
    destino_base = UPLOAD_DIR.resolve()

    if destino_base not in caminho.parents:
        raise UploadInvalido("Caminho de arquivo inválido.")

    arquivo.save(caminho)

    return {
        "nome_arquivo": nome_seguro,
        "caminho_arquivo": str(caminho)
    }


def arquivo_remoto(caminho_arquivo):

    return caminho_arquivo.startswith(
        ("http://", "https://")
    )
