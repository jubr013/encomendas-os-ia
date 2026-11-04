import os

import pytest
from dotenv import load_dotenv

from encomendas_os import banco

load_dotenv()
sem_banco = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("DATABASE_URL_POOLED")),
    reason="Requer as URLs do banco no .env; não roda no CI.",
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


@sem_banco
def test_so_a_url_pooled_aponta_para_o_pooler():
    assert "-pooler" in banco.obter_url()
    assert "-pooler" not in banco.obter_url(direta=True)


@sem_banco
@pytest.mark.parametrize("direta", [True, False])
def test_conexao_responde(direta):
    with banco.conectar(direta=direta) as conexao:
        assert conexao.execute("SELECT 1").fetchone() == (1,)
