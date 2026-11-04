# Encomendas OS com IA

Projeto de portfólio de AI Engineering: transformar conversas de WhatsApp de pequenos negócios que vendem por encomenda em pedidos e orçamentos estruturados, sempre com confirmação humana.

> **Status:** em construção. Por enquanto há apenas o ambiente Python e testes básicos. Todos os dados do projeto são fictícios.

## Objetivos de aprendizado

- Construir RAG em Python, começando sem framework e medindo cada melhoria.
- Criar um servidor MCP com FastMCP integrado ao PostgreSQL.
- Avaliar agentes e modelos com conjuntos de referência, não só verificar se o código executa.

## Stack planejada

| Camada | Tecnologia |
|---|---|
| RAG, agente, API e MCP | Python 3.12 e FastMCP |
| Banco e busca vetorial | PostgreSQL com pgvector, no Neon |
| LLM e embeddings | Gemini, nível gratuito |
| Interface | React, TypeScript e Tailwind |
| Reprodutibilidade | Docker Compose, executado no GitHub Actions |

## Documentação

- [Plano de acordo com a ementa](docs/02-plano-pela-ementa.md)
- [Provedores e ambiente](docs/03-provedores-e-ambiente.md)
- [Gestão do projeto](docs/04-gestao-do-projeto.md)

## Como rodar

Requer Python 3.12 ou superior. Os comandos abaixo são para PowerShell, no Windows.

O ambiente virtual fica fora da pasta do projeto para não ser sincronizado, caso ela esteja no OneDrive ou em serviço parecido.

```powershell
py -3.12 -m venv "$env:USERPROFILE\.venvs\encomendas-os-ia"
& "$env:USERPROFILE\.venvs\encomendas-os-ia\Scripts\Activate.ps1"
python -m pip install -e ".[dev]"
```

Para verificar:

```powershell
pytest
ruff check .
```
