import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

PASTA = Path(__file__).parent.parent / "data" / "confeitaria_ficticia"
LINHA_DE_PRECO = re.compile(r"^\| ([A-Z]{3}-[A-Z0-9]+) \|.*\| (\d+),(\d{2}) \|$", re.MULTILINE)
SABADO = 5
TERCA = 1
DADOS_PESSOAIS = {
    "e-mail": re.compile(r"\S+@\S+\.\S+"),
    "telefone": re.compile(r"\(?\b\d{2}\)?\s?\d{4,5}-\d{4}\b"),
    "CPF": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
}


def ler_jsonl(nome):
    linhas = (PASTA / nome).read_text(encoding="utf-8").splitlines()
    # Decimal evita erros de arredondamento de float ao somar dinheiro.
    return [json.loads(linha, parse_float=Decimal) for linha in linhas]


def calcular_total(precos, itens, entrega):
    return sum(precos[i["codigo"]] * Decimal(str(i["quantidade"])) for i in itens) + precos[entrega]


@pytest.fixture(scope="module")
def precos():
    texto = (PASTA / "tabela_precos.md").read_text(encoding="utf-8")
    return {c: Decimal(f"{r}.{d}") for c, r, d in LINHA_DE_PRECO.findall(texto)}


def test_tabela_de_precos_tem_todos_os_produtos(precos):
    assert len(precos) == 16


@pytest.mark.parametrize("pedido", ler_jsonl("pedidos_anteriores.jsonl"), ids=lambda p: p["id"])
def test_pedido_anterior_e_consistente(pedido, precos):
    assert calcular_total(precos, pedido["itens"], pedido["entrega"]) == pedido["total"]
    assert pedido["sinal"] == pedido["total"] / 2
    assert TERCA <= date.fromisoformat(pedido["data_entrega"]).weekday() <= SABADO


@pytest.mark.parametrize("conversa", ler_jsonl("conversas.jsonl"), ids=lambda c: c["id"])
def test_resultado_esperado_da_conversa_e_consistente(conversa, precos):
    esperado = conversa["esperado"]
    date.fromisoformat(conversa["data_referencia"])
    assert esperado["tipo"] in {"novo_pedido", "duvida", "cancelamento"}
    assert all(item["codigo"] in precos for item in esperado["itens"])

    if esperado["data_entrega"] is not None:
        assert TERCA <= date.fromisoformat(esperado["data_entrega"]).weekday() <= SABADO
    if esperado["total"] is None:
        return

    assert not esperado["faltando"]
    assert calcular_total(precos, esperado["itens"], esperado["entrega"]) == esperado["total"]


@pytest.mark.parametrize("nome", ["pedidos_anteriores.jsonl", "conversas.jsonl"])
def test_ids_sao_unicos(nome):
    ids = [registro["id"] for registro in ler_jsonl(nome)]
    assert len(ids) == len(set(ids))


def test_conversa_de_cancelamento_aponta_para_pedido_existente():
    pedidos = {p["id"] for p in ler_jsonl("pedidos_anteriores.jsonl")}
    esperados = [c["esperado"] for c in ler_jsonl("conversas.jsonl")]
    cancelamentos = [e for e in esperados if e["tipo"] == "cancelamento"]
    assert cancelamentos
    assert all(c["pedido_referencia"] in pedidos for c in cancelamentos)


@pytest.mark.parametrize("arquivo", sorted(PASTA.iterdir()), ids=lambda a: a.name)
@pytest.mark.parametrize("tipo", DADOS_PESSOAIS)
def test_nao_ha_dados_pessoais(arquivo, tipo):
    assert not DADOS_PESSOAIS[tipo].search(arquivo.read_text(encoding="utf-8"))
