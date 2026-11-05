# Banco e migrações: validação

**Data:** 2026-11-04
**Spec:** `.specs/features/banco-e-migracoes/spec.md`
**Faixa:** `main..feat/5-neon-pgvector` (`c72680b..8a5d4cd`)
**Verificador:** subagente independente, segunda rodada; não escreveu este código.

**Resultado: PASS, com ressalvas menores.** Os 16 critérios têm citação e o build passa. Das 61 mutações, 57 morreram. Nenhuma das 4 sobreviventes aponta defeito de produção. As 13 lacunas da rodada anterior: 11 fechadas, 1 fechada em parte e 1 aberta, todas sem impacto no comportamento atual.

---

## Incidente da rodada anterior

- **O que houve:** uma sonda própria do verificador anterior gravou a linha `0001_x.sql` em `public.migracoes_aplicadas`, porque a fixture tinha `public` no `search_path`.
- **Correção no projeto:** a fixture agora usa só o esquema temporário (`tests/test_migracoes.py:28`), e um teste protege isso (`:376-380`).
- **Linha indevida:** não existe mais. A consulta final desta rodada mostra só as duas migrações reais.
- **Regras desta rodada:** sem sondas no banco; mutações só em cópia temporária; `banco.py` mutado só sem URLs; testes e fixtures sem alteração, conferidos por hash antes de cada execução.
- **Estado final do banco:** consulta única pela conexão normal, com `transaction_read_only = on`.
  - `public.migracoes_aplicadas`: `0001_habilitar_pgvector.sql` e `0002_documentos_e_trechos.sql`
  - `public.documentos`: 0 linhas
  - `public.trechos`: 0 linhas
  - Esquemas `teste_%`: 0

---

## Conclusão das tarefas

| Tarefa | Status | Notas |
|---|---|---|
| T1 | Feita | `tasks.md:42` marcada. |
| T2 | Feita | `tasks.md:52` marcada. |
| T3 | Feita | `tasks.md:62` marcada. |
| T4 | Feita, com evidência parcial | `tasks.md:72` marcada. A consulta final confirma as duas migrações. A segunda execução real não foi repetida, pois as regras proíbem rodar o comando. |
| F1 | Feita | `tasks.md:81` marcada. |

---

## Critérios ancorados na spec

Arquivos: `tests/test_banco.py` e `tests/test_migracoes.py`.

