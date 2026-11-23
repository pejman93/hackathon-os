"""Load the brand from brand/brand.json, with optional overrides for one event.

    import brand
    B = brand.load()                          # the default brand
    B = brand.load("my-event.json")           # with that file's "brand" block on top
    B.rgb("accent")          -> (126, 152, 255)
    B.font("display", 800)   -> path to the .ttf
    B.logo("white")          -> path to the .png

An override uses the same structure as brand.json, for example:
    {"brand": {"colours": {"accent": {"hex": "#3FB68B"}}}}
Only the keys given change.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brand"
BRAND_FILE = BRAND_DIR / "brand.json"


def merge(base, over):
    """Deep-merge `over` onto `base`. Keys starting with an underscore are notes and are skipped."""
    out = dict(base)
    for key, value in over.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out


class Brand:
    def __init__(self, data):
        self.data = data

    def hex(self, name):
        return self.data["colours"][name]["hex"]

    def rgb(self, name):
        h = self.hex(name).lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def font(self, role, weight):
        path = BRAND_DIR / self.data["fonts"][role]["files"][str(weight)]
        if not path.exists():
            raise FileNotFoundError(f"brand.json names a font file that is missing: {path}")
        return path

    def logo(self, name):
        path = BRAND_DIR / self.data["logos"][name]["file"]
        if not path.exists():
            raise FileNotFoundError(f"brand.json names a logo file that is missing: {path}")
        return path


def load(config=None):
    """The brand, with the "brand" block of the JSON file `config` applied on top, if given."""
    data = json.loads(BRAND_FILE.read_text(encoding="utf-8"))
    if config:
        over = json.loads(pathlib.Path(config).read_text(encoding="utf-8")).get("brand") or {}
        data = merge(data, over)
    return Brand(data)
