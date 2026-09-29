#!/usr/bin/env python3
"""Lingua Franca glyph ideas: invented signs that dissolve from top left to bottom right.

Writes four standalone SVGs next to this file and, when a path is given, the
review page as HTML. Run: python3 generate.py [page.html]
"""
import random
import sys
from pathlib import Path

OUT = Path(__file__).parent
S = 512


def diag(x, y):
    return (x + y) / (2 * S)


def fall(t, start, span=0.6, power=1.1):
    return 1.0 if t < start else max(0.0, 1 - ((t - start) / span) ** power)


def svg(uid, defs, body, bg=None):
    grad = f"""<linearGradient id="{uid}g" gradientUnits="userSpaceOnUse" x1="70" y1="70" x2="450" y2="450">
      <stop offset="0" style="stop-color:var(--g0,#141a2e)"/>
      <stop offset="0.55" style="stop-color:var(--g1,#2d3f8f)"/>
      <stop offset="1" style="stop-color:var(--g2,#4fa39a)"/>
    </linearGradient>"""
    rect = f'<rect width="{S}" height="{S}" rx="96" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" role="img" aria-hidden="true">'
            f"<defs>{grad}{defs}</defs>{rect}{body}</svg>")


def mask(uid, parts):
    return f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="{S}" height="{S}">' + "".join(parts) + "</mask>"


# A. Stem: a carved sign, hooks and a dot on one stem. Breaks into shards.
def shards(uid, p=24, start=0.36, seed=11):
    rnd = random.Random(seed)
    out = []
    for gy in range(0, S, p):
        for gx in range(0, S, p):
            cx, cy = gx + p / 2, gy + p / 2
            t = diag(cx, cy)
            s = fall(t, start)
            e = max(0, t - start)
            if e and rnd.random() < e * 0.7:
                continue
            if s <= 0.06:
                continue
            size = p * s + (0.8 if s == 1 else 0)
            ang = rnd.uniform(-1, 1) * e * 80
            dx, dy = e * rnd.uniform(0, 30), e * rnd.uniform(0, 30)
            out.append(f'<rect x="{-size/2:.1f}" y="{-size/2:.1f}" width="{size:.1f}" height="{size:.1f}" fill="#fff" '
                       f'transform="translate({cx+dx:.1f} {cy+dy:.1f}) rotate({ang:.1f})"/>')
    return mask(uid, out)


def idea_stem(uid, bg=None):
    body = f"""<g fill="none" stroke="url(#{uid}g)" stroke-width="30" stroke-linecap="square" stroke-linejoin="miter" mask="url(#{uid}m)">
    <path d="M170 70 V442"/>
    <path d="M170 132 H320 A56 56 0 0 1 376 188 V262"/>
    <path d="M110 262 H286"/>
    <path d="M170 350 Q300 350 336 442"/>
    <path d="M236 70 H300" stroke-width="22"/>
  </g>
  <circle cx="380" cy="330" r="26" fill="url(#{uid}g)" mask="url(#{uid}m)"/>"""
    return svg(uid, shards(uid), body, bg)


