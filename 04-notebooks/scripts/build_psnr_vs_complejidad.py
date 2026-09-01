"""
Grafico de dispersion: PSNR (dataset DJI) vs. nivel de complejidad geometrica,
una serie por tecnica (Nerfacto / Splatfacto). Usado en Cap. 4 (B3) y Cap. 5.

Solo se usa el dataset DJI de cada sitio para mantener el dispositivo de
captura constante entre los tres casos de estudio (evita mezclar la
variable de complejidad con la variable de dispositivo, que es la que
evalua H4 por separado).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = r"C:\nerfstudio_work\thesis\00-auditoria\charts\07_psnr_vs_complejidad.png"

# nivel de complejidad: 1=baja (Paraguas), 2=media (Templete), 3=alta (Panteon)
sitios = ["Los Paraguas\n(baja)", "Templete Central\n(media)", "Panteon Asoc. Espanola\n(alta)"]
x = [1, 2, 3]

nerfacto = [25.914, 19.466, 10.449]
splatfacto = [30.559, 23.575, 25.939]

fig, ax = plt.subplots(figsize=(9, 6))

ax.plot(x, nerfacto, "o-", color="#1f77b4", markersize=10, linewidth=2, label="Nerfacto (NeRF)")
ax.plot(x, splatfacto, "s-", color="#9467bd", markersize=10, linewidth=2, label="Splatfacto (3DGS)")

for xi, yi in zip(x, nerfacto):
    ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points", xytext=(0, -18), ha="center", fontsize=9, color="#1f77b4")
for xi, yi in zip(x, splatfacto):
    ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color="#9467bd")

ax.set_xticks(x)
ax.set_xticklabels(sitios)
ax.set_xlim(0.7, 3.3)
ax.set_ylabel("PSNR (dB) — mas alto es mejor")
ax.set_title("PSNR vs. nivel de complejidad geometrica (dataset DJI)\nH3 — divergencia esperada entre tecnicas")
ax.grid(True, alpha=0.3)
ax.legend()

fig.tight_layout()
fig.savefig(OUT, dpi=150)
print("guardado:", OUT)
