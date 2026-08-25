from pathlib import Path
import json
import hashlib
import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData
from datetime import datetime

ROOT = Path(r"C:\nerfstudio_work\thesis")

CLOUDS = {
    "01-paraguas-vicentelopez": {
        "folder": ROOT / "01-paraguas-vicentelopez" / "02-resultados-finales" / "colmap-fotogrametria-densa",
        "candidates": [
            "fused_medium_high_clean.ply",
            "fused_medium_high.ply",
        ],
        "source": "COLMAP dense reconstruction",
    },

    "02-templete-central": {
        "folder": ROOT / "02-templete-central" / "02-resultados-finales" / "dji" / "colmap-fotogrametria",
        "candidates": [
            "nube-densa.xyz",
        ],
        "source": "RealityScan dense reconstruction export",
    },

    "03-panteon-asociacion-catalana": {
        "folder": ROOT / "03-panteon-asociacion-catalana" / "02-resultados-finales" / "dji" / "colmap-fotogrametria",
        "candidates": [
            "nube-densa.xyz",
        ],
        "source": "RealityScan dense reconstruction export",
    },
}


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def sha256_file(path, chunk_size=8 * 1024 * 1024):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def find_cloud(folder, candidates):
    for name in candidates:
        p = folder / name

        if p.exists():
            return p

    return None


def reservoir_sample_update(sample, seen, points, max_samples, rng):
    """
    Reservoir sampling, allowing us to compute local-density metrics
    without loading millions of points into RAM.
    """
    for p in points:
        seen += 1

        if len(sample) < max_samples:
            sample.append(p.copy())
            continue

        j = rng.integers(0, seen)

        if j < max_samples:
            sample[j] = p.copy()

    return seen


# ------------------------------------------------------------
# XYZ
# ------------------------------------------------------------

def analyze_xyz(path, sample_limit=150_000):
    minimum = np.array([np.inf, np.inf, np.inf], dtype=np.float64)
    maximum = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float64)

    sums = np.zeros(3, dtype=np.float64)
    point_count = 0

    sample = []
    seen = 0
    rng = np.random.default_rng(42)

    detected_columns = None
    has_rgb = False
    has_normals = False

    chunk = []

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.replace(",", ".").split()

            if len(parts) < 3:
                continue

            try:
                values = [float(x) for x in parts]
            except ValueError:
                # headers/comments
                continue

            if detected_columns is None:
                detected_columns = len(values)

                # Typical XYZRGB = X Y Z R G B
                if detected_columns >= 6:
                    rgb_candidate = np.asarray(values[3:6])

                    if np.all(rgb_candidate >= 0) and np.all(rgb_candidate <= 255):
                        has_rgb = True

                # XYZ + normals may also contain six+ values,
                # but we don't infer normals unless structure clearly indicates it.

            xyz = np.asarray(values[:3], dtype=np.float64)

            minimum = np.minimum(minimum, xyz)
            maximum = np.maximum(maximum, xyz)

            sums += xyz
            point_count += 1

            chunk.append(xyz)

            if len(chunk) >= 10_000:
                seen = reservoir_sample_update(
                    sample,
                    seen,
                    chunk,
                    sample_limit,
                    rng
                )
                chunk = []

    if chunk:
        seen = reservoir_sample_update(
            sample,
            seen,
            chunk,
            sample_limit,
            rng
        )

    centroid = sums / point_count

    return {
        "point_count": point_count,
        "min": minimum,
        "max": maximum,
        "centroid": centroid,
        "sample": np.asarray(sample),
        "has_rgb": has_rgb,
        "has_normals": has_normals,
        "property_count": detected_columns,
    }


# ------------------------------------------------------------
# PLY
# ------------------------------------------------------------

