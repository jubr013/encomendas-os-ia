import os
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

from encomendas_os import banco

load_dotenv()
sem_banco = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("DATABASE_URL_POOLED")),
    reason="Requer as URLs do banco no .env.",
)
so_no_neon = pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="O CI usa um PostgreSQL no Docker Compose, sem o pooler do Neon.",
)


@pytest.fixture
def ambiente_vazio(monkeypatch):
    monkeypatch.setattr(banco, "load_dotenv", lambda: None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_POOLED", raising=False)
    return monkeypatch


@pytest.mark.parametrize(
    ("direta", "nome"), [(True, "DATABASE_URL"), (False, "DATABASE_URL_POOLED")]
)
def test_obter_url_escolhe_a_variavel_certa(ambiente_vazio, direta, nome):
    ambiente_vazio.setenv(nome, "postgresql://exemplo")
    assert banco.obter_url(direta=direta) == "postgresql://exemplo"


@pytest.mark.parametrize(
    ("direta", "nome"), [(True, "DATABASE_URL"), (False, "DATABASE_URL_POOLED")]
)
def test_obter_url_sem_variavel_cita_o_nome_que_falta(ambiente_vazio, direta, nome):
    with pytest.raises(RuntimeError, match=rf"Defina {nome} no"):
        banco.obter_url(direta=direta)


def test_obter_url_le_o_arquivo_env(ambiente_vazio):
    ambiente_vazio.setattr(
        banco,
        "load_dotenv",
        lambda: ambiente_vazio.setenv("DATABASE_URL_POOLED", "postgresql://do-arquivo"),
    )
    assert banco.obter_url() == "postgresql://do-arquivo"


@pytest.mark.parametrize(("direta", "url"), [(True, "url-direta"), (False, "url-pooled")])
def test_conectar_usa_a_url_pedida(ambiente_vazio, direta, url):
    ambiente_vazio.setenv("DATABASE_URL", "url-direta")
    ambiente_vazio.setenv("DATABASE_URL_POOLED", "url-pooled")
    ambiente_vazio.setattr(banco.psycopg, "connect", lambda url_recebida: url_recebida)

    assert banco.conectar(direta=direta) == url


@sem_banco
@so_no_neon
def test_so_a_url_pooled_aponta_para_o_pooler():
    assert "-pooler" in urlparse(banco.obter_url()).hostname
    assert "-pooler" not in urlparse(banco.obter_url(direta=True)).hostname


@sem_banco
@pytest.mark.parametrize("direta", [True, False])
def test_conexao_responde(direta):
    with banco.conectar(direta=direta) as conexao:
        assert conexao.execute("SELECT 1").fetchone() == (1,)
