"""Turn single captioned images in source_images/ into clean 16:9 panels.
Drops the caption band at the top, crops to 16:9 around a horizontal focus point.
Usage: python prep_singles.py source_images panels"""
import sys, os, glob, json
import numpy as np
from PIL import Image, ImageFilter
W, H = 2560, 1440
TOP_CUT = 0.30                  # caption band ("17. Entering the Forest...")
FOCUS = {"20": 0.78, "30": 0.68, "17": 0.4, "29": 0.3, "22": 0.55}   # 0=left, 1=right; default 0.5

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, "[1-3][0-9]-*.png"))):
    n = os.path.basename(f)[:2]
    if int(n) < 13: continue          # Act 1 comes from the storyboard sheet
    im = Image.open(f).convert("RGB"); w, h = im.size
    top = int(h * {"32": 0.50, "29": 0.36}.get(n, 0.34))
    a = np.asarray(im.convert("L")).astype(float)
    while top < h - 60 and (a[top].mean() > 225 or a[top].std() < 12): top += 1   # skip leftover white gutter
    top += 9
    bot = h
    for y in range(h - 1, int(h * 0.7), -1):          # white gutter line from the sheet near the bottom
        if a[y].mean() > 215: bot = y
    bot -= 4
    ch = bot - top; cw = int(ch * 16 / 9)
    fx = FOCUS.get(n, 0.5); x0 = min(max(int(w * fx - cw / 2), 0), w - cw)
    p = im.crop((x0, top, x0 + cw, bot)).resize((W, H), Image.LANCZOS)
    p = p.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    p.save(os.path.join(out, f"img_{n}.jpg"), quality=92)
    print("img_" + n)
