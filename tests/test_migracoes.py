import os
from uuid import uuid4

import psycopg
import pytest
from dotenv import load_dotenv

from encomendas_os import banco, migracoes

load_dotenv()
sem_banco = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Requer as URLs do banco no .env; não roda no CI.",
)


@pytest.fixture
def conexao_isolada():
    """Conexão em um esquema temporário, para os testes não tocarem nas tabelas reais."""
    esquema = f"teste_{uuid4().hex}"
    with banco.conectar(direta=True) as conexao:
        conexao.autocommit = True
        conexao.execute(f"CREATE SCHEMA {esquema}")
        conexao.execute(f"SET search_path TO {esquema}, public")
        yield conexao
        conexao.execute(f"DROP SCHEMA {esquema} CASCADE")


def tabela_existe(conexao, nome):
    linha = conexao.execute(
        """
        SELECT count(*) FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = %s
        """,
        (nome,),
    ).fetchone()
    return linha[0] == 1


def nomes_registrados(conexao):
    return [
        linha[0]
        for linha in conexao.execute(
            "SELECT nome FROM migracoes_aplicadas ORDER BY nome"
        ).fetchall()
    ]


def test_listar_migracoes_ordena_por_nome_e_ignora_o_que_nao_e_sql(tmp_path):
    (tmp_path / "0002_b.sql").write_text("SELECT 2", encoding="utf-8")
    (tmp_path / "0001_a.sql").write_text("SELECT 1", encoding="utf-8")
    (tmp_path / "anotacoes.txt").write_text("não é migração", encoding="utf-8")

    nomes = [arquivo.name for arquivo in migracoes.listar_migracoes(tmp_path)]

    assert nomes == ["0001_a.sql", "0002_b.sql"]


@sem_banco
def test_aplica_em_ordem_e_registra_cada_migracao(conexao_isolada, tmp_path):
    (tmp_path / "0002_b.sql").write_text("CREATE TABLE b (a_id int REFERENCES a)", encoding="utf-8")
    (tmp_path / "0001_a.sql").write_text("CREATE TABLE a (id int PRIMARY KEY)", encoding="utf-8")

    aplicadas = migracoes.aplicar_migracoes(conexao_isolada, tmp_path)

    assert aplicadas == ["0001_a.sql", "0002_b.sql"]
    assert nomes_registrados(conexao_isolada) == ["0001_a.sql", "0002_b.sql"]
    assert tabela_existe(conexao_isolada, "a")
    assert tabela_existe(conexao_isolada, "b")


@sem_banco
def test_segunda_execucao_nao_reaplica_nem_duplica(conexao_isolada, tmp_path):
    (tmp_path / "0001_a.sql").write_text("CREATE TABLE a (id int)", encoding="utf-8")
    migracoes.aplicar_migracoes(conexao_isolada, tmp_path)

    assert migracoes.aplicar_migracoes(conexao_isolada, tmp_path) == []
    assert nomes_registrados(conexao_isolada) == ["0001_a.sql"]


@sem_banco
def test_so_aplica_a_migracao_nova(conexao_isolada, tmp_path):
    (tmp_path / "0001_a.sql").write_text("CREATE TABLE a (id int)", encoding="utf-8")
    migracoes.aplicar_migracoes(conexao_isolada, tmp_path)
    (tmp_path / "0002_b.sql").write_text("CREATE TABLE b (id int)", encoding="utf-8")

    assert migracoes.aplicar_migracoes(conexao_isolada, tmp_path) == ["0002_b.sql"]


@sem_banco
def test_falha_desfaz_a_migracao_e_interrompe_as_seguintes(conexao_isolada, tmp_path):
    (tmp_path / "0001_boa.sql").write_text("CREATE TABLE boa (id int)", encoding="utf-8")
    (tmp_path / "0002_ruim.sql").write_text(
        "CREATE TABLE parcial (id int); SELECT coluna_inexistente FROM boa",
        encoding="utf-8",
    )
    (tmp_path / "0003_depois.sql").write_text("CREATE TABLE depois (id int)", encoding="utf-8")

    with pytest.raises(RuntimeError, match="0002_ruim.sql") as erro:
        migracoes.aplicar_migracoes(conexao_isolada, tmp_path)

    assert isinstance(erro.value.__cause__, psycopg.Error)
    assert tabela_existe(conexao_isolada, "boa")
    assert not tabela_existe(conexao_isolada, "parcial")
    assert not tabela_existe(conexao_isolada, "depois")
    assert nomes_registrados(conexao_isolada) == ["0001_boa.sql"]


