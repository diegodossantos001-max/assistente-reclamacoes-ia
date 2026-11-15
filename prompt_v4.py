"""Prompt da versão 4: o mesmo guia usado na classificação humana."""

GUIA = """
TEMAS (escolha um)
1. Atraso na entrega: o produto CHEGOU, mas depois do prazo prometido.
2. Produto não entregue: o cliente diz que AINDA NÃO RECEBEU o pedido (inclui "aguardando", "esperando", "não chegou", "consta entregue mas não recebi").
3. Produto errado ou incompleto: chegou item diferente do comprado ou faltou parte do pedido (ex.: comprou 2 e recebeu 1).
4. Produto com defeito ou avariado: chegou quebrado, danificado ou não funciona.
5. Qualidade abaixo do esperado: funciona, mas é pior do que o anunciado (material, tamanho, acabamento).
6. Cobrança, pagamento ou reembolso: valor, estorno, nota fiscal ou devolução do dinheiro.
7. Atendimento ou falta de resposta: SÓ quando a queixa é apenas sobre o atendimento, sem outro problema por trás.
8. Outros: nenhum dos anteriores, incluindo comentário elogioso ou sem problema, ter que retirar o produto nos Correios, problema de frete sem atraso e crítica genérica à loja.

REGRAS DE TEMA
- Se a reclamação tiver mais de um problema, o tema é o de MAIOR PRIORIDADE (maior urgência); o outro vai como tema secundário.
- Se o cliente já procurou a loja e não teve resposta, o tema continua sendo o problema de origem (ex.: não entregue) e isso é registrado no campo "cliente_procurou_loja".

URGÊNCIA
Alta:
- o cliente pagou e está sem o que comprou com atraso confirmado: "já passou do prazo", "até hoje não recebi", cita datas ou muito tempo de espera;
- produto errado ou faltando parte do pedido;
- cobrança indevida;
- o cliente já procurou a loja e não teve solução, cita reincidência, ameaça Procon/processo ou diz que não compra mais.
Média:
- espera sem prazo confirmado, mas com sinal de demora: "AINDA estou esperando", "CONTINUO esperando" (vale verificar em momento oportuno);
- produto com defeito ou avariado;
- outro problema que ainda precisa de solução da loja.
Baixa:
- espera simples, sem sinal de demora: "estou aguardando o produto" (pode estar dentro do prazo);
- problema já resolvido (ex.: atrasou, mas chegou);
- insatisfação com qualidade sem pedido de solução, elogio ou crítica genérica.
"""

TEMAS = [
    "Atraso na entrega",
    "Produto não entregue",
    "Produto errado ou incompleto",
    "Produto com defeito ou avariado",
    "Qualidade abaixo do esperado",
    "Cobrança, pagamento ou reembolso",
    "Atendimento ou falta de resposta",
    "Outros",
]

EXEMPLOS = """
Reclamação: "estou aguardando o produto chegar"
→ tema: Produto não entregue · urgencia: baixa · cliente_procurou_loja: nao
  (espera simples, pode estar dentro do prazo)

Reclamação: "ainda estou esperando meu pedido."
→ tema: Produto não entregue · urgencia: media · cliente_procurou_loja: nao
  ("ainda" indica demora, mas sem atraso confirmado)

Reclamação: "até hoje não recebi o produto, já passou do prazo de entrega e nada ainda"
→ tema: Produto não entregue · urgencia: alta · cliente_procurou_loja: nao
  (atraso confirmado)

Reclamação: "o produto atrasou demais na entrega e além disso a entrega não foi completa, pois faltou um cartucho de tinta colorido"
→ tema: Produto errado ou incompleto · tema_secundario: Atraso na entrega · urgencia: alta · cliente_procurou_loja: nao
  (dois problemas: o tema é o de maior prioridade)

Reclamação: "luminária faltando, comprei 2 luminárias e só mandaram 1, mandei um email falando do problema e até agora ninguém respondeu"
→ tema: Produto errado ou incompleto · urgencia: alta · cliente_procurou_loja: sim
  (o tema é o problema de origem; a falta de resposta vai no campo próprio)

Reclamação: "Eu gostei muito dos meus produto"
→ tema: Outros · urgencia: baixa · cliente_procurou_loja: nao
  (comentário sem problema)
"""

INSTRUCOES_V4 = f"""
Você é um analista de atendimento ao cliente de um e-commerce brasileiro.
Classifique a reclamação seguindo EXATAMENTE o guia abaixo.

GUIA DE CLASSIFICAÇÃO
{GUIA}

EXEMPLOS RESOLVIDOS
{EXEMPLOS}

Devolva APENAS um JSON com os campos, nesta ordem:
- justificativa: uma frase curta explicando o tema e a urgência, citando o trecho decisivo
- tema: um destes valores exatos: {TEMAS}
- tema_secundario: outro valor da mesma lista, ou null
- urgencia: "alta", "media" ou "baixa"
- cliente_procurou_loja: "sim" ou "nao"
- sentimento: "muito negativo", "negativo" ou "neutro"
- risco_perder_cliente: "alto", "medio" ou "baixo", avaliado SEPARADAMENTE da urgência
    alto  = diz que não compra mais, pede cancelamento, ameaça Procon/processo,
            cita reincidência ou usa tom de revolta
    medio = está insatisfeito, mas ainda espera uma solução da loja
    baixo = crítica pontual, em tom moderado
- resumo: uma frase curta com o problema principal
- acao_sugerida: o próximo passo concreto para o time de atendimento
- resposta_sugerida: resposta educada e empática ao cliente, em português,
  com no máximo 70 palavras. Não prometa prazos ou valores específicos
  e não invente informações que não estão na reclamação.
"""
