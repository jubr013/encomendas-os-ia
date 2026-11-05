# Encomendas OS: gestão do projeto

**Data:** 04/11/2026
**Status:** publicado no GitHub; Sprint 1 concluída e Sprint 2 em andamento

## 1. Ferramenta

**Recomendação: GitHub Projects em vez de Trello.** É gratuito, fica ao lado do código e liga cada card ao seu PR sem integração extra. Quem avaliar o portfólio também vê o processo de trabalho.

## 2. Como se organiza

| Conceito | No GitHub |
|---|---|
| Card | Issue, com critérios de aceite |
| Sprint | Campo de iteração do Project |
| Entrega da ementa | Milestone |
| Coluna | Campo de status: Backlog, A fazer, Em andamento, Em revisão, Concluído |
| Tipo e área | Labels: `feat`, `fix`, `docs`, `eval`, `rag`, `mcp`, `api`, `ui`, `infra` |
| Conclusão | PR que referencia a issue e a fecha ao ser integrado |

**Milestones:** Entrega 1 (RAG e agente em CLI), Entrega 2 (API e MCP), Entrega 3 (interface e implantação) e Defesa técnica.

**Sprints:** duração sugerida de 2 semanas, já que não há prazo do curso. Ao final de cada uma, uma revisão curta: o que foi entregue, o que passa para a próxima e o que foi aprendido.

## 3. Sprints e cards

O andamento de cada card fica no [quadro do projeto](https://github.com/users/jubr013/projects/1).

| Sprint | Período | Situação |
|---|---|---|
| Sprint 1 | 04/11/2026 (um dia no quadro) | Concluída |
| Sprint 2 | 05/11/2026 a 18/11/2026 | Em andamento |

### Cards da Sprint 2

| Card | Título |
|---|---|
| [#15](https://github.com/jubr013/encomendas-os-ia/issues/15) | Rodar os testes de banco no CI com Docker Compose |
| [#16](https://github.com/jubr013/encomendas-os-ia/issues/16) | Fechar as lacunas menores da verificação do banco |
| [#17](https://github.com/jubr013/encomendas-os-ia/issues/17) | Criar interface de provedores com Gemini |
| [#18](https://github.com/jubr013/encomendas-os-ia/issues/18) | Indexar os documentos da confeitaria no pgvector |
| [#19](https://github.com/jubr013/encomendas-os-ia/issues/19) | Buscar por similaridade em linha de comando |
| [#20](https://github.com/jubr013/encomendas-os-ia/issues/20) | Criar conjunto de referência da busca |
| [#21](https://github.com/jubr013/encomendas-os-ia/issues/21) | Medir recall@k e MRR da busca |
| [#22](https://github.com/jubr013/encomendas-os-ia/issues/22) | Atualizar documentos com a direção e a Sprint 2 |

## 4. O que fica fora do repositório

- **Análise de mercado:** mantida apenas localmente.
- **Segredos:** `.env` fora do Git desde o primeiro commit; `.env.example` lista os nomes das variáveis, sem valores.