| Critério | Resultado definido na spec | `arquivo:linha` e asserção | Resultado |
|---|---|---|---|
| CON-01 | Conexão direta usa `DATABASE_URL` | `test_banco.py:29`: `banco.obter_url(direta=direta) == "postgresql://exemplo"`; `:55`: `banco.conectar(direta=direta) == url` | PASS |
| CON-02 | Conexão normal usa `DATABASE_URL_POOLED` | `test_banco.py:29` e `:55`, parâmetro `direta=False` | PASS |
| CON-03 | `RuntimeError` citando a variável | `test_banco.py:36`: `pytest.raises(RuntimeError, match=rf"Defina {nome} no")` | PASS |
| CON-04 | `SELECT 1` devolve `(1,)` nas duas; só a pooled tem `-pooler` no host | `test_banco.py:68`: `fetchone() == (1,)`; `:60-61`: `"-pooler" in urlparse(...).hostname` e `not in` | PASS |
| CON-05 | URLs só no `.env` são lidas desse arquivo | `test_banco.py:46`: `banco.obter_url() == "postgresql://do-arquivo"` | **PASS com ressalva.** O teste troca `load_dotenv` por um dublê, sem arquivo real. Conferi à parte, com um `.env` fictício e sem conexão: as duas variáveis foram lidas. |
| MIG-01 | Aplica `.sql` em ordem de nome, registra e devolve a lista | `test_migracoes.py:105`: `aplicadas == ["0001_a.sql", "0002_b.sql"]`; `:106`: `nomes_registrados(...)` igual. A ordem é real: `b` referencia `a` (`:99`) | PASS |
| MIG-02 | Lista vazia, sem reaplicar nem duplicar | `test_migracoes.py:116`: `== []`; `:117`: `== ["0001_a.sql"]`; `:126`: só a nova | PASS |
| MIG-03 | Desfaz, não registra, para, mantém anteriores, cita o arquivo; vale no SQL, no registro, na leitura e no comando | SQL: `:138`, `:142-145`. Registro: `:155`, `:158-159`. Leitura: `:168`, `:171-173`. Comando: `:198`, `:201-202` | PASS |
| MIG-04 | Exatamente as colunas listadas | `test_migracoes.py:255`: `{linha[0] for linha in linhas} == colunas`; `:263`: só as três tabelas | PASS |
| MIG-05 | Repetir `origem` e `hash` viola unicidade | `test_migracoes.py:297-298`: `pytest.raises(UniqueViolation)`, com `titulo` e `conteudo` diferentes; `:307`: complemento | PASS |
| MIG-06 | Documento inexistente viola chave estrangeira | `test_migracoes.py:312`: `pytest.raises(ForeignKeyViolation)` | PASS |
| MIG-07 | Repetir `documento_id` e `ordem` viola unicidade | `test_migracoes.py:320-321`: `pytest.raises(UniqueViolation)`, com `conteudo` diferente; `:332`: complemento | PASS |
| MIG-08 | Apagar documento apaga seus trechos | `test_migracoes.py:345`: `linhas == [(mantido,)]` | PASS |
| MIG-09 | pgvector habilitado; `<=>` a partir de `[1,2,4]` devolve `[1,2,3]` | `test_migracoes.py:362`: `linha == ("perto",)`; `:367-370`: migração registrada; `:372`: `linha == (1,)` em `pg_extension` | **PASS com ressalva.** Não prova que 0001 cria a extensão, limite aceito em `spec.md:33` (M2). |
| MIG-10 | Conexão direta; imprime nomes ou a mensagem; sem URL no stdout nem no stderr | `test_migracoes.py:80`: `pedidos == [True]`; `:83`: `capturado.out == saida`; `:84`: `capturado.err == ""`; `:209-212`: `python -m` real em esquema temporário | **PASS com ressalva.** A ausência de URL só é testada no caminho de sucesso. |
| MIG-11 | Tipos aprovados; nenhuma coluna aceita nulo | `test_migracoes.py:277-290`: `tipos == {...}`; `:291`: `{nulo for *_, nulo in linhas} == {"NO"}` | PASS |

**Status:** 16 de 16 com citação. 13 PASS e 3 PASS com ressalva. Sem lacuna de precisão aberta nos critérios; a spec não define o caso de variável vazia em CON-03 (B7).

---

## Lacunas da rodada anterior

| # | Lacuna | Situação | Evidência |
|---|---|---|---|
| 1 | Autocommit do comando | Fechada | `test_migracoes.py:81`, `:201-202`; X2, C5 mortas |
| 2 | Transação ao redor da migração | Fechada | `test_migracoes.py:149-159`; X1 morta |
| 3 | MIG-09 não prova a 0001 | Fechada em parte | `test_migracoes.py:367-372`; M1 morta, M2 sobrevive, limite aceito em `spec.md:33` |
| 4 | `public` no `search_path` | Fechada | `test_migracoes.py:28`, `:185`, `:376-380`. A proposta de conferir que a fixture não está na pooled não entrou (ver gap 1 abaixo). |
| 5 | Falha de leitura não cita o arquivo | Fechada | `migracoes.py:36`, `:40`; `test_migracoes.py:168`, `:171`; L1, L2 mortas |
| 6 | `conectar` ignora `direta` | Fechada | `test_banco.py:49-55`; B1, B2 mortas |
| 7 | Unicidade não varia outras colunas | Fechada | `test_migracoes.py:298`, `:321`; U1, U2, U6 mortas |
| 8 | `python -m` sem teste | Fechada | `test_migracoes.py:205-212`; P1 morta |
| 9 | Executor pode ler não `.sql` | Fechada | `test_migracoes.py:101`, `:105`; S2 morta |
| 10 | Stderr sem verificação | Fechada | `test_migracoes.py:84`; C1 morta |
| 11 | Leitura do `.env` sem teste | Fechada | `spec.md:48`; `test_banco.py:40-46`; B3, B4 mortas |
| 12 | `-pooler` conferido na URL | Fechada | `test_banco.py:60-61` usa `hostname` |
| 13 | Ordem depende do NTFS | **Aberta** | `test_migracoes.py:87-94`; O2 sobrevive |

