# Encomendas OS: plano de acordo com a ementa

**Data:** 04/11/2026
**Fonte:** `Unipds.pdf`, "Ementa Engenharia de Software em IA Aplicada" (19 páginas)
**Status:** em execução; Sprint 1 concluída e Sprint 2 iniciada em 05/11/2026

## 1. Como a ementa se aplica

O projeto segue o **Módulo 11, Projeto Integrador (Capstone)**, que pede um Micro-SaaS com três entregas e uma defesa técnica. Os demais módulos entram como matéria aplicada em partes do produto.

**Vínculo:** estudo guiado por conta própria, definido por Julia em 04/11/2026. Não há avaliação nem prazo do curso; a ementa é roteiro, não exigência, e desvios não precisam de aprovação.

**Direção:** Organização com IA para confeitaria sob encomenda é o núcleo deste portfólio, por decisão de Julia em 05/11/2026, e isso não valida um produto comercial.

## 2. Roteiro pelas entregas do Capstone

| Etapa do Capstone | O que construir no Encomendas OS | Módulos de apoio | Pronto quando |
|---|---|---|---|
| **Unidade 1:** ideação e arquitetura | Problema, público, proposta de valor, arquitetura, backlog, marcos e decisões de stack | 1, 7, 8 (Unidade 1) | Documentos e backlog revisados por Julia |
| **Entrega 1:** RAG e agente em CLI (Python) | Base com cardápio, preços, políticas e pedidos anteriores fictícios; agente que lê uma conversa e propõe pedido e orçamento | 1, 2, 4 (Unidades 1 a 5), 8 (Unidade 4) | CLI funcionando e primeira avaliação com conjunto de referência |
| **Entrega 2:** API e MCP (Python) | API documentada, PostgreSQL com contratos e ferramentas FastMCP; aplicação com MCP habilitado | 3, 4 (Unidades 3, 6 e 7), 2 (RAG avançado) | Cliente MCP cria e consulta pedidos; testes de contrato passam |
| **Entrega 3:** interface e implantação | UI em React, TypeScript e Tailwind, mobile-first, com aprovação humana, CI/CD e implantação | 5, 6 (Unidade VIII), 3 (segurança), 10 | Solução no ar, com um agente interagindo pela interface via MCP |
| **Unidade 5:** defesa técnica | README, diagrama, demonstração e justificativa das decisões | 11, 12 | Apresentação ensaiada e documentação completa |

### O RAG precisa de uma função real

O Capstone coloca o RAG no centro, mas extrair um pedido de uma conversa não depende dele. Para que não fique artificial, ele deve responder ao que muda de negócio para negócio: **cardápio, tabela de preços, regras de sinal e prazo, e pedidos parecidos já feitos**.

Exemplo: uma cliente pede um bolo temático para 30 pessoas. O agente estrutura o pedido, busca os preços e casos semelhantes daquela confeitaria e propõe um orçamento, que só é enviado após aprovação humana.

### Stack e objetivo de aprendizado

Objetivo definido por Julia: fortalecer Python e RAG, sem abandonar React, TypeScript e Tailwind.

| Camada | Tecnologia | Papel para Julia |
|---|---|---|
| RAG, agente, avaliações, API e MCP | Python e FastMCP | **Foco de aprendizado** |
| Banco e busca vetorial | PostgreSQL, com pgvector a avaliar | **Foco de aprendizado** |
| Interface | React, TypeScript e Tailwind | Ponto forte; entrega rápida e demonstração |
| Ligação entre as camadas | Contrato OpenAPI da API, com tipos TypeScript gerados a partir dele (a avaliar) | Conecta o que é novo ao que já é familiar |

### Construir o RAG para aprender

Cada passo começa sem framework de RAG, para que a mecânica fique visível, e só avança quando a avaliação mostrar ganho:

1. **Busca básica:** dividir os documentos, gerar embeddings, gravar no Postgres e buscar por similaridade.
2. **Medição:** criar perguntas de referência e medir recall@k e MRR antes de qualquer otimização.
3. **Divisão dos documentos:** comparar estratégias de chunking pelas métricas.
4. **Busca híbrida:** combinar busca textual e vetorial, útil para nomes de produtos e valores exatos.
5. **Reranking:** adicionar só se as métricas justificarem.
6. **Resposta:** avaliar se o orçamento se apoia no que foi recuperado e se os valores conferem com a tabela.
7. **RAG com agente:** deixar o agente decidir o que buscar, em comparação com o fluxo fixo.
8. **Framework:** reescrever uma parte com LangChain ou similar, para comparar com a versão manual.

### Outros encaixes naturais

