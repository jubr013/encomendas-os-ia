import os
import runpy
from contextlib import contextmanager
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo

from encomendas_os import banco, migracoes

load_dotenv()
sem_banco = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Requer as URLs do banco no .env.",
)


@pytest.fixture
def conexao_isolada():
    """Conexão em um esquema temporário, para os testes não tocarem nas tabelas reais."""
    esquema = f"teste_{uuid4().hex}"
    with banco.conectar(direta=True) as conexao:
        conexao.autocommit = True
        conexao.execute(f"CREATE SCHEMA {esquema}")
        # Sem public no caminho: nenhuma consulta do teste alcança as tabelas reais.
        conexao.execute(f"SET search_path TO {esquema}")
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


@pytest.mark.parametrize(
    ("aplicadas", "saida"),
    [
        (["0001_a.sql", "0002_b.sql"], "0001_a.sql\n0002_b.sql\n"),
        ([], "Nenhuma migração pendente.\n"),
    ],
)
def test_comando_usa_conexao_direta_e_imprime_so_o_resultado(
    monkeypatch, capsys, aplicadas, saida
):
    pedidos = []
    autocommit_ao_aplicar = []

    @contextmanager
    def conectar_falso(direta=False):
        pedidos.append(direta)
        yield SimpleNamespace(autocommit=False)

    def aplicar_falso(conexao, pasta):
        autocommit_ao_aplicar.append(conexao.autocommit)
        return aplicadas

    monkeypatch.setattr(migracoes.banco, "conectar", conectar_falso)
    monkeypatch.setattr(migracoes, "aplicar_migracoes", aplicar_falso)

    migracoes.main()

    assert pedidos == [True]
    assert autocommit_ao_aplicar == [True]
    capturado = capsys.readouterr()
    assert capturado.out == saida
    assert capturado.err == ""


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
    (tmp_path / "anotacoes.txt").write_text("CREATE TABLE ignorada (id int)", encoding="utf-8")

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


@sem_banco
def test_falha_ao_registrar_desfaz_a_migracao(conexao_isolada, tmp_path):
    (tmp_path / "0001_ruim.sql").write_text(
        "CREATE TABLE parcial (id int); DROP TABLE migracoes_aplicadas",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="0001_ruim.sql"):
        migracoes.aplicar_migracoes(conexao_isolada, tmp_path)

    assert not tabela_existe(conexao_isolada, "parcial")
    assert tabela_existe(conexao_isolada, "migracoes_aplicadas")


@sem_banco
def test_arquivo_ilegivel_cita_o_nome_e_interrompe(conexao_isolada, tmp_path):
    (tmp_path / "0001_boa.sql").write_text("CREATE TABLE boa (id int)", encoding="utf-8")
    (tmp_path / "0002_ilegivel.sql").write_bytes(b"\xff\xfe")
    (tmp_path / "0003_depois.sql").write_text("CREATE TABLE depois (id int)", encoding="utf-8")

    with pytest.raises(RuntimeError, match="0002_ilegivel.sql") as erro:
        migracoes.aplicar_migracoes(conexao_isolada, tmp_path)

    assert isinstance(erro.value.__cause__, UnicodeDecodeError)
    assert not tabela_existe(conexao_isolada, "depois")
    assert nomes_registrados(conexao_isolada) == ["0001_boa.sql"]


@pytest.fixture
def comando_isolado(conexao_isolada, monkeypatch):
    """Faz o comando usar uma conexão real, como a de produção, no esquema temporário."""
    conectar_real = banco.conectar
    esquema_de_teste = conexao_isolada.execute("SELECT current_schema()").fetchone()[0]

    @contextmanager
    def conectar_no_esquema(direta=False):
        with conectar_real(direta=True) as conexao:
            conexao.execute(f"SET search_path TO {esquema_de_teste}")
            conexao.commit()
            yield conexao

    monkeypatch.setattr(banco, "conectar", conectar_no_esquema)
    return conexao_isolada


@sem_banco
def test_comando_preserva_as_anteriores_quando_uma_migracao_falha(comando_isolado, tmp_path):
    (tmp_path / "0001_boa.sql").write_text("CREATE TABLE boa (id int)", encoding="utf-8")
    (tmp_path / "0002_ruim.sql").write_text("SELECT coluna_inexistente FROM boa", encoding="utf-8")

    with pytest.raises(RuntimeError, match="0002_ruim.sql"):
        migracoes.main(tmp_path)

    assert tabela_existe(comando_isolado, "boa")
    assert nomes_registrados(comando_isolado) == ["0001_boa.sql"]


@sem_banco
def test_python_m_aplica_as_migracoes_do_projeto(comando_isolado, capsys):
    runpy.run_module("encomendas_os.migracoes", run_name="__main__")

    assert capsys.readouterr().out == (
        "0001_habilitar_pgvector.sql\n0002_documentos_e_trechos.sql\n"
    )
    assert tabela_existe(comando_isolado, "documentos")


