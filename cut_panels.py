"""Cut storyboard sheets into individual 16:9 shots.
Usage: python cut_panels.py source_sheets/ panels/
Finds white gutters, drops the caption strip at the top of each panel, crops to 16:9, upscales."""
import sys, os, glob
import numpy as np
from PIL import Image, ImageFilter

W, H = 2560, 1440          # working size (renderer zooms inside this)
CAPTION_CUT = 0.19         # fraction of panel height removed from top (caption band)

def runs(mask):
    """Return [start,end) spans where mask is False (i.e. panel content)."""
    spans, s = [], None
    for i, m in enumerate(list(mask) + [True]):
        if not m and s is None: s = i
        if m and s is not None:
            if i - s > 40: spans.append((s, i))
            s = None
    return spans

def cut(sheet_path, out_dir, prefix):
    img = Image.open(sheet_path).convert("RGB")
    a = np.asarray(img.convert("L")).astype(float)
    cols = runs(a.mean(0) > 235)
    rows = runs(a.mean(1) > 235)
    n = 0
    for r0, r1 in rows:
        for c0, c1 in cols:
            n += 1
            ph = r1 - r0
            top = r0 + int(ph * CAPTION_CUT)
            h = r1 - top
            w = c1 - c0
            # crop to 16:9 inside the remaining area
            if w / h > 16 / 9:
                nw = int(h * 16 / 9); x0 = c0 + (w - nw) // 2
                box = (x0, top, x0 + nw, r1)
            else:
                nh = int(w * 9 / 16); box = (c0, r1 - nh, c1, r1)
            p = img.crop(box).resize((W, H), Image.LANCZOS)
            p = p.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
            p.save(os.path.join(out_dir, f"{prefix}_p{n:02d}.jpg"), quality=92)
    return n

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(src, "*.png"))):
        prefix = os.path.splitext(os.path.basename(f))[0].replace("smallpockets_", "")
        print(f, cut(f, out, prefix), "panels")