def analyze_ply(path, sample_limit=150_000):
    ply = PlyData.read(str(path))

    vertex = ply["vertex"].data
    names = vertex.dtype.names

    required = {"x", "y", "z"}

    if not required.issubset(names):
        raise ValueError(f"PLY without x/y/z properties: {names}")

    n = len(vertex)

    minimum = np.array([np.inf, np.inf, np.inf], dtype=np.float64)
    maximum = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float64)
    sums = np.zeros(3, dtype=np.float64)

    chunk_size = 250_000

    for start in range(0, n, chunk_size):
        stop = min(start + chunk_size, n)

        xyz = np.column_stack([
            vertex["x"][start:stop],
            vertex["y"][start:stop],
            vertex["z"][start:stop],
        ]).astype(np.float64)

        minimum = np.minimum(minimum, xyz.min(axis=0))
        maximum = np.maximum(maximum, xyz.max(axis=0))
        sums += xyz.sum(axis=0)

    centroid = sums / n

    rng = np.random.default_rng(42)

    sample_n = min(sample_limit, n)
    ids = rng.choice(n, size=sample_n, replace=False)

    sample = np.column_stack([
        vertex["x"][ids],
        vertex["y"][ids],
        vertex["z"][ids],
    ]).astype(np.float64)

    has_rgb = {"red", "green", "blue"}.issubset(names)
    has_normals = {"nx", "ny", "nz"}.issubset(names)

    face_count = 0

    if "face" in ply:
        face_count = len(ply["face"].data)

    return {
        "point_count": n,
        "min": minimum,
        "max": maximum,
        "centroid": centroid,
        "sample": sample,
        "has_rgb": has_rgb,
        "has_normals": has_normals,
        "properties": list(names),
        "face_count": face_count,
    }


# ------------------------------------------------------------
# Local geometry metrics
# ------------------------------------------------------------

def local_metrics(points):
    if len(points) < 10:
        return {}

    tree = cKDTree(points)

    # k=2: first neighbor is the point itself,
    # second is the nearest distinct neighbor.
    distances, _ = tree.query(points, k=2, workers=-1)

    nn = distances[:, 1]

    q1 = np.quantile(nn, 0.25)
    q3 = np.quantile(nn, 0.75)
    iqr = q3 - q1

    outlier_threshold = q3 + 1.5 * iqr
    outliers = nn > outlier_threshold

    return {
        "sample_points": int(len(points)),

        "nearest_neighbor": {
            "mean": float(np.mean(nn)),
            "median": float(np.median(nn)),
            "std": float(np.std(nn)),
            "min": float(np.min(nn)),
            "p05": float(np.quantile(nn, 0.05)),
            "p25": float(q1),
            "p75": float(q3),
            "p95": float(np.quantile(nn, 0.95)),
            "max": float(np.max(nn)),
        },

        "statistical_outlier_indicator": {
            "method": "NN > Q3 + 1.5*IQR",
            "threshold": float(outlier_threshold),
            "sample_outliers": int(outliers.sum()),
            "sample_outlier_percentage": float(outliers.mean() * 100),
        },
    }


# ------------------------------------------------------------
# One cloud
# ------------------------------------------------------------