@pytest.fixture
def esquema(conexao_isolada):
    migracoes.aplicar_migracoes(conexao_isolada)
    return conexao_isolada


def criar_documento(conexao, origem="cardapio.md", hash_="abc", titulo="Título", conteudo="Texto"):
    return conexao.execute(
        """
        INSERT INTO documentos (origem, titulo, conteudo, hash)
        VALUES (%s, %s, %s, %s) RETURNING id
        """,
        (origem, titulo, conteudo, hash_),
    ).fetchone()[0]


def criar_trecho(conexao, documento_id, ordem=0, conteudo="Trecho"):
    conexao.execute(
        "INSERT INTO trechos (documento_id, ordem, conteudo) VALUES (%s, %s, %s)",
        (documento_id, ordem, conteudo),
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
def test_colunas_tem_os_tipos_aprovados_e_sao_obrigatorias(esquema):
    linhas = esquema.execute(
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = current_schema()
        """
    ).fetchall()
    tipos = {(tabela, coluna): tipo for tabela, coluna, tipo, _ in linhas}

    assert tipos == {
        ("migracoes_aplicadas", "nome"): "text",
        ("migracoes_aplicadas", "aplicada_em"): "timestamp with time zone",
        ("documentos", "id"): "bigint",
        ("documentos", "origem"): "text",
        ("documentos", "titulo"): "text",
        ("documentos", "conteudo"): "text",
        ("documentos", "hash"): "text",
        ("documentos", "criado_em"): "timestamp with time zone",
        ("trechos", "id"): "bigint",
        ("trechos", "documento_id"): "bigint",
        ("trechos", "ordem"): "integer",
        ("trechos", "conteudo"): "text",
    }
    assert {nulo for *_, nulo in linhas} == {"NO"}


@sem_banco
def test_documento_repetido_na_mesma_origem_e_rejeitado(esquema):
    criar_documento(esquema)
    with pytest.raises(psycopg.errors.UniqueViolation):
        criar_documento(esquema, titulo="Outro título", conteudo="Outro texto")


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
        criar_trecho(esquema, documento_id, conteudo="Outro trecho")


@sem_banco
def test_trecho_com_outra_ordem_ou_de_outro_documento_e_aceito(esquema):
    documento_id = criar_documento(esquema)
    outro_documento_id = criar_documento(esquema, "outra.md")
    criar_trecho(esquema, documento_id)
    criar_trecho(esquema, documento_id, ordem=1)
    criar_trecho(esquema, outro_documento_id)

    assert esquema.execute("SELECT count(*) FROM trechos").fetchone() == (3,)


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
    # A extensão vale para o banco inteiro e fica em public, por isso os nomes qualificados.
    esquema.execute("CREATE TEMP TABLE vetores (nome text, vetor public.vector(3))")
    esquema.execute("INSERT INTO vetores VALUES ('perto', '[1,2,3]'), ('longe', '[9,9,9]')")

    linha = esquema.execute(
        """
        SELECT nome FROM vetores
        ORDER BY vetor OPERATOR(public.<=>) '[1,2,4]'::public.vector
        LIMIT 1
        """
    ).fetchone()

    assert linha == ("perto",)


@sem_banco
def test_migracao_do_pgvector_e_registrada_e_a_extensao_existe(esquema):
    assert nomes_registrados(esquema) == [
        "0001_habilitar_pgvector.sql",
        "0002_documentos_e_trechos.sql",
    ]
    linha = esquema.execute("SELECT count(*) FROM pg_extension WHERE extname = 'vector'").fetchone()
    assert linha == (1,)


@pytest.fixture
def banco_vazio():
    """Banco temporário: começa sem a extensão, o que prova a migração do zero."""
    nome = f"teste_{uuid4().hex}"
    url = banco.obter_url(direta=True)
    with psycopg.connect(url, autocommit=True) as administracao:
        administracao.execute(f"CREATE DATABASE {nome}")
        try:
            with psycopg.connect(make_conninfo(url, dbname=nome), autocommit=True) as conexao:
                yield conexao
        finally:
            administracao.execute(f"DROP DATABASE {nome} WITH (FORCE)")


@sem_banco
def test_migracao_habilita_o_pgvector_em_um_banco_que_nao_o_tem(banco_vazio):
    consulta = "SELECT count(*) FROM pg_extension WHERE extname = 'vector'"
    assert banco_vazio.execute(consulta).fetchone() == (0,)

    migracoes.aplicar_migracoes(banco_vazio)

    assert banco_vazio.execute(consulta).fetchone() == (1,)
    distancia = banco_vazio.execute("SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector").fetchone()[0]
    assert distancia == 0


@sem_banco
def test_conexao_de_teste_nao_alcanca_o_esquema_public(conexao_isolada):
    caminho = conexao_isolada.execute("SHOW search_path").fetchone()[0]
    assert "public" not in caminho
    with pytest.raises(psycopg.errors.UndefinedTable):
        conexao_isolada.execute("SELECT 1 FROM migracoes_aplicadas")
