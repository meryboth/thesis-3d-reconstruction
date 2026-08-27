"""
Calcula una posicion de camara razonable (vista 3/4, no cenital) para un
export de Splatfacto (.ply), usando el rango percentil 5-95 de las
gaussianas (robusto a floaters/outliers, que sabemos que existen en los
exports crudos sin limpiar en SuperSplat).

Uso: python compute_splat_camera.py <archivo.ply>
Imprime JSON: {"position": [x,y,z], "target": [x,y,z], "fov": N}
"""
import json
import sys

import numpy as np
from plyfile import PlyData

path = sys.argv[1]
ply = PlyData.read(path)
v = ply["vertex"]
pts = np.stack([v["x"], v["y"], v["z"]], axis=1).astype(np.float64)

lo = np.percentile(pts, 5, axis=0)
hi = np.percentile(pts, 95, axis=0)
center = (lo + hi) / 2
extent = hi - lo
radius = float(np.linalg.norm(extent)) / 2

# Vista elevada con poco desplazamiento horizontal: en las pruebas, una
# camara "desde arriba y de lejos" evita mucho mejor el halo de floaters
# (gaussianas gigantes cerca del sujeto) que un 3/4 simetrico en X/Z a la
# misma distancia -- el offset horizontal simetrico termina mirando A TRAVES
# del halo, mientras que una elevacion fuerte lo esquiva desde arriba.
dist = radius * 5.5
position = [
    float(center[0]),
    float(center[1] + dist * 0.85),
    float(center[2] + dist * 0.55),
]
target = [float(center[0]), float(center[1]), float(center[2])]

print(json.dumps({"position": position, "target": target, "fov": 60, "center": center.tolist(), "radius": radius}))
