# Encomendas OS: gestão do projeto

**Data:** 04/11/2026
**Status:** publicado no GitHub; os cards da Sprint 2 serão criados ao fim da Sprint 1

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

## 3. Primeiros cards (rascunho)

### Sprint 1: fundação

| Card | Pronto quando |
|---|---|
| Criar repositório, README e `.gitignore` | `.env` ignorado; README explica o projeto e como rodar |
| Criar Project, milestones e labels | Quadro acessível, com estes cards |
| Configurar Python 3.12 e dependências | Instalação documentada funciona em ambiente limpo |
| Configurar CI | Lint e testes rodam em cada PR |
| Conectar ao Neon e habilitar pgvector | Migração cria as tabelas; teste de conexão passa |
| Criar dados fictícios | Cardápio, preços, políticas e pedidos de uma confeitaria inventada |

### Sprint 2: passos 1 e 2 do RAG

| Card | Pronto quando |
|---|---|
| Criar interface de provedores com Gemini | Embeddings e texto funcionam atrás da interface; chave lida do `.env` |
| Indexar os documentos | Documentos divididos, com embeddings gravados no pgvector |
| Implementar busca por similaridade em CLI | Pergunta retorna os trechos mais próximos |
| Criar conjunto de referência da busca | Perguntas com trechos corretos marcados |
| Medir recall@k e MRR | Comando gera o relatório e os valores de referência são registrados |
| Escrever a primeira anotação de aprendizado | `docs/aprendizados/` explica conceito, decisão e resultado |

Os cards serão detalhados ao serem criados, com a skill `criar-item-de-trabalho`.

## 4. O que fica fora do repositório

- **Análise de mercado:** mantida apenas localmente.
- **Segredos:** `.env` fora do Git desde o primeiro commit; `.env.example` lista os nomes das variáveis, sem valores.
