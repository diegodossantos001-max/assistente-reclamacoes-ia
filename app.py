"""Assistente de Reclamações com IA: página web em Streamlit.

Painel com as 200 reclamações já classificadas (sem custo) e classificação ao vivo,
liberada por código de acesso para controlar o gasto com a API.
"""
import altair as alt
import pandas as pd
import streamlit as st

from classificador import LIMITE_CARACTERES, MODELO, classificar, prioridade

REPOSITORIO = "https://github.com/diegodossantos001-max/assistente-reclamacoes-ia"
LIMITE_POR_SESSAO = 15
AZUL = "#2a78d6"
LOGISTICA = ["Produto não entregue", "Produto errado ou incompleto", "Atraso na entrega"]

EXEMPLOS = {
    "Espera simples": "estou aguardando o produto chegar",
    "Prazo estourado": "Comprei há mais de 20 dias, já passou do prazo de entrega e até hoje não recebi. Mandei e-mail e ninguém respondeu.",
    "Pedido incompleto": "Comprei dois aparelhos e só chegou um!!! Cadê meu produto?",
    "Qualidade": "O tecido é bem mais fino do que parecia na foto, mas serve.",
}

ROTULOS = {
    "alta": "🔴 Alta", "media": "🟠 Média", "baixa": "🟢 Baixa",
    "alto": "🔴 Alto", "medio": "🟠 Médio", "baixo": "🟢 Baixo",
    "sim": "Sim", "nao": "Não",
}

st.set_page_config(page_title="Assistente de Reclamações com IA", page_icon="📨", layout="wide")


@st.cache_data
def carregar_dados():
    base = pd.read_csv("reclamacoes_classificadas_v4.csv", encoding="utf-8-sig")
    base["prioridade"] = [prioridade(u, r) for u, r in zip(base["urgencia"], base["risco_perder_cliente"])]
    comparacao = pd.read_csv("comparacao_modelos.csv", encoding="utf-8-sig", index_col=0)
    return base, comparacao


def segredo(nome: str):
    """Lê um segredo do Streamlit sem quebrar a página quando ele não existe."""
    try:
        return st.secrets.get(nome)
    except Exception:
        return None


base, comparacao = carregar_dados()

st.title("📨 Assistente de Reclamações com IA")
st.markdown(
    "Classifica reclamações de clientes por **tema, urgência e risco de perder o cliente**, "
    "sugere o próximo passo e um rascunho de resposta. A qualidade foi medida contra uma "
    f"classificação humana. [Código e metodologia no GitHub]({REPOSITORIO})."
)

aba_classificar, aba_painel, aba_qualidade = st.tabs(["🔎 Classificar uma reclamação", "📊 Painel", "✅ Como foi avaliado"])

