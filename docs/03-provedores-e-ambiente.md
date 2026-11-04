# Encomendas OS: provedores e ambiente

**Data:** 04/11/2026
**Status:** diretriz de Julia em 04/11/2026: usar modelos gratuitos sempre que possível, não sobrecarregar a memória da máquina e publicar no GitHub. A configuração abaixo é a recomendação para isso.

## 1. Configuração recomendada

| Camada | Escolha | Custo | Observação |
|---|---|---|---|
| LLM | Gemini, nível gratuito, começando por `gemini-3.1-flash-lite` | Grátis | Uma chave só; limites no painel do AI Studio |
| Embeddings | Gemini, nível gratuito | Grátis | Voyage AI (200 milhões de tokens grátis) entra como comparação |
| Banco | Neon, plano gratuito, com pgvector | Grátis, sem cartão | Nada de banco rodando na máquina |
| Docker Compose | Arquivo no repositório, validado no GitHub Actions | Grátis em repositório público | Sem Docker nem WSL locais |
| Código | Provedores atrás de uma interface pequena | | Trocar e comparar sem reescrever o sistema |

**Limites a respeitar:**

- **Só dados fictícios no Gemini gratuito:** nesse nível, os dados são usados para melhorar produtos do Google. Se o projeto receber dados reais de clientes, é obrigatório migrar para um nível pago ou outro provedor.
- **Cotas não verificadas:** a documentação não publica os números do nível gratuito, e eles aparecem só no painel. Avaliações grandes podem precisar de pausas e novas tentativas, assunto que a ementa cobre no Módulo 2.
- **Neon:** 1 GB por projeto e 100 CU-hours mensais. O banco é suspenso após 5 minutos parado, então a primeira consulta depois disso pode demorar mais. Outros serviços hospedados não foram comparados.

Nenhum modelo foi testado ainda com dados deste projeto. Os preços abaixo continuam como referência para uma eventual migração.

## 2. Preços

Valores em dólar por milhão de tokens, consultados nas páginas oficiais em 04/11/2026. A lista traz apenas opções representativas.

### LLM

| Provedor | Modelo | Entrada | Saída | Custo por pedido (estimado) |
|---|---|---:|---:|---:|
| Anthropic | Claude Haiku 5.5 | 0,10 | 0,50 | US$ 0,00055 |
| Anthropic | Claude Sonnet 5.5 | 2,00 | 10,00 | US$ 0,011 |
| Anthropic | Claude Opus 5.5 | 4,00 | 20,00 | US$ 0,022 |
| OpenAI | `gpt-6-luna` | 0,10 | 0,50 | US$ 0,00055 |
| OpenAI | `gpt-6.1-terra` | 1,00 | 5,00 | US$ 0,0055 |
| Google | `gemini-3.1-flash-lite` | 0,25 | 1,50 | US$ 0,0015 |
| Google | `gemini-3.6-flash` (dobra em 01/01/2027) | 0,75 | 3,75 | US$ 0,0041 |

**Premissa da estimativa:** 3.000 tokens de entrada e 500 de saída por pedido, sem cache. É um número ilustrativo: tokens de raciocínio podem aumentar a saída, e o custo real será medido na Entrega 1.

Com essa premissa, uma avaliação de 100 casos custa cerca de US$ 0,06 no Haiku 5.5, US$ 1,10 no Sonnet 5.5 e US$ 2,20 no Opus 5.5.

### Embeddings

| Provedor | Modelo | Preço | Observação |
|---|---|---:|---|
| Voyage AI | `voyage-4-lite` | 0,02 | 200 milhões de tokens grátis por modelo |
| Voyage AI | `voyage-4` | 0,06 | 200 milhões de tokens grátis; equilíbrio entre qualidade e custo |
| Voyage AI | `voyage-4-large` | 0,12 | 200 milhões de tokens grátis; maior qualidade |
| OpenAI | `text-embedding-3-small` | 0,02 | |
| OpenAI | `text-embedding-3-large` | 0,13 | |
| Google | `gemini-embedding-001` | 0,15 | |

O reranking da Voyage custa US$ 0,05 (`rerank-3`) ou US$ 0,02 (`rerank-3-lite`), também com 200 milhões de tokens grátis. Isso atende ao passo 5 do roteiro de RAG, se as métricas justificarem.

## 3. Alternativas

| Opção | A favor | Contra |
|---|---|---|
| **Claude e Voyage** | Saídas estruturadas e reranking disponíveis; cota grátis de embeddings | Duas contas; a Voyage exige conta no MongoDB Atlas |
| **OpenAI** | Uma conta só; é o provedor usado no projeto do Módulo 2 da ementa | Sem cota grátis confirmada na página consultada |
| **Gemini** | Nível gratuito cobre texto e embeddings | Dados do nível gratuito são usados para melhorar produtos do Google; aceitável apenas com dados fictícios |
| **Modelo local (Ollama)** | Sem custo por uso | Inviável nesta máquina como opção principal (ver seção 4) |

## 4. Ambiente

Conferido em 04/11/2026:

| Item | Situação | Consequência |
|---|---|---|
| Python | **3.12 já instalado**, além do 3.9 padrão | Não precisa instalar; usar `py -3.12` e ambiente virtual |
| Node e npm | 26.13.0 e 11.20.0 | Prontos para React |
| Windows | 11 Home, build 26300; virtualização ativa | Roda containers Linux, o suficiente para o projeto |
| WSL | Não instalado | Necessário para o Docker Desktop |
| RAM | 8 GB instalados; 5,9 GB utilizáveis; 0,5 GB livre durante a verificação | **Principal limitação** |
| CPU | Ryzen 3 3200U | Modelos locais tendem a ser lentos; execução não testada |
| Disco | 75 GB livres | Suficiente |

### Docker

O Docker Desktop pede 8 GB de RAM. A máquina atinge esse valor no instalado, mas não no utilizável, então **WSL e Docker não serão instalados localmente**.

No desenvolvimento, a API e a interface rodam direto na máquina e o banco fica no Neon, que tem pgvector em todos os planos. O `docker-compose.yml` continua no repositório e é executado no GitHub Actions, o que preserva a execução reproduzível sem ocupar memória local.

### Chaves de API

As chaves ficam em um arquivo `.env` local, fora do Git, e nunca são coladas no chat.

## Fontes

- [Preços da Anthropic](https://platform.claude.com/docs/en/about-claude/pricing)
- [Embeddings na documentação da Anthropic](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- [Preços da Voyage AI](https://docs.voyageai.com/docs/pricing)
- [Preços da OpenAI](https://developers.openai.com/api/docs/pricing)
- [Preços do Gemini](https://aistudio.google.com/docs/pricing)
- [Docker Desktop no Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Limites do Gemini](https://aistudio.google.com/docs/rate-limits)
- [Planos da Neon](https://neon.com/pricing)
- [pgvector na Neon](https://neon.com/docs/extensions/pgvector)
- [Cobrança do GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
