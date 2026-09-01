"""
Render rapido (proyeccion de puntos con color real, no rasterizacion de
gaussianas completa) del splat original vs. el limpio de la POC, para
verificar visualmente que la limpieza no se come geometria real del
edificio. No reemplaza un render real de Nerfstudio/SuperSplat -- es un
chequeo de sanidad rapido para la POC.
"""
from pathlib import Path
import numpy as np
from plyfile import PlyData

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ORIG_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\export\splat.ply")
CLEAN_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\export\splat-clean-poc.ply")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup")

SH_C0 = 0.28209479177387814


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def load(path):
    vertex = PlyData.read(str(path))["vertex"].data
    xyz = np.column_stack([vertex[c] for c in ["x", "y", "z"]]).astype(np.float64)
    dc = np.column_stack([vertex[f"f_dc_{i}"] for i in range(3)]).astype(np.float64)
    rgb = np.clip(0.5 + SH_C0 * dc, 0, 1)
    opacity_raw = np.asarray(vertex["opacity"], dtype=np.float64)
    alpha = sigmoid(opacity_raw) if (opacity_raw.min() < 0 or opacity_raw.max() > 1) else opacity_raw
    return xyz, rgb, alpha


def render_view(ax, xyz, rgb, alpha, elev, azim, title, point_size=1.2):
    # proyeccion simple: rotamos la nube a un sistema de camara y graficamos X/Y proyectados,
    # ordenando por profundidad (pintor's algorithm) para que lo cercano tape lo lejano.
    el = np.radians(elev)
    az = np.radians(azim)

    # direccion de camara
    cx, cy, cz = (np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el))
    forward = np.array([cx, cy, cz])
    forward /= np.linalg.norm(forward)
    world_up = np.array([0, 0, 1.0])
    right = np.cross(forward, world_up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)

    depth = xyz @ forward
    proj_x = xyz @ right
    proj_y = xyz @ up

    order = np.argsort(-depth)  # lejos primero, para pintar cerca encima
    ax.scatter(proj_x[order], proj_y[order], s=point_size, c=rgb[order], alpha=np.clip(alpha[order] * 0.9 + 0.1, 0, 1), linewidths=0)
    ax.set_facecolor("black")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title(title, fontsize=10, color="black")


def main():
    xyz_o, rgb_o, alpha_o = load(ORIG_PATH)
    xyz_c, rgb_c, alpha_c = load(CLEAN_PATH)

    # Vista oblicua "aerea", similar al angulo de captura del drone (mirando hacia abajo y al frente)
    ELEV, AZIM = 35, -60

    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))
    render_view(axes[0], xyz_o, rgb_o, alpha_o, ELEV, AZIM, f"Original ({len(xyz_o):,} gaussianas)")
    render_view(axes[1], xyz_c, rgb_c, alpha_c, ELEV, AZIM, f"Limpio ({len(xyz_c):,} gaussianas, -{100*(1-len(xyz_c)/len(xyz_o)):.1f}%)")
    fig.suptitle("POC limpieza de floaters — Templete Central (DJI) — proyección de puntos con color real", fontsize=12)
    fig.tight_layout()
    out = OUT_DIR / "poc_floater_cleanup_render_wide.png"
    fig.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    print(f"[OK] {out}")

    # Vista mas cercana, centrada en el edificio (recorte del rango donde esta la masa densa)
    fig2, axes2 = plt.subplots(1, 2, figsize=(13, 6.2))
    render_view(axes2[0], xyz_o, rgb_o, alpha_o, ELEV, AZIM, f"Original — detalle ({len(xyz_o):,})", point_size=2.5)
    render_view(axes2[1], xyz_c, rgb_c, alpha_c, ELEV, AZIM, f"Limpio — detalle ({len(xyz_c):,})", point_size=2.5)
    for ax in axes2:
        ax.set_xlim(-18, 18)
        ax.set_ylim(-8, 20)
    fig2.suptitle("Mismo par, recortado al entorno del edificio (zoom)", fontsize=12)
    fig2.tight_layout()
    out2 = OUT_DIR / "poc_floater_cleanup_render_zoom.png"
    fig2.savefig(out2, dpi=150, facecolor="white", bbox_inches="tight")
    print(f"[OK] {out2}")


if __name__ == "__main__":
    main()