**Lacunas de precisão da spec:** todas fechadas. Métrica em `spec.md:70`; stderr em `:77`; leitura em `:56`; tipos e nulos em `:71`; `.env` em `:48`; contagem de 16 requisitos em `:98` (5 de CON e 11 de MIG, confere); objetivos marcados em `:9-11`.

---

## Sensor de discriminação

**Profundidade:** P0, integridade de dados, com 61 mutações manuais.

**Controles:** em toda execução, o executor confirmou que `encomendas_os.__file__` vinha da cópia e abortaria se testes ou fixtures diferissem da árvore real. Sem mutação, a cópia deu 78 aprovados e 0 pulados com banco, e 52 aprovados e 26 pulados sem banco.

**Modo:** "banco" usa a suíte inteira, em esquema temporário. "sem URLs" usa só os testes sem banco, por segurança.

| ID | Local | Mutação | Modo | Resultado |
|---|---|---|---|---|
| O1 | `migracoes.py:13` | Ordem invertida | banco | Morta (6) |
| O2 | `migracoes.py:13` | Sem ordenar | banco | **Sobreviveu.** Quase equivalente neste Windows. |
| R1 | `migracoes.py:37` | Não registra em `migracoes_aplicadas` | banco | Morta (8) |
| R2 | `migracoes.py:38` | Registra sem a extensão | banco | Morta (7) |
| R3 | `migracoes.py:31` | Não pula as já aplicadas | banco | Morta (2) |
| R4 | `migracoes.py:43` | Devolve lista vazia | banco | Morta (3) |
| X1 | `migracoes.py:35` | Sem a transação | banco | Morta (1) |
| X2 | `migracoes.py:50` | Comando sem autocommit | banco | Morta (3) |
| C5 | `migracoes.py:50` | Comando sem autocommit | sem URLs | Morta (2) |
| L1 | `migracoes.py:36` | Leitura do arquivo fora do `try` | banco | Morta (1) |
| L2 | `migracoes.py:40` | Sem `UnicodeDecodeError` | banco | Morta (1) |
| L3 | `migracoes.py:40` | Sem `OSError` | banco | **Sobreviveu.** Equivalente para a spec. |
| L4 | `migracoes.py:40` | Sem `psycopg.Error` | banco | Morta (3) |
| E1 | `migracoes.py:41` | Erro sem o nome | banco | Morta (4) |
| E2 | `migracoes.py:41` | Segue depois da falha | banco | Morta (4) |
| P1 | `migracoes.py:59` | `python -m` não chama `main()` | banco | Morta (1) |
| S1 | `migracoes.py:13` | `listar_migracoes` sem filtro `.sql` | banco | Morta (2) |
| S2 | `migracoes.py:30` | Executor lê a pasta inteira | banco | Morta (1) |
| C1 | `migracoes.py:52` | Marcador de URL fictício no stderr | sem URLs | Morta (2) |
| C2 | `migracoes.py:52` | Marcador de URL fictício no stdout | sem URLs | Morta (2) |
| C3 | `migracoes.py:48` | Comando usa a pooled | sem URLs | Morta (2) |
| C4 | `migracoes.py:55` | Mensagem errada sem pendências | sem URLs | Morta (1) |
| B1 | `banco.py:20` | `conectar` sempre na pooled | sem URLs | Morta (1) |
| B2 | `banco.py:20` | `conectar` sempre na direta | sem URLs | Morta (1) |
| B3 | `banco.py:11` | Sem `load_dotenv` | sem URLs | Morta (1) |
| B4 | `banco.py:11` | `load_dotenv` depois de ler a variável | sem URLs | Morta (1) |
| B5 | `banco.py:12` | Variáveis trocadas | sem URLs | Morta (7) |
| B6 | `banco.py:15` | Erro sem o nome da variável | sem URLs | Morta (2) |
| B7 | `banco.py:14` | `if url is None`: variável vazia passa | sem URLs | **Sobreviveu.** Lacuna menor. |
| M1 | `0001` | Remove o arquivo | banco | Morta (2) |
| M2 | `0001:1` | Troca por `SELECT 1` | banco | **Sobreviveu.** Limite aceito em `spec.md:33`. |
| U1, U2 | `0002:8` | Chave com `titulo` ou com `conteudo`, mais fraca | banco | Mortas (1 cada) |
| U3, U4 | `0002:8` | Só `origem` ou só `hash`, mais forte | banco | Mortas (1 e 3) |
| U5 | `0002:8` | Sem unicidade | banco | Morta (1) |
| U6 | `0002:16` | Chave com `conteudo`, mais fraca | banco | Morta (1) |
| U7, U8 | `0002:16` | Só `ordem` ou só `documento_id`, mais forte | banco | Mortas (2 e 1) |
| U9 | `0002:16` | Sem unicidade | banco | Morta (1) |
| F1 | `0002:13` | Sem cascata | banco | Morta (1) |
| F2 | `0002:13` | Sem chave estrangeira | banco | Morta (2) |
| T1 a T7 | `0002` | Tipos: 2 ids `integer`, `documento_id integer`, `ordem bigint`, `criado_em` sem fuso, `origem` e `hash` `varchar` | banco | 7 mortas |
| T8, T9 | `migracoes.py:21-22` | `aplicada_em` sem fuso, `nome` `varchar` | banco | 2 mortas |
| N1 a N7 | `0002` | Sem `NOT NULL` em `hash`, `origem`, `titulo`, `criado_em`, `documento_id`, `ordem`, `trechos.conteudo` | banco | 7 mortas |
| N8 | `migracoes.py:22` | `aplicada_em` aceita nulo | banco | Morta |
| Q1, Q2 | `0002` | Coluna a mais, tabela a mais | banco | 2 mortas |

