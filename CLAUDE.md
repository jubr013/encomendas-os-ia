# Encomendas OS com IA: instruções para o Claude

Projeto solo de portfólio e estudo. Conversas de WhatsApp viram pedidos e orçamentos estruturados, sempre com confirmação humana. Contexto em [README.md](README.md), [plano](docs/02-plano-pela-ementa.md), [provedores](docs/03-provedores-e-ambiente.md) e [gestão](docs/04-gestao-do-projeto.md).

## Forma de trabalho

O objetivo é aprender Python e RAG, não só entregar. Claude escreve o código de Python e RAG e explica. Cada passo do roteiro de RAG termina com:

- explicação do que foi feito, por que e quais alternativas foram descartadas;
- anotação em `docs/aprendizados/`, em linguagem simples, com conceito, decisão e resultado das métricas;
- um experimento para Julia rodar sozinha, como mudar um parâmetro e comparar as métricas.

Cada passo do RAG começa sem framework e só avança quando a avaliação mostrar ganho.

## Dados e segredos

- **Só dados fictícios.** O nível gratuito do Gemini usa os dados enviados para melhorar produtos do Google. Dados reais de clientes exigem migrar antes para nível pago ou outro provedor.
- **Segredos só no `.env`**, que fica fora do Git. Variável nova entra em `.env.example`, sem valor.
- **O repositório é público.** `docs/01-analise-de-mercado-e-comparativo.md` fica só local: não citar seu conteúdo em arquivos versionados, issues ou PRs.

## Ambiente

- Python 3.12 ou superior. Os comandos locais são para PowerShell, no Windows.
- O ambiente virtual fica em `$env:USERPROFILE\.venvs\encomendas-os-ia`, fora do OneDrive.
- Sem Docker, WSL ou banco na máquina. O plano é usar o Neon como banco e validar o Docker Compose no GitHub Actions; nenhum dos dois está configurado ainda.
- Preferir serviços gratuitos e não sobrecarregar a memória da máquina.

## Verificação

Rodar antes de propor commit. O CI executa os mesmos comandos em cada PR e em cada push na `main`, em Linux:

```powershell
ruff check .
pytest
```

Dependência entra em `pyproject.toml` só quando o código precisar dela.

## Git e PR

- **Base:** a branch nasce de `main`, e o PR vai para `main`. Só perguntar em exceção.
- **Branch:** `<tipo>/<issue>-<descrição>`, como `feat/3-ambiente-python`.
- **Commit e título do PR:** `<tipo>: <descrição em português>`, como `ci: roda lint e testes no GitHub Actions`. Tipos já usados: `feat`, `docs`, `ci`, `test`.
- **Corpo do PR:** seções `## O que muda` e `## Como foi verificado`, com o que não foi verificado dito de forma explícita, e `Closes #N` no fim.
- Push, abertura de PR, merge e mudanças em issues continuam dependendo de confirmação.

## Quadro

Cards são issues com critérios de aceite, no GitHub Project "Encomendas OS com IA". Colunas, labels e milestones estão em [gestão do projeto](docs/04-gestao-do-projeto.md).

## Padrões para as skills

Estas respostas valem como decisão já tomada, então as skills não precisam perguntar:

- **Papéis:** Julia é responsável e testadora de tudo. Não perguntar nem validar identidade.
- **Prioridade e data:** opcionais, só se Julia pedir. Sprint e milestone continuam sendo perguntados.
- **`.specs/` (spec, tarefas e handoff):** só em cards maiores: passos do roteiro de RAG, esquema de banco ou mudanças em vários módulos. Card pequeno usa só a issue e o PR.
- **Replicação em outra linha do produto:** não se aplica. Só existe uma linha, então não perguntar.