@pytest.fixture
def esquema(conexao_isolada):
    migracoes.aplicar_migracoes(conexao_isolada)
    return conexao_isolada


def criar_documento(conexao, origem="cardapio.md", hash_="abc"):
    return conexao.execute(
        """
        INSERT INTO documentos (origem, titulo, conteudo, hash)
        VALUES (%s, 'Título', 'Conteúdo', %s) RETURNING id
        """,
        (origem, hash_),
    ).fetchone()[0]


def criar_trecho(conexao, documento_id, ordem=0):
    conexao.execute(
        "INSERT INTO trechos (documento_id, ordem, conteudo) VALUES (%s, %s, 'Trecho')",
        (documento_id, ordem),
    )


@sem_banco
@pytest.mark.parametrize(
    ("tabela", "colunas"),
    [
        ("migracoes_aplicadas", {"nome", "aplicada_em"}),
        ("documentos", {"id", "origem", "titulo", "conteudo", "hash", "criado_em"}),
        ("trechos", {"id", "documento_id", "ordem", "conteudo"}),
    ],
)
def test_tabela_tem_exatamente_as_colunas_aprovadas(esquema, tabela, colunas):
    linhas = esquema.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = %s
        """,
        (tabela,),
    ).fetchall()
    assert {linha[0] for linha in linhas} == colunas


@sem_banco
def test_esquema_tem_somente_as_tabelas_aprovadas(esquema):
    linhas = esquema.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()"
    ).fetchall()
    assert {linha[0] for linha in linhas} == {"migracoes_aplicadas", "documentos", "trechos"}


@sem_banco
def test_documento_repetido_na_mesma_origem_e_rejeitado(esquema):
    criar_documento(esquema)
    with pytest.raises(psycopg.errors.UniqueViolation):
        criar_documento(esquema)


@sem_banco
@pytest.mark.parametrize(
    ("origem", "hash_"), [("outra.md", "abc"), ("cardapio.md", "outro")]
)
def test_documento_diferente_em_origem_ou_hash_e_aceito(esquema, origem, hash_):
    primeiro = criar_documento(esquema)
    assert criar_documento(esquema, origem, hash_) != primeiro


@sem_banco
def test_trecho_de_documento_inexistente_e_rejeitado(esquema):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        criar_trecho(esquema, 999_999)


@sem_banco
def test_trecho_com_ordem_repetida_no_documento_e_rejeitado(esquema):
    documento_id = criar_documento(esquema)
    criar_trecho(esquema, documento_id)
    with pytest.raises(psycopg.errors.UniqueViolation):
        criar_trecho(esquema, documento_id)


@sem_banco
def test_apagar_documento_apaga_seus_trechos_e_preserva_os_outros(esquema):
    apagado = criar_documento(esquema)
    mantido = criar_documento(esquema, "outra.md")
    criar_trecho(esquema, apagado)
    criar_trecho(esquema, mantido)

    esquema.execute("DELETE FROM documentos WHERE id = %s", (apagado,))

    linhas = esquema.execute("SELECT documento_id FROM trechos").fetchall()
    assert linhas == [(mantido,)]


@sem_banco
def test_pgvector_encontra_o_vetor_mais_proximo(esquema):
    esquema.execute("CREATE TEMP TABLE vetores (nome text, vetor vector(3))")
    esquema.execute("INSERT INTO vetores VALUES ('perto', '[1,2,3]'), ('longe', '[9,9,9]')")

    linha = esquema.execute(
        "SELECT nome FROM vetores ORDER BY vetor <=> '[1,2,4]' LIMIT 1"
    ).fetchone()

    assert linha == ("perto",)