**Resultado:** 57 de 61 mortas. As tipagens e os nulos morreram por `test_colunas_tem_os_tipos_aprovados_e_sao_obrigatorias`.

**Não medidas, por regra de segurança:**

- B1 a B7 e C3 não rodaram com a suíte de banco. Todas têm resultado nos testes sem banco, inclusive as pedidas (`conectar` e `load_dotenv`), então nenhuma mutação pedida ficou sem medição. A sobrevivência de B7 na suíte com banco é dedução: os testes de banco sempre têm URL preenchida.
- A fixture e o `SET search_path` não foram mutados.

### Por que as sobreviventes não reprovam

- **O2:** o NTFS já devolve os nomes em ordem, então o Windows não distingue. A ordenação existe no código, e no Linux do CI o teste `:87-94` tende a pegar a falha, sem garantia.
- **L3:** sem o `OSError`, a falha ainda para o laço, não registra nada e mantém as anteriores. A exceção do Python já traz o caminho do arquivo. A rodada anterior mediu isso com pasta chamada `.sql` (S3), e aqui não refiz. Muda só o tipo do erro, que a spec não fixa.
- **B7:** a spec diz "faltar", sem definir variável vazia. O código trata vazia como faltando, o que é o certo, mas nenhum teste protege. O caso é plausível, porque `.env.example` traz `DATABASE_URL=` vazia.
- **M2:** o banco já tem a extensão, e `spec.md:33` aceita esse limite como suposição ainda não confirmada.

