# Banco e migrações: especificação

## Problema

O RAG da Sprint 2 precisa guardar documentos e trechos no PostgreSQL do Neon. O esquema precisa estar versionado como código, e não criado à mão, para ser reproduzível e para mostrar a mecânica sem framework.

## Objetivos

- [x] Conectar ao banco lendo as URLs do `.env`, sem expor segredos.
- [x] Aplicar migrações em SQL com um executor pequeno, sem Alembic.
- [x] Criar as tabelas `migracoes_aplicadas`, `documentos` e `trechos`, e habilitar o pgvector.

## Fora de escopo

| Item | Motivo |
|---|---|
| Coluna de embedding | O tamanho do vetor depende do modelo, escolhido na Sprint 2 |
| Tabelas de pedidos e clientes | Ficam para a Entrega 2; antes disso, o RAG lê os pedidos como documentos |
| Alembic ou outro framework | Decisão aprovada por Julia: começar sem framework |
| Desfazer migrações | Não há necessidade nesta etapa |
| `neon.ts`, `neon init` e `neon deploy` | As URLs já estão no `.env`, e o projeto é Python |
| Testes de banco no CI | O CI não tem acesso ao banco; esses testes rodam localmente |

## Suposições

| Decisão | Escolha | Motivo | Confirmada? |
|---|---|---|---|
| Esquema das tabelas | Campos de MIG-04 | Aprovado por Julia em 04/11/2026 | Sim |
| Chave de `documentos` | Única em `origem` + `hash` | Mesmo conteúdo da mesma origem não se repete; a versão nova de um arquivo entra como outro documento | Sim |
| Tipo dos ids | `bigint` gerado pelo banco | Padrão simples do PostgreSQL | Sim |
| Apagar documento | Apaga seus trechos em cascata | Trecho não existe sem documento | Sim |
| Isolamento dos testes | Esquema temporário removido ao final, sem `public` no `search_path` | Os testes não alcançam as tabelas reais | Não |
| Prova da extensão | Banco temporário, criado e apagado pelo teste, que começa sem a extensão | Decisão de Julia em 04/11/2026: provar a migração do zero | Sim |
| Concorrência | Sem trava entre execuções | Projeto de uma pessoa, com execução manual | Não |

**Perguntas abertas:** nenhuma.

## Histórias

### P1: Conexão

**Critérios:**

1. **CON-01:** QUANDO a conexão direta for pedida, ENTÃO o sistema DEVE usar `DATABASE_URL`.
2. **CON-02:** QUANDO a conexão normal for pedida, ENTÃO o sistema DEVE usar `DATABASE_URL_POOLED`.
3. **CON-03:** QUANDO a variável faltar, ENTÃO o sistema DEVE lançar `RuntimeError` citando o nome da variável.
4. **CON-04:** QUANDO as URLs estiverem configuradas, ENTÃO as duas conexões DEVEM executar `SELECT 1` e receber `(1,)`, e só a pooled DEVE ter `-pooler` no host.
5. **CON-05:** QUANDO as URLs estiverem só no arquivo `.env`, ENTÃO o sistema DEVE lê-las desse arquivo.

### P1: Executor de migrações

**Critérios:**

1. **MIG-01:** QUANDO houver migrações pendentes, ENTÃO o executor DEVE aplicar os arquivos `.sql` em ordem de nome, registrar cada nome em `migracoes_aplicadas` e devolver a lista dos aplicados nessa ordem.
2. **MIG-02:** QUANDO for executado de novo sem novidades, ENTÃO DEVE devolver lista vazia, sem reaplicar nem duplicar registros.
3. **MIG-03:** QUANDO uma migração falhar, inclusive na execução do SQL, no registro ou na leitura do arquivo, ENTÃO suas mudanças DEVEM ser desfeitas, ela não DEVE ser registrada, as seguintes não DEVEM rodar, as anteriores DEVEM permanecer e o erro DEVE citar o nome do arquivo. Isso vale também para o comando de MIG-10.

### P1: Esquema

**Critérios:**

1. **MIG-04:** QUANDO as migrações do projeto forem aplicadas, ENTÃO DEVEM existir exatamente estas colunas:
   - `migracoes_aplicadas`: `nome`, `aplicada_em`
   - `documentos`: `id`, `origem`, `titulo`, `conteudo`, `hash`, `criado_em`
   - `trechos`: `id`, `documento_id`, `ordem`, `conteudo`
2. **MIG-05:** QUANDO um documento repetir `origem` e `hash`, ENTÃO o banco DEVE rejeitar com violação de unicidade.
3. **MIG-06:** QUANDO um trecho citar documento inexistente, ENTÃO o banco DEVE rejeitar com violação de chave estrangeira.
4. **MIG-07:** QUANDO um trecho repetir `documento_id` e `ordem`, ENTÃO o banco DEVE rejeitar com violação de unicidade.
5. **MIG-08:** QUANDO um documento for apagado, ENTÃO seus trechos DEVEM ser apagados.
6. **MIG-09:** QUANDO as migrações forem aplicadas em um banco sem a extensão, ENTÃO o pgvector DEVE passar de ausente a habilitado, e uma busca por distância de cosseno (`<=>`) entre os vetores `[1,2,3]` e `[9,9,9]`, a partir de `[1,2,4]`, DEVE devolver o primeiro.
7. **MIG-11:** QUANDO as migrações forem aplicadas, ENTÃO os ids e `documento_id` DEVEM ser `bigint`, `ordem` DEVE ser `integer`, as datas DEVEM ser `timestamptz`, os demais campos DEVEM ser `text` e nenhuma coluna DEVE aceitar nulo.

### P1: Comando

**Critérios:**

1. **MIG-10:** QUANDO `python -m encomendas_os.migracoes` rodar, ENTÃO DEVE usar a conexão direta e imprimir o nome de cada migração aplicada, ou `Nenhuma migração pendente.`, sem imprimir a URL na saída padrão nem na de erro.

## Casos de borda

- QUANDO a pasta de migrações tiver arquivos que não são `.sql`, ENTÃO o executor DEVE ignorá-los (MIG-01).

## Dimensões implícitas

- **Falhas:** cobertas por CON-03 e MIG-03.
- **Repetição segura:** coberta por MIG-02.
- **Demais dimensões:** não se aplicam a este escopo.

## Rastreabilidade

| Requisito | Tarefa | Status |
|---|---|---|
| CON-01 a CON-05 | T1, F1 | Implementado |
| MIG-01 a MIG-03 | T2, F1 | Implementado |
| MIG-04 a MIG-09 e MIG-11 | T3, F1 | Implementado |
| MIG-10 | T4, F1 | Implementado |

**Cobertura:** 16 requisitos, 16 mapeados, nenhum sem tarefa.