| Tema da ementa | Uso no produto |
|---|---|
| Multimodal e OCR (Módulo 2) | Ler prints e transcrever áudios de WhatsApp |
| Human-in-the-loop e guardrails (Módulos 4 e 8) | Confirmar pedido, valor e data antes de salvar ou enviar |
| Roteamento de modelos e cache (Módulo 8) | Controlar o custo por pedido |
| Observabilidade (Módulos 2 e 4) | Registrar chamadas, latência, tokens e custo |
| Riscos legais e de dados (Módulo 10) | LGPD e tratamento de dados de clientes |
| Fine-tuning (Módulo 9) | Testar contra o modelo base, só se a avaliação indicar necessidade |

### Módulos sem aplicação direta no produto

Valem como estudo, sem forçar uso no MVP:

- **Módulo 1:** redes neurais em JavaScript e ML em vídeo e jogos.
- **Módulo 6:** Kubernetes, AIOps e FinOps. Só a parte de CI/CD é necessária ao Capstone.
- **Módulo 7:** ferramentas de gestão. O projeto usa só o que apoia o próprio backlog.
- **Módulo 4, Unidade 9, e Módulo 8, Unidade 3:** multiagente. O Capstone admite "múltiplos agentes ou LLMs", então um fluxo simples basta.
- **Módulo 12:** carreira, para a fase final.

## 3. Conflitos com o briefing e as regras do negócio

| Tema | Briefing ou regras | Ementa | Encaminhamento |
|---|---|---|---|
| Linguagem | Python | JavaScript nos módulos práticos; o Capstone não fixa a linguagem do back-end | **Definido:** Python no back-end; exemplos do curso precisam ser adaptados |
| Servidor MCP | FastMCP | MCP em JavaScript/TypeScript | **Definido:** FastMCP |
| Papel do MCP | Servidor no back-end | Também MCP na aplicação e na interface (Entregas 2 e 3) | Começar pelo servidor; MCP na interface fica como etapa de estudo posterior |
| Orquestração | Não definida | ADK no Capstone; LangGraph no Módulo 4 | Opcional; começar com fluxo simples e adotar um framework só se houver necessidade |
| Interface | React, TypeScript e Tailwind (escolha de Julia) | Angular, citado explicitamente na Unidade 4 do Capstone | **Definido:** React; desvio consciente da ementa |
| Banco | PostgreSQL | Postgres no primeiro RAG; banco vetorial no Capstone | Avaliar pgvector para manter um único banco |
| Implantação | Docker Compose | CI/CD e implantação | Manter os dois |
| Avaliação | Conjuntos de referência, regressões e avaliação independente | Métricas de agentes e de fine-tuning, sem suíte dedicada | Manter o briefing; é um diferencial do portfólio |
| Ordem | Validar antes de desenvolver | Construir para entregar o Capstone | **Definido:** projeto de portfólio; a venda só avança após um teste de compra real |

## 4. Ambiente

Conferido em 04/11/2026:

| Ferramenta | Situação |
|---|---|
| Node 26.13.0 e npm 11.20.0 | Instalados |
| Docker | Não será instalado localmente, para poupar memória; o Compose roda no GitHub Actions (ver [provedores e ambiente](03-provedores-e-ambiente.md)) |
| Cliente PostgreSQL (`psql`) | Não instalado; dispensável, o banco fica no Neon |
| Python | 3.12 instalado, além do 3.9 padrão; usar o 3.12, pois o FastMCP 4.1.6 exige 3.10 ou superior |

O projeto fica em pasta do OneDrive. Ao usar Docker, os dados do banco devem ficar em volume nomeado, fora da pasta sincronizada.

## 5. Decisões pendentes

Nenhuma decisão pendente neste plano; o andamento fica na [gestão do projeto](04-gestao-do-projeto.md).

**Definido em 04/11/2026, relação com o negócio:** o projeto é portfólio, com dados fictícios. A venda só avança após um teste de compra real, e o desenvolvimento não conta como validação comercial.

**Definido em 04/11/2026, forma de trabalho:** Claude escreve o código de Python e RAG e explica. Para manter o objetivo de aprendizado, cada passo do roteiro de RAG termina com:

- explicação do que foi feito, por que e quais alternativas foram descartadas;
- anotação em `docs/aprendizados/`, escrita em linguagem simples, com conceito, decisão e resultado das métricas;
- um experimento que Julia roda sozinha, como mudar um parâmetro e comparar as métricas.

## 6. Observações sobre a ementa

- A Unidade 1 do Módulo 9, "Quando fazer fine-tuning", repete os tópicos da Unidade 5 do Módulo 8. Parece erro de edição; o conteúdo real dessa unidade não está claro.
- A ementa não traz prazos, carga horária nem critérios detalhados, além dos fatores gerais da avaliação final: complexidade, funcionalidade, qualidade do código, apresentação e defesa.
