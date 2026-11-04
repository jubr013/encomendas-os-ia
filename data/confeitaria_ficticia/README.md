# Confeitaria Doce Exemplo (dados fictícios)

**Tudo nesta pasta é inventado:** a confeitaria, os preços, os bairros, os pedidos e as conversas. Não há dados pessoais reais, e clientes são identificados apenas por códigos.

| Arquivo | Conteúdo | Uso previsto |
|---|---|---|
| `cardapio.md` | Produtos e descrições | Documento para o RAG |
| `tabela_precos.md` | Códigos e preços; é a fonte de verdade dos valores | Documento para o RAG |
| `politicas.md` | Sinal, prazos, entrega, cancelamento e temas | Documento para o RAG |
| `pedidos_anteriores.jsonl` | Pedidos já feitos, um por linha | Busca por pedidos parecidos |
| `conversas.jsonl` | Conversas no estilo WhatsApp com o resultado esperado | Conjunto de referência para avaliação |

## Campos de `conversas.jsonl`

- `caso`: o que a conversa testa.
- `data_referencia`: o "hoje" da conversa, para interpretar prazos e datas relativas.
- `esperado.tipo`: `novo_pedido`, `duvida` ou `cancelamento`.
- `esperado.itens`: produtos identificados, com código e quantidade.
- `esperado.entrega`: código de entrega ou retirada, ou `null` se não informado.
- `esperado.faltando`: informações que precisam ser perguntadas à cliente.
- `esperado.alertas`: pontos que exigem atenção humana.
- `esperado.total`: valor total, ou `null` quando o pedido está incompleto.

Os valores de `esperado` foram definidos à mão, e os testes em `tests/test_dados_ficticios.py` conferem sua consistência com a tabela de preços.