def analyze_cloud(case, cfg):
    folder = cfg["folder"]
    path = find_cloud(folder, cfg["candidates"])

    if path is None:
        print(f"[SKIP] {case}: dense cloud not found")
        return

    print()
    print("=" * 75)
    print(case)
    print(path)
    print("=" * 75)

    suffix = path.suffix.lower()

    if suffix == ".xyz":
        base = analyze_xyz(path)

    elif suffix == ".ply":
        base = analyze_ply(path)

    else:
        raise ValueError(f"Unsupported format: {suffix}")

    minimum = base["min"]
    maximum = base["max"]

    ranges = maximum - minimum
    bbox_diagonal = float(np.linalg.norm(ranges))
    bbox_volume = float(np.prod(ranges))

    local = local_metrics(base["sample"])

    file_size = path.stat().st_size

    metadata = {
        "case": case,
        "artifact": "dense-point-cloud",
        "method": "photogrammetry",
        "source": cfg["source"],

        "generated_analysis_at": datetime.now().isoformat(),

        "file": {
            "name": path.name,
            "path": str(path),
            "format": suffix.lstrip("."),
            "size_bytes": file_size,
            "size_mb": file_size / (1024 ** 2),
            "sha256": sha256_file(path),
        },

        "geometry": {
            "point_count": int(base["point_count"]),

            "bounding_box": {
                "min": minimum.tolist(),
                "max": maximum.tolist(),
                "range": ranges.tolist(),
                "diagonal": bbox_diagonal,
                "volume": bbox_volume,
            },

            "centroid": base["centroid"].tolist(),
        },

        "attributes": {
            "has_rgb": bool(base["has_rgb"]),
            "has_normals": bool(base["has_normals"]),
        },

        "local_geometry_sample": local,

        "important_note": (
            "Nearest-neighbor and outlier metrics were calculated from a "
            "deterministic random sample, not from every point, to keep "
            "memory usage bounded. Full point count and bounding box use "
            "the complete cloud."
        ),
    }

    if suffix == ".ply":
        metadata["geometry"]["face_count"] = int(base.get("face_count", 0))
        metadata["attributes"]["ply_properties"] = base.get("properties", [])

    if suffix == ".xyz":
        metadata["attributes"]["detected_column_count"] = base.get(
            "property_count"
        )

    json_path = folder / "dense-cloud-metadata.json"
    log_path = folder / "dense-cloud-metrics.log"

    json_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    nn = local.get("nearest_neighbor", {})
    out = local.get("statistical_outlier_indicator", {})

    lines = [
        "DENSE POINT CLOUD ANALYSIS",
        "=" * 70,
        "",
        f"Case: {case}",
        f"Source: {cfg['source']}",
        "",
        "FILE",
        "----",
        f"Path: {path}",
        f"Format: {suffix}",
        f"Size bytes: {file_size}",
        f"Size MB: {file_size / (1024**2):.3f}",
        f"SHA256: {metadata['file']['sha256']}",
        "",
        "POINT CLOUD",
        "-----------",
        f"Points: {base['point_count']}",
        f"Has RGB: {base['has_rgb']}",
        f"Has normals: {base['has_normals']}",
        "",
        "BOUNDING BOX",
        "------------",
        f"X min: {minimum[0]:.9f}",
        f"X max: {maximum[0]:.9f}",
        f"X range: {ranges[0]:.9f}",
        f"Y min: {minimum[1]:.9f}",
        f"Y max: {maximum[1]:.9f}",
        f"Y range: {ranges[1]:.9f}",
        f"Z min: {minimum[2]:.9f}",
        f"Z max: {maximum[2]:.9f}",
        f"Z range: {ranges[2]:.9f}",
        f"BBox diagonal: {bbox_diagonal:.9f}",
        f"BBox volume: {bbox_volume:.9f}",
        "",
        "CENTROID",
        "--------",
        f"X: {base['centroid'][0]:.9f}",
        f"Y: {base['centroid'][1]:.9f}",
        f"Z: {base['centroid'][2]:.9f}",
        "",
        "LOCAL POINT DISTRIBUTION",
        "------------------------",
        f"Sample size: {local.get('sample_points', 0)}",
        f"NN mean: {nn.get('mean', float('nan')):.9f}",
        f"NN median: {nn.get('median', float('nan')):.9f}",
        f"NN std: {nn.get('std', float('nan')):.9f}",
        f"NN P05: {nn.get('p05', float('nan')):.9f}",
        f"NN P25: {nn.get('p25', float('nan')):.9f}",
        f"NN P75: {nn.get('p75', float('nan')):.9f}",
        f"NN P95: {nn.get('p95', float('nan')):.9f}",
        "",
        "OUTLIER INDICATOR",
        "-----------------",
        f"Method: {out.get('method', 'n/a')}",
        f"Threshold: {out.get('threshold', float('nan')):.9f}",
        f"Sample outliers: {out.get('sample_outliers', 0)}",
        f"Sample outlier %: {out.get('sample_outlier_percentage', float('nan')):.4f}",
        "",
        "METHODOLOGICAL NOTE",
        "-------------------",
        "Point count, centroid and bounding box are computed from the full cloud.",
        "Nearest-neighbor statistics and the outlier indicator are computed from",
        "a deterministic random sample of at most 150,000 points.",
        "",
        "No points were modified or deleted during this analysis.",
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] Points: {base['point_count']:,}")
    print(f"[OK] Log:  {log_path}")
    print(f"[OK] JSON: {json_path}")


for case, cfg in CLOUDS.items():
    try:
        analyze_cloud(case, cfg)

    except Exception as e:
        print(f"[ERROR] {case}: {e}")