"""Aplica as migrações SQL em ordem de nome, registrando o que já rodou."""

from pathlib import Path

import psycopg

from encomendas_os import banco

PASTA_MIGRACOES = Path(__file__).parents[2] / "migrations"


def listar_migracoes(pasta: Path = PASTA_MIGRACOES) -> list[Path]:
    return sorted(pasta.glob("*.sql"), key=lambda arquivo: arquivo.name)


def aplicar_migracoes(conexao: psycopg.Connection, pasta: Path = PASTA_MIGRACOES) -> list[str]:
    """Aplica as migrações pendentes e devolve os nomes das aplicadas."""
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS migracoes_aplicadas (
            nome text PRIMARY KEY,
            aplicada_em timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    linhas = conexao.execute("SELECT nome FROM migracoes_aplicadas").fetchall()
    ja_aplicadas = {linha[0] for linha in linhas}

    aplicadas = []
    for arquivo in listar_migracoes(pasta):
        if arquivo.name in ja_aplicadas:
            continue
        try:
            # A transação garante que a migração e seu registro entram juntos, ou nenhum dos dois.
            with conexao.transaction():
                conexao.execute(arquivo.read_text(encoding="utf-8"))
                conexao.execute(
                    "INSERT INTO migracoes_aplicadas (nome) VALUES (%s)", (arquivo.name,)
                )
        except psycopg.Error as erro:
            raise RuntimeError(f"Falha na migração {arquivo.name}.") from erro
        aplicadas.append(arquivo.name)
    return aplicadas


def main() -> None:
    # Migrações mudam o esquema, então usam a conexão direta.
    with banco.conectar(direta=True) as conexao:
        conexao.autocommit = True
        aplicadas = aplicar_migracoes(conexao)
    for nome in aplicadas:
        print(nome)
    if not aplicadas:
        print("Nenhuma migração pendente.")


if __name__ == "__main__":
    main()
