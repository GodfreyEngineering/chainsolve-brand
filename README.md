# ChainSolve — Brand Package

The complete visual identity for **ChainSolve**, an engineering calculation and simulation
workbench. Every asset here is generated directly from the *Brand & Design System Specification
v1.0* (Palette: Terracotta) — the mark is reproduced exactly from the master SVG, and the colour
ramps and type scale are lifted verbatim from the spec appendix.

> **Simulate before you build.**

## The mark

Two rounded squares interlocked as a chain link — a **true weave**, not a simple overlap. The
top-left link's right edge passes *over* the bottom-right link; its bottom edge passes *under*.
The interlock reads as *solving connected systems*.

```
viewBox        0 0 100 100
stroke-width   12   ·   weave gap 19
corner radius  16% of the mark's box
clearspace     0.25 × mark height   ·   min size 24px (mark) / 96px (lockup)
```

Colours are fixed. **Never** recolor, stretch, rotate, add a shadow, change the weave direction,
alter the corner radius or stroke weight, or place the two-colour mark on a busy photo.

## Contents

| Folder | Files |
|--------|-------|
| `logo/` | Mark in 4 variants (`primary`, `reversed`, `mono-ink`, `mono-reversed`) as **SVG + 1024px PNG**, plus horizontal & stacked lockups (light + dark). |
| `icon/` | App-icon tiles at 1024px — dark (product default), light, and terracotta. |
| `favicon/` | `favicon.ico` (16/32/256) + PNGs (16→512), maskable PWA icons, `site.webmanifest`. |
| `social/` | Square avatar (1024), Open Graph card (1200×630), LinkedIn banner (1584×396). |
| `guide/` | `brand-guide.html` — the 5-page brand guidelines document — plus page PNGs. |
| `tokens/` | `tokens.css` (CSS custom properties + light/dark themes) and `tokens.json`. |
| `src/` | `gen.py` — the generator. Everything in this repo is reproducible from it. |

## Colour

`#E06A4E` (terracotta 500) is the brand accent. A warm, low-chroma neutral ramp pairs with it.
Ink `#1C1815`, paper `#FAF4F0`, dark `#14110F`. Full ramps, functional colours, and per-workbench
accents live in `tokens/`.

## Type

- **Montserrat** — display, logo, marketing (600 / 700 / 800)
- **IBM Plex Sans** — interface, panels, body (400 / 500 / 600 / 700)
- **IBM Plex Mono** — node values, units, coordinates, code (400 / 500 / 600)

## Reproduce

```sh
python3 src/gen.py          # writes SVGs + render targets
python3 src/render.py       # Chrome-headless renders every target to PNG
```

Rendering uses headless Chrome (it fetches the brand fonts from Google Fonts itself); no local
font install required.

---
© Godfrey Engineering. Generated from Brand & Design System Specification v1.0 · Jul 2026.
