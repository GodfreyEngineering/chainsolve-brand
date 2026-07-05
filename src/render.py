#!/usr/bin/env python3
"""Render every HTML target in the manifest to PNG via Chrome headless."""
import json, subprocess, sys, pathlib, concurrent.futures as cf

ROOT = pathlib.Path(__file__).parent
targets = json.loads((ROOT/"render_manifest.json").read_text())
only = sys.argv[1] if len(sys.argv) > 1 else None

def render(t):
    html, png, w, h, scale = t
    if only and only not in html:
        return None
    cmd = [
        "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--disable-lcd-text",
        f"--force-device-scale-factor={scale}",
        "--default-background-color=00000000",
        f"--window-size={w},{h}",
        "--virtual-time-budget=4000",
        f"--screenshot={png}",
        f"file://{html}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    ok = pathlib.Path(png).exists()
    return (png.split('assets/')[-1], w*scale, h*scale, ok)

todo = [t for t in targets if not only or only in t[0]]
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(render, todo):
        if res:
            print(f"{'OK ' if res[3] else 'ERR'} {res[0]:<44} {res[1]}x{res[2]}")
