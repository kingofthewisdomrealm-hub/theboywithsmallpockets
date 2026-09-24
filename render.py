"""Render the story video from timeline.json + panels/ + audio.
Usage: python render.py [--preview]   (preview = 640x360, fast)"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = "--preview" in sys.argv
OW, OH = (640, 360) if PREVIEW else (1920, 1080)
FPS = 30
XF = 0.6  # crossfade seconds

def font(sz):
    for p in ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def placeholder(path, n, title, bg=None):
    im = Image.open(bg).convert("RGB").resize((2560, 1440)).filter(ImageFilter.GaussianBlur(28)) if bg else Image.new("RGB", (2560, 1440), (20, 16, 12))
    im = Image.blend(im, Image.new("RGB", im.size, (10, 8, 6)), 0.55)
    d = ImageDraw.Draw(im)
    for txt, f, y in [(f"SCENE {n}", font(70), 560), (title, font(130), 660), ("image coming", font(56), 860)]:
        w = d.textlength(txt, font=f); d.text(((2560 - w) / 2, y), txt, font=f, fill=(240, 214, 150))
    im.save(path, quality=92)

def main():
    tl = json.load(open(os.path.join(ROOT, "timeline.json")))
    audio = os.path.join(ROOT, tl["audio"])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]))
    tmp = tempfile.mkdtemp()
    shots, last_img = [], None
    sc = tl["scenes"]
    for i, s in enumerate(sc):
        end = sc[i + 1]["start"] if i + 1 < len(sc) else dur
        per = (end - s["start"]) / len(s["shots"])
        for j, name in enumerate(s["shots"]):
            p = next((os.path.join(ROOT, "panels", name + e) for e in (".jpg", ".png") if os.path.exists(os.path.join(ROOT, "panels", name + e))), None)
            if p: last_img = p
            else:
                p = os.path.join(tmp, f"ph_{s['n']}_{j}.jpg"); placeholder(p, s["n"], s["title"], last_img)
            shots.append((p, per))
    # one Ken Burns clip per shot (alternating zoom in / out), each padded by XF for the crossfade
    from concurrent.futures import ThreadPoolExecutor
    def make(args):
        k, (img, d) = args
        frames = int((d + XF) * FPS)
        z = f"1+0.12*on/{frames}" if k % 2 == 0 else f"1.12-0.12*on/{frames}"
        out = os.path.join(tmp, f"c{k:03d}.mp4")
        vf = (f"scale={OW*2}:{OH*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={OW}x{OH}:fps={FPS},format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", img, "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", out], check=True)
        return (out, d)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        clips = list(ex.map(make, enumerate(shots)))
    # chain crossfades
    inputs, fc, prev, t = [], [], "0:v", 0.0
    for k, (c, d) in enumerate(clips):
        inputs += ["-i", c]
        if k == 0: t = d; continue
        lab = f"v{k}"
        fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={t - XF/2:.3f}[{lab}]")
        prev, t = lab, t + d
    outname = os.path.join(ROOT, "output", "small_pockets_preview.mp4" if PREVIEW else "small_pockets.mp4")
    os.makedirs(os.path.dirname(outname), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-i", audio, "-filter_complex", ";".join(fc) or "null",
           "-map", f"[{prev}]" if fc else "0:v", "-map", f"{len(clips)}:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
           "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.2f}", "-movflags", "+faststart", outname]
    subprocess.run(cmd, check=True)
    print("wrote", outname)

if __name__ == "__main__":
    main()