---

## UAT interativo

Não se aplica. A entrega é de backend.

---

## Qualidade do código

| Princípio | Status |
|---|---|
| Código mínimo | OK |
| Mudanças cirúrgicas | OK. Os 12 arquivos do diff batem com as tarefas. |
| Sem escopo extra | OK |
| Segue os padrões do repositório | OK |
| Valores asseridos batem com a spec | OK |
| Cobertura por camada | OK, com as ressalvas de CON-05 e MIG-10. |
| Todo teste liga a um requisito | OK. `test_conexao_de_teste_nao_alcanca_o_esquema_public` protege a suposição de isolamento (`spec.md:32`). |
| Orientações seguidas: `CLAUDE.md`, `pyproject.toml` | OK. Sem host do Neon nem senha no diff. As únicas URLs com outro valor são a fictícia `postgresql://do-arquivo`. `.env` segue ignorado pelo Git. |

**Observações, sem bloqueio:**

- **`PASTA_MIGRACOES` (`migracoes.py:9`)** só funciona em instalação editável, a forma usada pelo README e pelo CI.
- **Falha no meio do comando:** `main()` só imprime no fim (`migracoes.py:52-55`). As migrações já confirmadas não aparecem na saída. A spec não pede isso.
- **Banco sem a extensão (dedução, não medida):** com o `search_path` só no esquema temporário, 0001 criaria a extensão nesse esquema, e o `DROP SCHEMA ... CASCADE` a removeria. Os testes `public.vector` (`test_migracoes.py:351`) falhariam de forma visível. O banco atual não está nesse caso.
- **`tasks.md:38` e `:58`** não citam CON-05 e MIG-11. A rastreabilidade em `spec.md:93-95` cobre os dois.

---

## Casos de borda

- [x] **Arquivos que não são `.sql` são ignorados.** `test_migracoes.py:94` em `listar_migracoes`, e `:101` com `:105` no executor. S1 e S2 mortas.

---

## Verificação de build

- **Comando:** `ruff check . --no-cache` e `pytest -p no:cacheprovider -q --tb=short -rs -W default`, na pasta real e sem bytecode.
- **ruff:** saída 0. `All checks passed!`
- **pytest:** 78 aprovados, 0 falhas, 0 pulados, 1 aviso.
- **Aviso:** `RuntimeWarning` do `runpy` em `test_python_m_aplica_as_migracoes_do_projeto`, porque o módulo já está importado. É efeito de rodar pelo `runpy` dentro do pytest, e não afeta o resultado.
- **Testes antes da feature:** 42 (`main`, coletados de uma extração em pasta temporária).
- **Testes depois:** 78.
- **Diferença:** +36.
- **Simulação do CI, sem URLs, na cópia:** 52 aprovados, 26 pulados, 0 falhas; ruff sem erros. Todos os pulos têm o motivo esperado (`spec.md:22`). A simulação rodou no Windows, não no Linux do CI.
- **Árvore real:** `git status` igual antes e depois do build. As pastas não versionadas `.claude/`, `.mcp.json` e `skills-lock.json` já existiam. Este relatório é o único arquivo alterado, sem commit.

**Não verificado nesta rodada:**

- A segunda execução real do comando.
- O vazamento de URL em erro de conexão, por exigir uma sonda. `banco.py` não mudou desde a rodada anterior, que mediu ausência de vazamento com URL falsa (S1).
- O CI real no GitHub.

---

## Planos de correção

Nada foi corrigido. Todos os itens são opcionais e nenhum bloqueia o card.

