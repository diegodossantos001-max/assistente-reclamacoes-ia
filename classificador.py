"""Classificação de uma reclamação com o prompt da versão 4 (gpt-4o-mini)."""
import json

from prompt_v4 import INSTRUCOES_V4, TEMAS

MODELO = "gpt-4o-mini"
LIMITE_CARACTERES = 1000

URGENCIAS = ["alta", "media", "baixa"]
RISCOS = ["alto", "medio", "baixo"]


def _escolher(valor, opcoes, padrao):
    """Garante que o valor devolvido pela IA está entre as opções esperadas."""
    valor = str(valor or "").strip().lower().replace("é", "e")
    for opcao in opcoes:
        if valor == opcao.lower():
            return opcao
    return padrao


def normalizar_resultado(bruto: dict) -> dict:
    """Valida o JSON da IA para que a tela nunca mostre um valor fora da lista."""
    tema = bruto.get("tema") if bruto.get("tema") in TEMAS else "Outros"
    secundario = bruto.get("tema_secundario")
    secundario = secundario if secundario in TEMAS and secundario != tema else None
    return {
        "justificativa": str(bruto.get("justificativa", "")).strip(),
        "tema": tema,
        "tema_secundario": secundario,
        "urgencia": _escolher(bruto.get("urgencia"), URGENCIAS, "media"),
        "cliente_procurou_loja": _escolher(bruto.get("cliente_procurou_loja"), ["sim", "nao"], "nao"),
        "sentimento": str(bruto.get("sentimento", "")).strip(),
        "risco_perder_cliente": _escolher(bruto.get("risco_perder_cliente"), RISCOS, "medio"),
        "resumo": str(bruto.get("resumo", "")).strip(),
        "acao_sugerida": str(bruto.get("acao_sugerida", "")).strip(),
        "resposta_sugerida": str(bruto.get("resposta_sugerida", "")).strip(),
    }


def classificar(texto: str, client) -> dict:
    """Envia a reclamação ao modelo e devolve a classificação validada."""
    texto = texto.strip()[:LIMITE_CARACTERES]
    resp = client.chat.completions.create(
        model=MODELO,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": INSTRUCOES_V4},
            {"role": "user", "content": texto},
        ],
    )
    return normalizar_resultado(json.loads(resp.choices[0].message.content))


def prioridade(urgencia: str, risco: str) -> str:
    """Traduz urgência e risco em uma fila de atendimento."""
    if urgencia == "alta" and risco == "alto":
        return "Atender hoje"
    if urgencia == "alta":
        return "Atender em seguida"
    if urgencia == "media":
        return "Verificar em momento oportuno"
    return "Acompanhar"
