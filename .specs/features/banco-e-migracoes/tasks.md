# Banco e migrações: tarefas

**Spec:** `.specs/features/banco-e-migracoes/spec.md`
**Design:** dispensado; o esquema foi aprovado e não há decisão de arquitetura em aberto.
**Status:** implementado, em verificação

## Matriz de cobertura

Orientações: `CLAUDE.md` e `pyproject.toml`.

| Camada | Teste | Expectativa | Local | Comando |
|---|---|---|---|---|
| Conexão | Unitário e integração | Todos os critérios de CON | `tests/test_banco.py` | `pytest` |
| Executor | Unitário e integração | Todos os critérios, em esquema temporário | `tests/test_migracoes.py` | `pytest` |
| Esquema SQL | Integração | Todos os critérios, em esquema temporário | `tests/test_migracoes.py` | `pytest` |

Os testes de integração são pulados quando não há URLs do banco, como no CI.

## Comandos de verificação

| Nível | Comando |
|---|---|
| Rápido e completo | `pytest` |
| Build | `ruff check .` e `pytest` |

## Ordem de execução

```
T1 → T2 → T3 → T4
```

## Tarefas

### T1: Conexão com o banco

- **Onde:** `src/encomendas_os/banco.py`, `tests/test_banco.py`, `pyproject.toml`, `.env.example`
- **Depende de:** nada
- **Requisitos:** CON-01 a CON-04
- **Testes:** unitário e integração
- **Verificação:** build
- **Commit:** `feat: adiciona conexão com o PostgreSQL`
- [x] Critérios CON cobertos e verificação passando

### T2: Executor de migrações

- **Onde:** `src/encomendas_os/migracoes.py`, `tests/test_migracoes.py`
- **Depende de:** T1
- **Requisitos:** MIG-01 a MIG-03
- **Testes:** unitário e integração
- **Verificação:** build
- **Commit:** `feat: adiciona executor de migrações`
- [x] Critérios cobertos e verificação passando

### T3: Migrações do esquema

- **Onde:** `migrations/0001_habilitar_pgvector.sql`, `migrations/0002_documentos_e_trechos.sql`, `tests/test_migracoes.py`
- **Depende de:** T2
- **Requisitos:** MIG-04 a MIG-09
- **Testes:** integração
- **Verificação:** build
- **Commit:** `feat: cria tabelas de documentos e trechos`
- [x] Critérios cobertos e verificação passando

### T4: Comando e aplicação no banco real

- **Onde:** `src/encomendas_os/migracoes.py`, `tests/test_migracoes.py`, `README.md`, `CLAUDE.md`
- **Depende de:** T3
- **Requisitos:** MIG-10
- **Testes:** integração
- **Verificação:** build, mais execução real duas vezes
- **Commit:** `feat: adiciona comando de migrações`
- [x] Comando aplicado no banco real, e a segunda execução não aplica nada