| # | Gravidade | Lacuna | Evidência | Correção proposta |
|---|---|---|---|---|
| 1 | Menor, preventiva | A fixture não confere o isolamento antes de entregar a conexão. Só um teste à parte confere, e ele não impede os outros de rodar antes. | `test_migracoes.py:24-29`, `:376-380` | Afirmar na própria fixture que `current_schema()` é o esquema temporário e que o `-pooler` não está no host. |
| 2 | Menor | Variável vazia sem teste | `banco.py:14`, `test_banco.py:35-37`, B7 | Parametrizar o teste de CON-03 com a variável definida como `""`, e definir o caso na spec. |
| 3 | Menor | URL em erro só é coberta no caminho de sucesso | `test_migracoes.py:84`, `banco.py:20` | Testar `main()` com `psycopg.connect` falhando e afirmar que a URL não aparece no erro. Não toca no banco. |
| 4 | Menor | CON-05 sem arquivo real | `test_banco.py:41-46` | Usar um `.env` em `tmp_path`, passando pelo `load_dotenv` real. |
| 5 | Menor | Ordem depende do sistema de arquivos | `migracoes.py:13`, `test_migracoes.py:87-94`, O2 | Trocar `glob` por um dublê que devolve fora de ordem. |
| 6 | Menor | Ramo de `OSError` sem teste | `migracoes.py:40`, L3 | Usar uma pasta chamada `0001_x.sql` e afirmar `RuntimeError` com o nome. |
| 7 | Decisão de Julia | Suposição da extensão segue sem confirmação | `spec.md:33`, M2 | Confirmar a suposição, ou provar 0001 em banco descartável. |
| 8 | Cosmético | Requisitos ausentes nas tarefas | `tasks.md:38`, `:58` | Incluir CON-05 e MIG-11. |

### Lições sugeridas

Não rodei `scripts/lessons.py`.

1. Mutação em código de conexão pode desviar o teste de banco; rode essas mutações sem URLs, e faça a fixture conferir o isolamento antes de entregar a conexão.
2. Teste com dublê de leitor de arquivo prova que a chamada existe, não que o arquivo é lido.
3. Mutação sobrevivente pode ser equivalente para a spec; compare o resultado definido antes de abrir correção.
4. Verificação com variável de ambiente deve cobrir ausente e vazia, quando o modelo de `.env` traz chaves vazias.

---

## Rastreabilidade proposta

Não alterei `spec.md`.

| Requisito | Status anterior | Novo status |
|---|---|---|
| CON-01 a CON-05 | Implementado | Verificado |
| MIG-01 a MIG-11 | Implementado | Verificado |

---

## Resumo

**Geral:** pronto, com ressalvas menores.

**Critérios:** 16 de 16 com citação; 13 PASS, 3 PASS com ressalva.
**Sensor:** 57 de 61 mortas; 4 sobreviventes explicadas; nenhuma mutação pedida ficou sem medição.
**Build:** 78 aprovados, 0 falhas, 0 pulados, 1 aviso; ruff sem erros. CI simulado: 52 aprovados, 26 pulados.

**O que funciona:** conexão, executor, transação, autocommit, leitura com falha, `python -m`, esquema, tipos, restrições e isolamento dos testes.

**Próximos passos:** Julia decide sobre as melhorias opcionais e a suposição de `spec.md:33`, e depois sobre commit, push e PR.

## Complemento depois da segunda rodada

Esta seção foi escrita pelo autor do código, não pelo verificador independente. Nenhuma nova rodada do verificador foi feita depois dela.

Julia decidiu provar a migração do pgvector do zero. O teste `test_migracao_habilita_o_pgvector_em_um_banco_que_nao_o_tem` cria um banco temporário, confirma que a extensão está ausente, aplica as migrações, confirma que ela passou a existir e apaga o banco ao final.

- **Mutação M2 (0001 trocada por `SELECT 1`):** agora é detectada, em cópia temporária.
- **Verificação:** 79 testes passaram, e o `ruff` não apontou nada.
- **Banco real:** segue com as 2 migrações, sem documentos, e sem bancos ou esquemas de teste.
- **Suposições da spec:** confirmadas por Julia.
- **Lacunas menores restantes:** ficam para um card próprio, por decisão de Julia.
