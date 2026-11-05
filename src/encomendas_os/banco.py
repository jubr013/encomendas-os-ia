"""Conexão com o PostgreSQL no Neon."""

import os

import psycopg
from dotenv import load_dotenv


def obter_url(direta: bool = False) -> str:
    """Lê a URL do banco: direta para mudar o esquema, pooled para o uso normal."""
    load_dotenv()
    nome = "DATABASE_URL" if direta else "DATABASE_URL_POOLED"
    url = os.environ.get(nome)
    if not url:
        raise RuntimeError(f"Defina {nome} no arquivo .env.")
    return url


def conectar(direta: bool = False) -> psycopg.Connection:
    return psycopg.connect(obter_url(direta))