# ---------------------------------------------------------------- Classificar
with aba_classificar:
    st.markdown("Escolha um exemplo ou escreva uma reclamação, como um cliente escreveria.")
    colunas = st.columns(len(EXEMPLOS))
    for coluna, (nome, texto) in zip(colunas, EXEMPLOS.items()):
        if coluna.button(nome, use_container_width=True):
            st.session_state["texto"] = texto

    texto = st.text_area("Reclamação", key="texto", height=120, max_chars=LIMITE_CARACTERES,
                         placeholder="Ex.: ainda estou esperando meu pedido.")
    codigo = st.text_input("Código de acesso", type="password",
                           help="A classificação ao vivo usa a API da OpenAI e é liberada por código. O painel ao lado é aberto a todos.")

    usadas = st.session_state.get("usadas", 0)
    if st.button("Classificar", type="primary", disabled=not texto.strip()):
        codigo_certo = segredo("CODIGO_ACESSO")
        chave = segredo("OPENAI_API_KEY")
        if not codigo_certo or not chave:
            st.error("A classificação ao vivo ainda não foi configurada neste servidor.")
        elif codigo.strip() != str(codigo_certo):
            st.error("Código de acesso inválido. O painel continua disponível na aba ao lado.")
        elif usadas >= LIMITE_POR_SESSAO:
            st.warning(f"Limite de {LIMITE_POR_SESSAO} classificações por sessão atingido.")
        else:
            from openai import OpenAI
            with st.spinner("Classificando..."):
                try:
                    st.session_state["resultado"] = classificar(texto, OpenAI(api_key=chave))
                    st.session_state["usadas"] = usadas + 1
                except Exception:
                    st.error("Não foi possível classificar agora. Tente de novo em instantes.")

    r = st.session_state.get("resultado")
    if r:
        st.divider()
        fila = prioridade(r["urgencia"], r["risco_perder_cliente"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tema", r["tema"])
        c2.metric("Urgência", ROTULOS[r["urgencia"]])
        c3.metric("Risco de perder o cliente", ROTULOS[r["risco_perder_cliente"]])
        c4.metric("Fila", fila)
        if r["tema_secundario"]:
            st.caption(f"Tema secundário: {r['tema_secundario']}")
        if r["cliente_procurou_loja"] == "sim":
            st.warning("O cliente já procurou a loja e não teve solução.")
        st.markdown(f"**Por quê:** {r['justificativa']}")
        st.markdown(f"**Próximo passo:** {r['acao_sugerida']}")
        st.markdown("**Rascunho de resposta** (para o atendente revisar antes de enviar):")
        st.info(r["resposta_sugerida"])
        st.caption(f"Modelo: {MODELO} · prompt versão 4")

# ---------------------------------------------------------------- Painel
with aba_painel:
    st.markdown(f"**{len(base)} reclamações reais** (base pública Olist, notas 1 e 2), classificadas pela versão 4.")
    f1, f2 = st.columns(2)
    temas = f1.multiselect("Tema", sorted(base["tema"].unique()), placeholder="Todos os temas")
    urgencias = f2.multiselect("Urgência", ["alta", "media", "baixa"], format_func=lambda v: ROTULOS[v],
                               placeholder="Todas as urgências")
    dados = base
    if temas:
        dados = dados[dados["tema"].isin(temas)]
    if urgencias:
        dados = dados[dados["urgencia"].isin(urgencias)]

    if dados.empty:
        st.info("Nenhuma reclamação com esses filtros.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Reclamações", len(dados))
        m2.metric("Entrega e separação", f"{dados['tema'].isin(LOGISTICA).mean():.0%}")
        m3.metric("Atender hoje", int((dados["prioridade"] == "Atender hoje").sum()),
                  help="Urgência alta e risco alto de perder o cliente")
        m4.metric("Já procuraram a loja", int((dados["cliente_procurou_loja"] == "sim").sum()))

        g1, g2 = st.columns([3, 2])
        contagem = dados["tema"].value_counts().reset_index()
        contagem.columns = ["Tema", "Reclamações"]
        grafico = (
            alt.Chart(contagem)
            .mark_bar(color=AZUL, cornerRadiusEnd=4)
            .encode(x=alt.X("Reclamações:Q"), y=alt.Y("Tema:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
                    tooltip=["Tema", "Reclamações"])
            .properties(title="Reclamações por tema", height=300)
        )
        g1.altair_chart(grafico, use_container_width=True)

        matriz = pd.crosstab(dados["urgencia"], dados["risco_perder_cliente"]).reindex(
            index=["alta", "media", "baixa"], columns=["alto", "medio", "baixo"], fill_value=0)
        matriz.index = [ROTULOS[i] for i in matriz.index]
        matriz.columns = [ROTULOS[c] for c in matriz.columns]
        g2.markdown("**Urgência × risco de perder o cliente**")
        g2.dataframe(matriz, use_container_width=True)

        st.markdown("**Fila de atendimento** (ordenada por prioridade)")
        ordem = {"Atender hoje": 0, "Atender em seguida": 1, "Verificar em momento oportuno": 2, "Acompanhar": 3}
        fila = dados.assign(_ordem=dados["prioridade"].map(ordem)).sort_values("_ordem")
        st.dataframe(
            fila[["prioridade", "tema", "resumo", "acao_sugerida", "cliente_procurou_loja"]],
            hide_index=True, use_container_width=True,
            column_config={
                "prioridade": "Prioridade", "tema": "Tema", "resumo": "Resumo",
                "acao_sugerida": "Próximo passo", "cliente_procurou_loja": "Já procurou a loja",
            },
        )

        with st.expander("Ver uma reclamação em detalhe"):
            escolha = st.selectbox("Reclamação", fila.index, format_func=lambda i: fila.loc[i, "texto"][:90])
            linha = fila.loc[escolha]
            st.markdown(f"**Texto do cliente:** {linha['texto']}")
            st.markdown(f"**Por quê:** {linha['justificativa']}")
            st.markdown("**Rascunho de resposta:**")
            st.info(linha["resposta_sugerida"])

# ---------------------------------------------------------------- Qualidade
with aba_qualidade:
    st.markdown(
        "Cada versão do prompt foi comparada com uma **classificação humana feita sem ver a resposta da IA**. "
        "O teste final usou 30 reclamações que nenhuma versão tinha visto."
    )
    tabela = comparacao.copy()
    tabela["tema"] = tabela["tema"].map("{:.0%}".format)
    tabela["urgencia"] = tabela["urgencia"].map("{:.0%}".format)
    tabela["custo_por_1000"] = tabela["custo_por_1000"].map(lambda v: "—" if pd.isna(v) else f"US$ {v:.2f}".replace(".", ","))
    tabela = tabela.drop(columns=["segundos_por_reclamacao"])
    tabela.columns = ["Acerto no tema", "Acerto na urgência", "Custo por mil reclamações"]
    st.dataframe(tabela, use_container_width=True)
    st.image("04_comparacao_modelos.png", use_container_width=True)
    st.markdown(
        "**Conclusão:** o maior ganho veio de transformar critérios de negócio em regras escritas "
        "([guia de classificação](" + REPOSITORIO + "/blob/main/GUIA_DE_CLASSIFICACAO.md)), "
        "e não de trocar por um modelo 8 vezes mais caro. Com 30 casos, cada erro vale cerca de 3 pontos: "
        "os percentuais são indicativos."
    )

st.caption("Projeto de Diego dos Santos · Python, Pandas, OpenAI API e Streamlit · "
           "A resposta sugerida é sempre um rascunho para revisão humana.")
