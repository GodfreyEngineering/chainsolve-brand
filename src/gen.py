#!/usr/bin/env python3
"""ChainSolve brand asset generator.

Single source of truth = the transparent *masked* weave mark. Placed on a
background matching its notch colour it is pixel-identical to the spec's
overpaint SVG (2.1), but it also works transparent on any surface.
Geometry, colours, and type follow the ChainSolve Brand & Design System v1.0.
"""
import os, json, pathlib

ROOT = pathlib.Path(__file__).parent
A = ROOT / "assets"

# --- palette (from spec §3 / appendix) -------------------------------------
TERRACOTTA = "#E06A4E"   # --tc-500 / accent
INK        = "#1C1815"   # --n-900 / ink
WHITE      = "#FFFFFF"
PAPER      = "#FAF4F0"   # --n-50 / light bg
DARK       = "#14110F"   # --bg dark (product default)
SURFACE_D  = "#1C1815"

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Montserrat:wght@600;700;800&"
         "family=IBM+Plex+Sans:wght@400;500;600;700&"
         "family=IBM+Plex+Mono:wght@400;500;600&display=swap")

# --- the mark --------------------------------------------------------------
def mark(a_color, b_color):
    """Exact §2.1 weave, transparent via masks. a=Ring A (top-left), b=Ring B."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%" role="img" aria-label="ChainSolve">
  <defs>
    <mask id="mA" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">
      <rect width="100" height="100" fill="#fff"/>
      <!-- Ring B carves the weave notch in Ring A at both crossings -->
      <rect x="38" y="38" width="54" height="54" rx="16" fill="none" stroke="#000" stroke-width="19"/>
    </mask>
    <mask id="mB" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">
      <rect width="100" height="100" fill="#fff"/>
      <!-- vertical halo carves Ring B where A's right edge passes over (62,38) -->
      <line x1="62" y1="28" x2="62" y2="48" stroke="#000" stroke-width="19"/>
    </mask>
  </defs>
  <!-- Ring A (top-left) -->
  <rect x="8" y="8" width="54" height="54" rx="16" fill="none" stroke="{a_color}" stroke-width="12" mask="url(#mA)"/>
  <!-- Ring B (bottom-right) -->
  <rect x="38" y="38" width="54" height="54" rx="16" fill="none" stroke="{b_color}" stroke-width="12" mask="url(#mB)"/>
  <!-- Redraw A's right edge OVER B to complete the alternating weave -->
  <line x1="62" y1="30" x2="62" y2="46" stroke="{a_color}" stroke-width="12" stroke-linecap="butt"/>
</svg>'''

# variant name -> (Ring A colour, Ring B colour)
VARIANTS = {
    "primary":       (TERRACOTTA, INK),    # two-colour, for light surfaces
    "reversed":      (TERRACOTTA, WHITE),  # two-colour, for dark surfaces
    "mono-ink":      (INK, INK),           # single colour on light
    "mono-reversed": (WHITE, WHITE),       # single colour on dark
}

def svg_file(path, inner, w=100, h=100, vb="0 0 100 100", bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">'
           f'{bgrect}{inner}</svg>')
    path.write_text(doc)

# standalone mark SVGs (transparent)
for name, (a, b) in VARIANTS.items():
    (A/"logo"/f"mark-{name}.svg").write_text(mark(a, b))

# --- HTML scaffolding ------------------------------------------------------
def page(body, w, h, bg="transparent", extra_css=""):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<style>
@import url('{FONTS}');
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;background:{bg};overflow:hidden}}
.mont{{font-family:'Montserrat',system-ui,sans-serif}}
.plex{{font-family:'IBM Plex Sans',system-ui,sans-serif}}
.mono{{font-family:'IBM Plex Mono',ui-monospace,monospace}}
{extra_css}
</style></head><body>{body}</body></html>'''

def wordmark(color, size):
    # Montserrat 700, letter-spacing -0.02em, cap-height ~0.68 x mark height.
    return (f'<span class="mont" style="font-weight:700;letter-spacing:-0.02em;'
            f'font-size:{size}px;color:{color};line-height:1;white-space:nowrap">ChainSolve</span>')

def inline_mark(name, px):
    a, b = VARIANTS[name]
    return f'<div style="width:{px}px;height:{px}px;flex:0 0 auto">{mark(a,b)}</div>'

RENDER = []  # (html_path, png_path, W, H, scale)
def render_html(rel, html, w, h, scale=2):
    p = A/rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html)
    RENDER.append((str(p), str(p.with_suffix(".png")), w, h, scale))

# --- lockups (§2.2) --------------------------------------------------------
# Horizontal: mark height H, gap 0.29H, wordmark cap-height 0.68H.
def lockup_h(mark_variant, word_color, bg, name):
    H = 220
    gap = round(0.29*H)          # 64
    font = round(H*0.96)         # cap-height ~0.68H for Montserrat
    pad = round(0.25*H)          # clearspace = 0.25 x mark height
    body = (f'<div style="height:{H+2*pad}px;display:flex;align-items:center;'
            f'justify-content:center;gap:{gap}px;padding:0 {pad}px">'
            f'{inline_mark(mark_variant, H)}'
            f'<span class="mont" style="font-weight:700;letter-spacing:-0.02em;'
            f'font-size:{font}px;color:{word_color};line-height:0.7;'
            f'white-space:nowrap;transform:translateY(-0.04em)">ChainSolve</span></div>')
    # width auto -> use a wide canvas then it will be trimmed on export by Canva; keep fixed
    W = pad*2 + H + gap + round(font*5.55)  # approx wordmark width
    render_html(f"logo/lockup-horizontal-{name}.html", page(body, W, H+2*pad, bg), W, H+2*pad)

def lockup_stacked(mark_variant, word_color, bg, name):
    H = 240
    gap = round(0.19*H)
    font = round(H*0.62)
    pad = round(0.25*H)
    body = (f'<div style="display:flex;flex-direction:column;align-items:center;'
            f'justify-content:center;gap:{gap}px;padding:{pad}px">'
            f'{inline_mark(mark_variant, H)}'
            f'<span class="mont" style="font-weight:700;letter-spacing:-0.02em;'
            f'font-size:{font}px;color:{word_color};line-height:1;white-space:nowrap">ChainSolve</span></div>')
    W = pad*2 + round(font*5.55)
    Ht = pad*2 + H + gap + round(font*1.2)
    render_html(f"logo/lockup-stacked-{name}.html", page(body, W, Ht, bg), W, Ht)

lockup_h("primary",  INK,   PAPER, "light")
lockup_h("reversed", WHITE, DARK,  "dark")
lockup_stacked("primary",  INK,   PAPER, "light")
lockup_stacked("reversed", WHITE, DARK,  "dark")

# --- app icons -------------------------------------------------------------
def app_icon(rel, mark_variant, tile_bg, w=1024, radius_pct=22.5, pad_pct=0.20):
    r = round(w*radius_pct/100)
    inner = round(w*(1-2*pad_pct))
    off = round(w*pad_pct)
    body = (f'<div style="width:{w}px;height:{w}px;background:{tile_bg};'
            f'border-radius:{r}px;position:relative">'
            f'<div style="position:absolute;left:{off}px;top:{off}px;'
            f'width:{inner}px;height:{inner}px">{mark(*VARIANTS[mark_variant])}</div></div>')
    render_html(rel, page(body, w, w, "transparent"), w, w, scale=1)

app_icon("icon/app-icon-dark.html",  "reversed", DARK,  1024)
app_icon("icon/app-icon-light.html", "primary",  PAPER, 1024)
app_icon("icon/app-icon-terracotta.html", "mono-reversed", TERRACOTTA, 1024)

# --- favicons (transparent mark, plus maskable dark tile) ------------------
for sz in (512, 256, 192, 180, 32, 16):
    body = f'<div style="width:{sz}px;height:{sz}px">{mark(*VARIANTS["primary"])}</div>'
    render_html(f"favicon/favicon-{sz}.html", page(body, sz, sz, "transparent"), sz, sz, scale=1)
# maskable (safe-zone padded) dark tile for PWA
for sz in (512, 192):
    app_icon(f"favicon/maskable-{sz}.html", "reversed", DARK, sz, radius_pct=0, pad_pct=0.16)

# --- standalone marks at hi-res (transparent) ------------------------------
for name in VARIANTS:
    body = f'<div style="width:1024px;height:1024px">{mark(*VARIANTS[name])}</div>'
    render_html(f"logo/mark-{name}.html", page(body, 1024, 1024, "transparent"), 1024, 1024, scale=1)

# --- social ----------------------------------------------------------------
# square avatar (dark)
body = (f'<div style="width:1024px;height:1024px;background:{DARK};'
        f'display:flex;align-items:center;justify-content:center">'
        f'<div style="width:560px;height:560px">{mark(*VARIANTS["reversed"])}</div></div>')
render_html("social/avatar-dark-1024.html", page(body, 1024, 1024, DARK), 1024, 1024, scale=1)

# OG banner 1200x630 with tagline
def banner(rel, W, Ht, bg, word_color, mark_variant, tagline_color, mh):
    gap = round(mh*0.29)
    font = round(mh*0.96)
    body = (f'<div style="width:{W}px;height:{Ht}px;background:{bg};position:relative;'
            f'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{round(Ht*0.06)}px">'
            f'<div style="display:flex;align-items:center;gap:{gap}px">'
            f'{inline_mark(mark_variant, mh)}'
            f'<span class="mont" style="font-weight:700;letter-spacing:-0.02em;'
            f'font-size:{font}px;color:{word_color};line-height:0.7;transform:translateY(-0.04em)">ChainSolve</span></div>'
            f'<span class="mono" style="font-size:{round(Ht*0.045)}px;color:{tagline_color};'
            f'letter-spacing:0.02em">Simulate before you build.</span></div>')
    render_html(rel, page(body, W, Ht, bg), W, Ht, scale=1)

banner("social/og-1200x630.html", 1200, 630, DARK, WHITE, "reversed", "#C9BAB0", 150)
banner("social/linkedin-1584x396.html", 1584, 396, DARK, WHITE, "reversed", "#C9BAB0", 132)

# --- brand guidelines document (multi-page, for Canva import) --------------
TC_RAMP = [("50","#FBEEE9"),("100","#F6D9CF"),("200","#EFB8A6"),("300","#E8977C"),
           ("400","#E3785E"),("500","#E06A4E"),("600","#C8543A"),("700","#A5412C"),
           ("800","#7E3222"),("900","#55231A")]
WARM_RAMP = [("0","#FFFFFF"),("50","#FAF4F0"),("100","#F2E9E3"),("200","#E3D7CE"),
             ("300","#C9BAB0"),("400","#A2938A"),("500","#7A6E66"),("600","#574E48"),
             ("700","#3B342F"),("800","#2A2420"),("900","#1C1815"),("950","#14110F")]
FUNCTIONAL = [("Success","#3E9E6E","converged, valid"),("Warning","#E0A33D","tolerance, caution"),
              ("Danger","#D6453C","diverged, error"),("Info","#4CB6C6","neutral notice")]
WORKBENCH = [("Automotive","#E0533A"),("Structural","#C77E52"),("Aerospace","#4CB6C6"),
             ("Finance","#3E9E6E"),("NN / ML","#8B6CD9")]

def swatch_row(ramp, dark_text_from=4):
    cells = ""
    for i,(step,hex_) in enumerate(ramp):
        tc = INK if i < dark_text_from else PAPER
        cells += (f'<div style="flex:1;min-width:0"><div style="height:64px;background:{hex_};'
                  f'border-radius:6px;border:1px solid rgba(28,24,21,.08)"></div>'
                  f'<div class="mono" style="font-size:10px;color:{INK};margin-top:6px;font-weight:600">{step}</div>'
                  f'<div class="mono" style="font-size:9px;color:#7A6E66">{hex_}</div></div>')
    return f'<div style="display:flex;gap:8px">{cells}</div>'

def gpage(inner, bg=PAPER):
    return (f'<div data-document-role="page" data-label="ChainSolve" '
            f'style="width:1600px;height:1000px;background:{bg};position:relative;'
            f'overflow:hidden;font-family:\'IBM Plex Sans\',system-ui,sans-serif">{inner}</div>')

def eyebrow(t, color="#C8543A"):
    return (f'<div class="mono" style="font-size:13px;letter-spacing:1.5px;font-weight:600;'
            f'text-transform:uppercase;color:{color};margin-bottom:12px">{t}</div>')

def h(t, size=40, color=INK, weight=800, ls=-1):
    return (f'<div class="mont" style="font-size:{size}px;font-weight:{weight};letter-spacing:{ls}px;'
            f'color:{color};line-height:1.05">{t}</div>')

P = 96  # page padding
# ---- page 1: cover ----
cover = gpage(
    f'<div style="position:absolute;right:-120px;top:-80px;width:760px;height:760px;opacity:.06">{mark(INK,INK)}</div>'
    f'<div style="position:absolute;left:{P}px;top:{P}px;display:flex;align-items:center;gap:28px">'
    f'<div style="width:96px;height:96px">{mark(*VARIANTS["primary"])}</div>'
    f'<span class="mont" style="font-size:52px;font-weight:700;letter-spacing:-1px;color:{INK}">ChainSolve</span></div>'
    f'<div style="position:absolute;left:{P}px;top:340px;max-width:1000px">'
    f'{eyebrow("Brand &amp; Design System · v1.0")}'
    f'{h("Simulate before<br>you build.", 92, INK, 800, -3)}'
    f'<div style="font-size:22px;line-height:1.5;color:#574E48;margin-top:32px;max-width:760px">'
    f'The complete visual identity for ChainSolve — an engineering calculation and simulation '
    f'workbench. Precise, technical, and confident: an instrument, not a toy.</div></div>'
    f'<div class="mono" style="position:absolute;left:{P}px;bottom:{P}px;font-size:13px;color:#7A6E66;'
    f'letter-spacing:.5px">Palette: Terracotta&nbsp;&nbsp;·&nbsp;&nbsp;Godfrey Engineering&nbsp;&nbsp;·&nbsp;&nbsp;Jul 2026</div>',
    PAPER)

# ---- page 2: logo ----
def variant_card(name, bg, label):
    return (f'<div style="flex:1"><div style="background:{bg};border-radius:12px;height:200px;'
            f'display:flex;align-items:center;justify-content:center;border:1px solid rgba(28,24,21,.08)">'
            f'<div style="width:120px;height:120px">{mark(*VARIANTS[name])}</div></div>'
            f'<div class="mono" style="font-size:12px;color:#7A6E66;margin-top:10px;text-align:center">{label}</div></div>')
logo_pg = gpage(
    f'<div style="padding:{P}px">'
    f'{eyebrow("01 · Logo")}'
    f'{h("The mark — a true weave", 44)}'
    f'<div style="font-size:17px;line-height:1.6;color:#574E48;margin-top:16px;max-width:1100px">'
    f'Two rounded squares interlocked as a chain link. It is a <b>true weave</b>, not a simple overlap: '
    f'the top-left link&rsquo;s right edge passes <i>over</i> the bottom-right link, while its bottom edge '
    f'passes <i>under</i>. The interlock reads as solving connected systems. Reproduce it exactly from '
    f'the master SVG — never recolor, stretch, rotate, or add shadow.</div>'
    f'<div style="display:flex;gap:24px;margin-top:48px">'
    f'{variant_card("primary", PAPER, "Two-color · primary")}'
    f'{variant_card("mono-ink", "#F2E9E3", "Mono · ink")}'
    f'{variant_card("reversed", DARK, "Two-color · reversed")}'
    f'{variant_card("mono-reversed", INK, "Mono · reversed")}'
    f'</div>'
    f'<div style="display:flex;gap:48px;margin-top:56px;align-items:center">'
    f'<div style="flex:0 0 auto;display:flex;align-items:center;gap:28px;background:{PAPER};'
    f'padding:28px 40px;border-radius:12px;border:1px solid rgba(28,24,21,.10)">'
    f'<div style="width:80px;height:80px">{mark(*VARIANTS["primary"])}</div>'
    f'<span class="mont" style="font-size:56px;font-weight:700;letter-spacing:-1.2px;color:{INK}">ChainSolve</span></div>'
    f'<div class="mono" style="font-size:13px;line-height:1.9;color:#574E48">'
    f'viewBox&nbsp;&nbsp;0 0 100 100<br>stroke-width&nbsp;&nbsp;12&nbsp;&nbsp;·&nbsp;&nbsp;weave gap&nbsp;19<br>'
    f'corner radius&nbsp;&nbsp;16% of box<br>clearspace&nbsp;&nbsp;0.25 × mark height</div></div>'
    f'</div>', PAPER)

# ---- page 3: color ----
color_pg = gpage(
    f'<div style="padding:{P}px">'
    f'{eyebrow("02 · Color")}'
    f'{h("Terracotta, warm neutrals, meaning", 44)}'
    f'<div style="font-size:16px;line-height:1.6;color:#574E48;margin-top:14px;max-width:1100px">'
    f'<b style="color:#C8543A">#E06A4E</b> is the brand accent. A warm, low-chroma neutral ramp pairs with '
    f'it and keeps the UI considered. Color carries meaning — every workbench and state has one.</div>'
    f'<div style="margin-top:36px">'
    f'<div class="mono" style="font-size:12px;font-weight:600;color:{INK};margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px">Terracotta — primary ramp</div>'
    f'{swatch_row(TC_RAMP, 4)}</div>'
    f'<div style="margin-top:28px">'
    f'<div class="mono" style="font-size:12px;font-weight:600;color:{INK};margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px">Warm neutrals</div>'
    f'{swatch_row(WARM_RAMP, 6)}</div>'
    f'<div style="display:flex;gap:64px;margin-top:36px">'
    f'<div><div class="mono" style="font-size:12px;font-weight:600;color:{INK};margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px">Functional</div>'
    + "".join(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
              f'<div style="width:28px;height:28px;border-radius:6px;background:{hx}"></div>'
              f'<div><span style="font-size:14px;font-weight:600;color:{INK}">{nm}</span> '
              f'<span class="mono" style="font-size:11px;color:#7A6E66">{hx} · {ds}</span></div></div>'
              for nm,hx,ds in FUNCTIONAL) + '</div>'
    f'<div><div class="mono" style="font-size:12px;font-weight:600;color:{INK};margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px">Workbench accents</div>'
    + "".join(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
              f'<div style="width:28px;height:28px;border-radius:6px;background:{hx}"></div>'
              f'<span style="font-size:14px;font-weight:600;color:{INK}">{nm}</span> '
              f'<span class="mono" style="font-size:11px;color:#7A6E66">{hx}</span></div>'
              for nm,hx in WORKBENCH) + '</div>'
    f'</div></div>', PAPER)

# ---- page 4: typography ----
def type_row(tok, spec, sample, size, weight, ls, mono=False, upper=False):
    fam = "'IBM Plex Mono',ui-monospace,monospace" if mono else "'Montserrat',system-ui,sans-serif"
    tt = "text-transform:uppercase;" if upper else ""
    return (f'<div style="display:flex;align-items:baseline;gap:32px;padding:14px 0;border-bottom:1px solid rgba(28,24,21,.08)">'
            f'<div class="mono" style="flex:0 0 130px;font-size:13px;color:#C8543A;font-weight:600">{tok}</div>'
            f'<div class="mono" style="flex:0 0 220px;font-size:12px;color:#7A6E66">{spec}</div>'
            f'<div style="font-family:{fam};font-size:{min(size,40)}px;font-weight:{weight};letter-spacing:{ls}px;color:{INK};{tt}line-height:1.1">{sample}</div></div>')
type_pg = gpage(
    f'<div style="padding:{P}px">'
    f'{eyebrow("03 · Typography")}'
    f'{h("Montserrat · IBM Plex Sans · IBM Plex Mono", 40)}'
    f'<div style="display:flex;gap:24px;margin-top:32px">'
    + "".join(f'<div style="flex:1;background:{PAPER};border:1px solid rgba(28,24,21,.10);border-radius:12px;padding:28px">'
              f'<div class="mono" style="font-size:11px;color:#7A6E66;letter-spacing:.5px">{role}</div>'
              f'<div style="font-family:{fam};font-size:64px;font-weight:700;color:{INK};margin:6px 0">Aa</div>'
              f'<div style="font-size:18px;font-weight:600;color:{INK}">{fname}</div>'
              f'<div style="font-size:13px;color:#574E48;margin-top:6px">{desc}</div></div>'
              for role,fam,fname,desc in [
                ("DISPLAY / BRAND","'Montserrat',sans-serif","Montserrat","Headlines, logo, marketing. 600 / 700 / 800."),
                ("UI / BODY","'IBM Plex Sans',sans-serif","IBM Plex Sans","Interface, panels, body. 400 / 500 / 600 / 700."),
                ("DATA / CODE","'IBM Plex Mono',monospace","IBM Plex Mono","Node values, units, coordinates. 400 / 500 / 600.")])
    + '</div>'
    f'<div style="margin-top:40px">'
    f'{type_row("display-xl","44 / 800 / -1.5","Simulate before you build",44,800,-1.5)}'
    f'{type_row("display-l","34 / 700 / -0.5","Multibody dynamics",34,700,-0.5)}'
    f'{type_row("h1","28 / 700 / -0.5","Workbench overview",28,700,-0.5)}'
    f'{type_row("h2","22 / 600 / -0.3","Constraint solver",22,600,-0.3)}'
    f'{type_row("body","15 / 400 / 0","Wire components and solve in real time.",18,400,0,mono=False)}'
    f'{type_row("data","14 / 500 / mono","τ = 42.7 N·m",18,500,0,mono=True)}'
    f'{type_row("eyebrow","12 / 600 / 1.5 · mono","Aerospace workbench",15,600,1.5,mono=True,upper=True)}'
    f'</div></div>', PAPER)

# ---- page 5: usage & voice ----
usage_pg = gpage(
    f'<div style="padding:{P}px;height:100%;box-sizing:border-box">'
    f'{eyebrow("04 · Usage &amp; voice", "#E8977C")}'
    f'{h("Every element earns its place", 44, PAPER)}'
    f'<div style="display:flex;gap:48px;margin-top:40px">'
    f'<div style="flex:1">'
    f'<div class="mono" style="font-size:12px;color:#C9BAB0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:16px">Voice &amp; tone</div>'
    + "".join(f'<div style="margin-bottom:18px"><span style="font-size:17px;font-weight:600;color:{PAPER}">{t}</span>'
              f'<span style="font-size:15px;color:#C9BAB0"> — {d}</span></div>'
              for t,d in [("Precise","name real quantities, units, methods."),
                          ("Confident, not loud","no hype, no exclamation."),
                          ("Active &amp; direct","&ldquo;Solve the system,&rdquo; not &ldquo;systems can be solved.&rdquo;"),
                          ("Sentence case","everywhere except the wordmark.")])
    + f'<div style="margin-top:28px;padding:20px 24px;background:{INK};border-radius:10px;border-left:3px solid {TERRACOTTA}">'
    f'<div style="font-size:15px;color:#3E9E6E">&#10003; &ldquo;Converged in 0.42 s across 6 bodies.&rdquo;</div>'
    f'<div style="font-size:15px;color:#D6453C;margin-top:8px">&#10007; &ldquo;Wow — your simulation is complete!!&rdquo;</div></div>'
    f'</div>'
    f'<div style="flex:1">'
    f'<div class="mono" style="font-size:12px;color:#C9BAB0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:16px">Never</div>'
    + "".join(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">'
              f'<span style="color:{TERRACOTTA};font-size:18px">&#10007;</span>'
              f'<span style="font-size:15px;color:#C9BAB0">{t}</span></div>'
              for t in ["Recolor the mark or use a color outside the palette",
                        "Stretch, rotate, or add a shadow to the mark",
                        "Change the weave direction, corner radius, or stroke weight",
                        "Place the two-color mark on a busy photo",
                        "Use title case or exclamation marks in product copy"])
    + f'<div style="margin-top:32px;display:flex;align-items:center;gap:20px">'
    f'<div style="width:72px;height:72px">{mark(*VARIANTS["reversed"])}</div>'
    f'<span class="mont" style="font-size:44px;font-weight:700;letter-spacing:-1px;color:{PAPER}">ChainSolve</span></div>'
    f'</div></div></div>', DARK)

guide_list = [cover, logo_pg, color_pg, type_pg, usage_pg]
_gstyle = (f"@import url('{FONTS}');*{{margin:0;padding:0;box-sizing:border-box}}"
           "body{background:#e5e0db}[data-document-role=page]{margin:0 auto 24px}"
           ".mont{font-family:'Montserrat',system-ui,sans-serif}"
           ".mono{font-family:'IBM Plex Mono',ui-monospace,monospace}")
guide_html = (f'<!doctype html><html><head><meta charset="utf-8">'
              f'<title>ChainSolve — Brand &amp; Design System</title><style>{_gstyle}</style>'
              f'</head><body>{"".join(guide_list)}</body></html>')
(A/"guide"/"brand-guide.html").write_text(guide_html)
# standalone per-page files for clean PNG previews
for i, pg in enumerate(guide_list, 1):
    one = (f'<!doctype html><html><head><meta charset="utf-8"><style>{_gstyle}'
           f'body{{background:transparent}}[data-document-role=page]{{margin:0}}</style>'
           f'</head><body>{pg}</body></html>')
    render_html(f"guide/guide-p{i}.html", one, 1600, 1000, scale=1)

manifest = ROOT/"render_manifest.json"
manifest.write_text(json.dumps(RENDER, indent=2))
print(f"generated {len(RENDER)} render targets + {len(VARIANTS)} standalone mark SVGs")