# B. Loops: interlocked rings and a tail, halftone dots.
def halftone(uid, p=20, start=0.34):
    out = []
    for gy in range(0, S + p, p):
        for gx in range(0, S + p, p):
            cx = gx + (p / 2 if (gy // p) % 2 else 0)
            s = fall(diag(cx, gy), start, span=0.6, power=1.0)
            if s <= 0.05:
                continue
            out.append(f'<circle cx="{cx:.1f}" cy="{gy}" r="{p*0.74*s + (0.3 if s == 1 else 0):.1f}" fill="#fff"/>')
    return mask(uid, out)


def idea_loops(uid, bg=None):
    body = f"""<g fill="none" stroke="url(#{uid}g)" stroke-width="28" stroke-linecap="round" mask="url(#{uid}m)">
    <ellipse cx="214" cy="196" rx="112" ry="66" transform="rotate(-22 214 196)"/>
    <ellipse cx="296" cy="262" rx="70" ry="112" transform="rotate(24 296 262)"/>
    <path d="M330 350 C368 392 398 410 446 440"/>
  </g>
  <circle cx="130" cy="330" r="20" fill="url(#{uid}g)" mask="url(#{uid}m)"/>
  <circle cx="176" cy="392" r="12" fill="url(#{uid}g)" mask="url(#{uid}m)"/>"""
    return svg(uid, halftone(uid), body, bg)


# C. Tally: an Ogham-like spine with notches. Each mark is its own piece.
def idea_tally(uid, bg=None):
    rnd = random.Random(4)
    pieces = []

    def piece(x, y, w, h, start=0.26):
        cx, cy = x + w / 2, y + h / 2
        t = diag(cx, cy)
        s = fall(t, start, span=0.62)
        e = max(0, t - start)
        if s <= 0.05 or (e and rnd.random() < e * 0.35):
            return
        dx, dy = e * rnd.uniform(6, 60), e * rnd.uniform(0, 70)
        ang = rnd.uniform(-1, 1) * e * 90
        pieces.append(f'<rect x="{-w*s/2:.1f}" y="{-h*s/2:.1f}" width="{w*s:.1f}" height="{h*s:.1f}" rx="{min(w,h)*s/2:.1f}" '
                      f'transform="translate({cx+dx:.1f} {cy+dy:.1f}) rotate({ang:.1f})"/>')

    for x in range(52, 460, 34):
        piece(x, 250, 34, 12)
    for i, ch in enumerate("XX.U.DDD.X.UU.D.XXX.U"):
        if ch == ".":
            continue
        x = 66 + i * 19
        L = rnd.choice([56, 76, 96, 116])
        if ch in "XU":
            piece(x, 250 - L, 12, L)
        if ch in "XD":
            piece(x, 276, 12, L)
    body = f'<g fill="url(#{uid}g)">{"".join(pieces)}</g>'
    return svg(uid, "", body, bg)


# D. Marks: a base sign with diacritics that drift away, cut into slats.
def slats(uid, pitch=26, start=0.3, seed=2):
    rnd = random.Random(seed)
    out = []
    k = -pitch
    while k < 2 * S + pitch:
        t = k / (2 * S)
        s = fall(t, start, span=0.55, power=0.95)
        e = max(0, t - start)
        if s > 0.05:
            w = pitch * s + (1 if s == 1 else 0)
            k1, k2 = k - w / 2, k + w / 2
            sh = e * rnd.uniform(-34, 34)
            pts = [(k1 + 600 + sh, -600), (k2 + 600 + sh, -600), (k2 - 600 + sh, 600), (k1 - 600 + sh, 600)]
            out.append('<polygon fill="#fff" points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
        k += pitch
    return mask(uid, out)


def idea_marks(uid, bg=None):
    base = f"""<g fill="none" stroke="url(#{uid}g)" stroke-width="32" stroke-linecap="butt" mask="url(#{uid}m)">
    <path d="M118 150 V282 A98 98 0 0 0 314 282 V206 Q314 178 350 178"/>
    <path d="M216 110 V400"/>
  </g>"""
    rnd = random.Random(9)
    marks = []
    # (kind, x, y): the first few sit on the base, the rest drift out.
    spec = [("bar", 92, 76), ("dot", 262, 74), ("dot", 306, 74), ("ring", 396, 112), ("tilde", 384, 226),
            ("comma", 372, 330), ("wedge", 292, 424), ("dot", 448, 396), ("ring", 452, 300), ("bar", 410, 452)]
    for kind, x, y in spec:
        t = diag(x, y)
        s = fall(t, 0.3, span=0.62)
        e = max(0, t - 0.3)
        if s <= 0.05:
            continue
        dx, dy = e * rnd.uniform(10, 70), e * rnd.uniform(-20, 60)
        ang = rnd.uniform(-1, 1) * e * 70
        tf = f'translate({x+dx:.1f} {y+dy:.1f}) rotate({ang:.1f}) scale({s:.2f})'
        shape = {
            "bar": '<rect x="-34" y="-9" width="68" height="18"/>',
            "dot": '<circle r="13"/>',
            "ring": '<circle r="17" fill="none" stroke="url(#%sg)" stroke-width="9"/>' % uid,
            "tilde": '<path d="M-30 4 Q-15 -16 0 0 T30 -4" fill="none" stroke="url(#%sg)" stroke-width="10" stroke-linecap="round"/>' % uid,
            "comma": '<path d="M-6 -14 A12 12 0 1 1 6 -14 Q6 6 -10 22 L-14 16 Q-4 6 -6 -4Z"/>',
            "wedge": '<path d="M-20 -14 H20 L0 22Z"/>',
        }[kind]
        marks.append(f'<g transform="{tf}">{shape}</g>')
    body = base + f'<g fill="url(#{uid}g)">{"".join(marks)}</g>'
    return svg(uid, slats(uid), body, bg)


IDEAS = [
    ("stem", "Stem", idea_stem,
     "A carved sign: one stem, a hooked arm, a bar and a dot. The corner it leaves behind breaks into square shards.",
     "Feels like a syllabary character or a stamped mark."),
    ("loops", "Loops", idea_loops,
     "Two interlocked rings and a tail, like a cursive sign from an undeciphered script. It fades out as a halftone.",
     "Softest of the four. Reads well at small sizes."),
    ("tally", "Tally", idea_tally,
     "A spine with notches of different length, in the manner of Ogham. Every notch is a separate piece that tumbles off.",
     "Most literal about writing. Pieces stay whole as they drift."),
    ("marks", "Marks", idea_marks,
     "A base sign with diacritics. The marks near the corner sit on the sign. The rest wander off while the sign is cut into slats.",
     "Speaks to linguists first: dots, macrons, tildes, ogoneks."),
]

if __name__ == "__main__":
    for key, name, fn, *_ in IDEAS:
        (OUT / f"{key}.svg").write_text(fn(key, bg="#eef0ec") + "\n")
    if len(sys.argv) > 1:
        cards = []
        for key, name, fn, note, verdict in IDEAS:
            cards.append(f"""<article class="card">
  <div class="tile">{fn(key + 'a')}</div>
  <div class="meta">
    <h2>{name}</h2>
    <p>{note}</p>
    <p class="verdict">{verdict}</p>
    <div class="sizes">
      <div class="lockup"><span class="ico">{fn(key + 'b')}</span><span class="word">Lingua Franca</span></div>
      <span class="ico s32">{fn(key + 'c')}</span>
    </div>
  </div>
</article>""")
        tpl = (OUT / "page.tpl.html").read_text()
        Path(sys.argv[1]).write_text(tpl.replace("<!--CARDS-->", "\n".join(cards)))
