# Guia de classificação de reclamações

Critérios usados tanto na classificação humana (gabarito e teste) quanto no prompt da versão 4. Foram escritos a partir da análise dos erros das versões 1 a 3.

## Temas

| # | Tema | Quando usar |
| --- | --- | --- |
| 1 | Atraso na entrega | O produto **chegou**, mas depois do prazo prometido |
| 2 | Produto não entregue | O cliente diz que **ainda não recebeu** ("aguardando", "esperando", "não chegou", "consta entregue mas não recebi") |
| 3 | Produto errado ou incompleto | Chegou item diferente do comprado ou faltou parte do pedido (ex.: comprou 2 e recebeu 1) |
| 4 | Produto com defeito ou avariado | Chegou quebrado, danificado ou não funciona |
| 5 | Qualidade abaixo do esperado | Funciona, mas é pior do que o anunciado (material, tamanho, acabamento) |
| 6 | Cobrança, pagamento ou reembolso | Valor, estorno, nota fiscal ou devolução do dinheiro |
| 7 | Atendimento ou falta de resposta | **Só** quando a queixa é apenas sobre o atendimento, sem outro problema por trás |
| 8 | Outros | Comentário elogioso ou sem problema, retirada do produto nos Correios, problema de frete sem atraso, crítica genérica à loja |

**Regras de tema**

- Com mais de um problema, o tema é o de **maior prioridade**; o outro vai como tema secundário.
- Se o cliente já procurou a loja e não teve resposta, o tema continua sendo o problema de origem, e isso é registrado no campo `cliente_procurou_loja`.

## Urgência

**Alta**
- Atraso confirmado: "já passou do prazo", "até hoje não recebi", cita datas ou muito tempo de espera.
- Produto errado ou faltando parte do pedido: o cliente pagou e está sem o que comprou.
- Cobrança indevida.
- O cliente já procurou a loja sem solução, cita reincidência, ameaça Procon ou processo, ou diz que não compra mais.

**Média**
- Espera com sinal de demora, mas sem prazo confirmado: "**ainda** estou esperando", "**continuo** esperando". Vale verificar em momento oportuno.
- Produto com defeito ou avariado.
- Outro problema que ainda precisa de solução da loja.

**Baixa**
- Espera simples, sem sinal de demora: "estou aguardando o produto" (pode estar dentro do prazo).
- Problema já resolvido (ex.: atrasou, mas chegou).
- Insatisfação com qualidade sem pedido de solução, elogio ou crítica genérica.
