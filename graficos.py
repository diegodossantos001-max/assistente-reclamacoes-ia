import sys, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "Inter" in f: fm.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Inter", "font.size": 11, "axes.edgecolor": "#c9c8c2",
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
TXT, MUT, BLUE, ORANGE = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"
d = pd.read_csv(sys.argv[1], encoding="utf-8-sig"); out = sys.argv[2]
n = len(d)

# 1. Temas
t = d["tema"].value_counts().sort_values()
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
ax.barh(t.index, t.values, color=BLUE, height=0.62)
for y, v in enumerate(t.values):
    ax.text(v + 1, y, f"{v}  ({v/n:.0%})", va="center", color=TXT, fontsize=10)
ax.set_xlim(0, t.max() * 1.22); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.tick_params(axis="y", length=0, colors=TXT)
fig.suptitle("Entrega e separação de pedidos somam 71% das reclamações", x=0.02, ha="left", fontsize=14, fontweight="semibold", color=TXT)
ax.set_title(f"Reclamações por tema · amostra de {n} avaliações com nota 1 ou 2 (Olist)", loc="left", color=MUT, fontsize=10, pad=10)
fig.tight_layout(); fig.savefig(f"{out}/01_temas.png"); plt.close(fig)

# 2. Matriz de prioridade
ordem_u, ordem_r = ["alta", "media", "baixa"], ["alto", "medio", "baixo"]
m = pd.crosstab(d["urgencia"], d["risco_perder_cliente"]).reindex(index=ordem_u, columns=ordem_r, fill_value=0)
fig, ax = plt.subplots(figsize=(6.6, 4.6), dpi=200)
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("b", ["#eef4fc", "#9ec5f4", "#3987e5", "#184f95"])
ax.imshow(m.values, cmap=cmap, vmin=0, vmax=m.values.max())
for i in range(3):
    for j in range(3):
        v = m.values[i, j]
        ax.text(j, i, str(v), ha="center", va="center", fontsize=15, fontweight="semibold",
                color="#ffffff" if v > m.values.max() * 0.45 else TXT)
for k in range(4):
    ax.axhline(k - 0.5, color="#fcfcfb", lw=3); ax.axvline(k - 0.5, color="#fcfcfb", lw=3)
ax.set_xticks(range(3), ["Alto", "Médio", "Baixo"]); ax.set_yticks(range(3), ["Alta", "Média", "Baixa"])
ax.set_xlabel("Risco de perder o cliente", color=MUT); ax.set_ylabel("Urgência", color=MUT)
ax.tick_params(length=0, colors=TXT); [s.set_visible(False) for s in ax.spines.values()]
fig.suptitle(f"{m.loc['alta','alto']} casos para atender primeiro", x=0.03, ha="left", fontsize=14, fontweight="semibold", color=TXT)
ax.set_title("Urgência × risco de perder o cliente (número de reclamações)", loc="left", color=MUT, fontsize=10, pad=10)
fig.tight_layout(); fig.savefig(f"{out}/02_matriz_prioridade.png"); plt.close(fig)

# 3. Acerto antes x depois (validação)
cats = ["Tema", "Urgência"]; v1 = [0.30, 0.60]; v3 = [0.60, 0.75]
fig, ax = plt.subplots(figsize=(7, 4.4), dpi=200)
import numpy as np
x = np.arange(2); w = 0.34
for off, vals, cor, nome in [(-w/2 - 0.01, v1, ORANGE, "Prompt versão 1"), (w/2 + 0.01, v3, BLUE, "Prompt versão 3")]:
    ax.bar(x + off, vals, w, color=cor, label=nome)
    for xi, v in zip(x + off, vals):
        ax.text(xi, v + 0.02, f"{v:.0%}", ha="center", color=TXT, fontsize=11, fontweight="semibold")
ax.set_xticks(x, cats); ax.set_ylim(0, 1); ax.set_yticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
ax.grid(axis="y", color="#e6e5e0", lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0, colors=TXT)
ax.legend(frameon=False, loc="upper left", fontsize=10)
fig.suptitle("Acerto da IA dobrou na classificação por tema", x=0.02, ha="left", fontsize=14, fontweight="semibold", color=TXT)
ax.set_title("Concordância com a classificação humana em 20 reclamações novas (validação)", loc="left", color=MUT, fontsize=10, pad=10)
fig.tight_layout(); fig.savefig(f"{out}/03_acerto_validacao.png"); plt.close(fig)
print("ok")
