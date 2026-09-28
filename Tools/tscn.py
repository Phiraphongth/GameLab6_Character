"""Tiny helper for writing Godot 4 .tscn files from Python (used by gen_scenes.py)."""
import json
import math


def q(text):
    """Quoted Godot string."""
    return json.dumps(text, ensure_ascii=False)


def vec3(x, y, z):
    return f"Vector3({x:g}, {y:g}, {z:g})"


def color(r, g, b, a=1.0):
    return f"Color({r:g}, {g:g}, {b:g}, {a:g})"


def xf(pos=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    """Transform3D from position, euler degrees (Godot YXZ order) and scale."""
    rx, ry, rz = (math.radians(a) for a in rot)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

    m = mul(mul(Ry, Rx), Rz)
    s = scale if isinstance(scale, (tuple, list)) else (scale, scale, scale)
    m = [[m[i][j] * s[j] for j in range(3)] for i in range(3)]
    vals = [m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2], *pos]
    return "Transform3D(" + ", ".join(f"{0.0 if abs(v) < 1e-9 else round(v, 6):g}" for v in vals) + ")"


def _fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{v:g}" if isinstance(v, float) else str(v)
    return v  # raw Godot expression


def _key(k):
    for group in ("colors", "font_sizes", "fonts", "constants", "styles"):
        prefix = f"theme_override_{group}_"
        if k.startswith(prefix):
            return f"theme_override_{group}/" + k[len(prefix):]
    return k


class Scene:
    def __init__(self, root_name, root_type=None, instance=None, script=None, groups=None, **props):
        self.ext = []
        self.subs = []
        self.nodes = []
        self.conns = []
        self._ids = {}
        root_props = dict(props)
        if script:
            root_props = {"script": self.res(script), **root_props}
        self.node(root_name, root_type, None, instance=instance, groups=groups, **root_props)

    def res(self, path, kind=None):
        if path not in self._ids:
            if kind is None:
                kind = {"gd": "Script", "tscn": "PackedScene", "glb": "PackedScene", "png": "Texture2D",
                        "ogg": "AudioStream", "res": "Resource", "tres": "Resource",
                        "gdshader": "Shader"}[path.rsplit(".", 1)[1]]
            eid = f"{len(self.ext) + 1}_r"
            self._ids[path] = eid
            self.ext.append(f'[ext_resource type="{kind}" path="{path}" id="{eid}"]')
        return f'ExtResource("{self._ids[path]}")'

    def sub(self, res_type, **props):
        sid = f"{res_type}_{len(self.subs) + 1}"
        body = "\n".join(f"{k} = {_fmt(v)}" for k, v in props.items())
        self.subs.append(f'[sub_resource type="{res_type}" id="{sid}"]\n{body}')
        return f'SubResource("{sid}")'

    def node(self, name, node_type=None, parent=".", instance=None, groups=None, **props):
        head = f'[node name="{name}"'
        if node_type and not instance:
            head += f' type="{node_type}"'
        if parent is not None:
            head += f' parent="{parent}"'
        if instance:
            head += f" instance={self.res(instance)}"
        if groups:
            head += " groups=[" + ", ".join(q(g) for g in groups) + "]"
        head += "]"
        body = "\n".join(f"{_key(k)} = {_fmt(v)}" for k, v in props.items())
        self.nodes.append(head + ("\n" + body if body else ""))
        return name if parent in (None, ".") else f"{parent}/{name}"

    def connect(self, signal, src, dst, method):
        self.conns.append(f'[connection signal="{signal}" from="{src}" to="{dst}" method="{method}"]')

    def write(self, path):
        steps = len(self.ext) + len(self.subs) + 1
        parts = [f"[gd_scene load_steps={steps} format=3]", "\n".join(self.ext)]
        parts += self.subs + self.nodes + self.conns
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(p for p in parts if p) + "\n")
