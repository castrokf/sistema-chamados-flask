import os
from pathlib import Path

from werkzeug.utils import secure_filename


UPLOAD_DIR = Path("uploads")


def usar_cloudinary():

    return bool(os.environ.get("CLOUDINARY_URL"))


def salvar_arquivo_chamado(arquivo, chamado_id):

    nome_seguro = secure_filename(
        arquivo.filename
    )

    nome_final = f"{chamado_id}_{nome_seguro}"

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

    caminho = UPLOAD_DIR / nome_final

    arquivo.save(caminho)

    return {
        "nome_arquivo": nome_seguro,
        "caminho_arquivo": str(caminho)
    }


def arquivo_remoto(caminho_arquivo):

    return caminho_arquivo.startswith(
        ("http://", "https://")
    )
