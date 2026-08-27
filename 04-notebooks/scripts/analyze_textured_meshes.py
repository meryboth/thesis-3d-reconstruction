from pathlib import Path
import hashlib
import json
from datetime import datetime

import numpy as np
from PIL import Image


ROOT = Path(r"C:\nerfstudio_work\thesis")

MESHES = {
    "01-paraguas-vicentelopez": {
        "root": ROOT / "01-paraguas-vicentelopez",
    },
    "02-templete-central": {
        "root": ROOT / "02-templete-central",
    },
    "03-panteon-asociacion-catalana": {
        "root": ROOT / "03-panteon-asociacion-catalana",
    },
}


def sha256_file(path, chunk_size=8 * 1024 * 1024):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def find_textured_obj(root):
    candidates = list(root.rglob("textured-mesh.obj"))

    if not candidates:
        candidates = [
            p for p in root.rglob("*.obj")
            if "textured" in p.name.lower()
        ]

    if not candidates:
        return None

    # Prefer paths inside resultados-finales
    candidates.sort(
        key=lambda p: (
            "02-resultados-finales" not in str(p),
            len(str(p))
        )
    )

    return candidates[0]


def parse_mtl(mtl_path):
    materials = set()
    textures = []

    if not mtl_path.exists():
        return materials, textures

    with mtl_path.open(
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for raw in f:
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("newmtl "):
                materials.add(line.split(maxsplit=1)[1])

            # Diffuse/albedo textures + other map types
            prefixes = (
                "map_Kd ",
                "map_Ka ",
                "map_Ks ",
                "map_Bump ",
                "map_bump ",
                "bump ",
                "disp ",
                "decal ",
            )

            for prefix in prefixes:
                if line.startswith(prefix):
                    tex_name = line[len(prefix):].strip()

                    # Common MTL options can precede filename.
                    # Use final token as a pragmatic fallback.
                    tex_name = tex_name.split()[-1]

                    textures.append(tex_name)
                    break

    return materials, textures


def analyze_obj(path):
    vertex_count = 0
    normal_count = 0
    uv_count = 0
    face_count = 0
    triangle_count = 0

    minimum = np.array(
        [np.inf, np.inf, np.inf],
        dtype=np.float64
    )
    maximum = np.array(
        [-np.inf, -np.inf, -np.inf],
        dtype=np.float64
    )
    sums = np.zeros(3, dtype=np.float64)

    mtllibs = []
    used_materials = set()

    with path.open(
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for raw in f:
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("v "):
                parts = line.split()

                if len(parts) >= 4:
                    try:
                        xyz = np.asarray(
                            [
                                float(parts[1]),
                                float(parts[2]),
                                float(parts[3]),
                            ],
                            dtype=np.float64
                        )
                    except ValueError:
                        continue

                    minimum = np.minimum(minimum, xyz)
                    maximum = np.maximum(maximum, xyz)
                    sums += xyz
                    vertex_count += 1

            elif line.startswith("vn "):
                normal_count += 1

            elif line.startswith("vt "):
                uv_count += 1

            elif line.startswith("f "):
                parts = line.split()[1:]
                n = len(parts)

                if n >= 3:
                    face_count += 1

                    # Polygon with n vertices triangulates into n-2 triangles.
                    triangle_count += n - 2

            elif line.startswith("mtllib "):
                mtllibs.append(
                    line.split(maxsplit=1)[1].strip()
                )

            elif line.startswith("usemtl "):
                used_materials.add(
                    line.split(maxsplit=1)[1].strip()
                )

    centroid = (
        sums / vertex_count
        if vertex_count > 0
        else np.zeros(3)
    )

    ranges = maximum - minimum
    diagonal = float(np.linalg.norm(ranges))
    bbox_volume = float(np.prod(ranges))

    return {
        "vertex_count": vertex_count,
        "normal_count": normal_count,
        "uv_count": uv_count,
        "face_count": face_count,
        "triangle_count": triangle_count,
        "min": minimum,
        "max": maximum,
        "range": ranges,
        "diagonal": diagonal,
        "bbox_volume": bbox_volume,
        "centroid": centroid,
        "mtllibs": mtllibs,
        "used_materials": sorted(used_materials),
    }


def analyze_textures(obj_path, mtllibs):
    texture_records = []
    all_materials = set()

    for mtl_name in mtllibs:
        mtl_path = obj_path.parent / mtl_name

        materials, texture_names = parse_mtl(mtl_path)
        all_materials.update(materials)

        for tex_name in texture_names:
            tex_path = obj_path.parent / tex_name

            rec = {
                "referenced_from": mtl_name,
                "name": tex_name,
                "path": str(tex_path),
                "exists": tex_path.exists(),
            }

            if tex_path.exists():
                rec["size_bytes"] = tex_path.stat().st_size
                rec["size_mb"] = (
                    tex_path.stat().st_size / (1024 ** 2)
                )
                rec["sha256"] = sha256_file(tex_path)

                try:
                    with Image.open(tex_path) as im:
                        rec["width"] = im.width
                        rec["height"] = im.height
                        rec["mode"] = im.mode
                except Exception as exc:
                    rec["image_read_error"] = str(exc)

            texture_records.append(rec)

    return sorted(all_materials), texture_records


def analyze_case(case, cfg):
    obj_path = find_textured_obj(cfg["root"])

    if obj_path is None:
        print(f"[SKIP] {case}: no textured OBJ found")
        return

    print()
    print("=" * 80)
    print(case)
    print(obj_path)
    print("=" * 80)

    mesh = analyze_obj(obj_path)

    mtl_materials, textures = analyze_textures(
        obj_path,
        mesh["mtllibs"]
    )

    total_texture_bytes = sum(
        x.get("size_bytes", 0)
        for x in textures
        if x.get("exists")
    )

    existing_texture_count = sum(
        1
        for x in textures
        if x.get("exists")
    )

    metadata = {
        "case": case,

        "artifact": {
            "type": "textured-mesh",
            "format": "obj",
        },

        "analysis": {
            "generated_at": datetime.now().isoformat(),
        },

        "file": {
            "name": obj_path.name,
            "path": str(obj_path),
            "size_bytes": obj_path.stat().st_size,
            "size_mb": obj_path.stat().st_size / (1024 ** 2),
            "sha256": sha256_file(obj_path),
        },

        "geometry": {
            "vertices": mesh["vertex_count"],
            "faces": mesh["face_count"],
            "triangles": mesh["triangle_count"],

            "bounding_box": {
                "min": mesh["min"].tolist(),
                "max": mesh["max"].tolist(),
                "range": mesh["range"].tolist(),
                "diagonal": mesh["diagonal"],
                "volume": mesh["bbox_volume"],
            },

            "centroid": mesh["centroid"].tolist(),
        },

        "attributes": {
            "normal_records": mesh["normal_count"],
            "uv_records": mesh["uv_count"],
            "has_normals": mesh["normal_count"] > 0,
            "has_uvs": mesh["uv_count"] > 0,
        },

        "materials": {
            "mtl_files": mesh["mtllibs"],
            "used_materials": mesh["used_materials"],
            "materials_defined_in_mtl": mtl_materials,
        },

        "textures": {
            "referenced_count": len(textures),
            "existing_count": existing_texture_count,
            "total_size_bytes": total_texture_bytes,
            "total_size_mb": total_texture_bytes / (1024 ** 2),
            "files": textures,
        },

        "methodological_note": (
            "The OBJ was analyzed without modifying geometry or texture files. "
            "Triangle count is derived from OBJ faces assuming standard fan "
            "triangulation for polygons containing more than three vertices."
        ),
    }

    folder = obj_path.parent

    json_path = folder / "textured-mesh-metadata.json"
    log_path = folder / "textured-mesh-metrics.log"

    json_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    lines = [
        "TEXTURED MESH ANALYSIS",
        "=" * 72,
        "",
        f"Case: {case}",
        "",
        "FILE",
        "----",
        f"Path: {obj_path}",
        f"Format: OBJ",
        f"Size bytes: {obj_path.stat().st_size}",
        f"Size MB: {obj_path.stat().st_size / (1024 ** 2):.3f}",
        f"SHA256: {metadata['file']['sha256']}",
        "",
        "GEOMETRY",
        "--------",
        f"Vertices: {mesh['vertex_count']}",
        f"Faces: {mesh['face_count']}",
        f"Triangles: {mesh['triangle_count']}",
        "",
        "ATTRIBUTES",
        "----------",
        f"Normal records: {mesh['normal_count']}",
        f"UV records: {mesh['uv_count']}",
        f"Has normals: {mesh['normal_count'] > 0}",
        f"Has UVs: {mesh['uv_count'] > 0}",
        "",
        "BOUNDING BOX",
        "------------",
        f"X min: {mesh['min'][0]:.9f}",
        f"X max: {mesh['max'][0]:.9f}",
        f"X range: {mesh['range'][0]:.9f}",
        f"Y min: {mesh['min'][1]:.9f}",
        f"Y max: {mesh['max'][1]:.9f}",
        f"Y range: {mesh['range'][1]:.9f}",
        f"Z min: {mesh['min'][2]:.9f}",
        f"Z max: {mesh['max'][2]:.9f}",
        f"Z range: {mesh['range'][2]:.9f}",
        f"BBox diagonal: {mesh['diagonal']:.9f}",
        f"BBox volume: {mesh['bbox_volume']:.9f}",
        "",
        "CENTROID",
        "--------",
        f"X: {mesh['centroid'][0]:.9f}",
        f"Y: {mesh['centroid'][1]:.9f}",
        f"Z: {mesh['centroid'][2]:.9f}",
        "",
        "MATERIALS",
        "---------",
        f"MTL references: {len(mesh['mtllibs'])}",
        f"Used materials: {len(mesh['used_materials'])}",
        f"Defined materials: {len(mtl_materials)}",
        "",
        "TEXTURES",
        "--------",
        f"Referenced textures: {len(textures)}",
        f"Existing textures: {existing_texture_count}",
        f"Total texture size MB: {total_texture_bytes / (1024 ** 2):.3f}",
    ]

    for i, tex in enumerate(textures, start=1):
        lines.extend([
            "",
            f"Texture {i}: {tex['name']}",
            f"  Exists: {tex['exists']}",
        ])

        if tex.get("exists"):
            lines.extend([
                f"  Size MB: {tex.get('size_mb', 0):.3f}",
                f"  Resolution: {tex.get('width', 'n/a')} x {tex.get('height', 'n/a')}",
                f"  Mode: {tex.get('mode', 'n/a')}",
                f"  SHA256: {tex.get('sha256', 'n/a')}",
            ])

    lines.extend([
        "",
        "METHODOLOGICAL NOTE",
        "-------------------",
        "The OBJ, MTL and texture files were analyzed without modification.",
        (
            "Triangle count is derived from OBJ face definitions; polygons "
            "with more than three vertices are counted as n-2 triangles."
        ),
    ])

    log_path.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"[OK] Vertices:  {mesh['vertex_count']:,}")
    print(f"[OK] Triangles: {mesh['triangle_count']:,}")
    print(f"[OK] Textures:  {existing_texture_count}")
    print(f"[OK] Log:       {log_path}")
    print(f"[OK] JSON:      {json_path}")


for case, cfg in MESHES.items():
    try:
        analyze_case(case, cfg)

    except Exception as exc:
        print(f"[ERROR] {case}: {exc}")