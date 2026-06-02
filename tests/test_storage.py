from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage


def test_storage_local_salva_anexo_em_pasta_configurada(tmp_path, monkeypatch):
    import services.storage as storage

    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path)

    arquivo = FileStorage(
        stream=BytesIO(b"conteudo do anexo"),
        filename="../../documento.pdf",
    )

    anexo = storage.salvar_arquivo_chamado(
        arquivo,
        chamado_id=7,
    )

    caminho = Path(anexo["caminho_arquivo"])

    assert anexo["nome_arquivo"] == "documento.pdf"
    assert caminho.name.startswith("7_")
    assert caminho.name.endswith("_documento.pdf")
    assert caminho.exists()
    assert caminho.read_bytes() == b"conteudo do anexo"
    assert storage.arquivo_remoto(anexo["caminho_arquivo"]) is False
    assert storage.arquivo_remoto("https://exemplo.com/anexo.pdf") is True


def test_storage_rejeita_extensao_invalida(tmp_path, monkeypatch):
    import pytest
    import services.storage as storage

    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path)

    arquivo = FileStorage(
        stream=BytesIO(b"conteudo"),
        filename="script.exe",
        content_type="application/octet-stream",
    )

    with pytest.raises(storage.UploadInvalido):
        storage.salvar_arquivo_chamado(
            arquivo,
            chamado_id=7,
        )
