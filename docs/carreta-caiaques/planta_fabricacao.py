#!/usr/bin/env python3
"""Planta de fabricação — carreta porta-caiaques (Aqua Terra Paraty), rev. 3.

Uso: python3 planta_fabricacao.py <pasta_saida> [render_3d.png]
Gera folha1.svg … folha5.svg (A3, cotas em mm).

Eixos reais: x = comprimento (0 = traseira do chassi, + para a lança),
y = largura (0 = eixo de simetria), z = altura a partir do chão.
"""
import base64
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
IMG = sys.argv[2] if len(sys.argv) > 2 else None
REV = '3 — fabricação'
DATA = '14/10/2026'
NFOLHAS = 5

# ---------------------------------------------------------------- geometria
TIERS = (480, 960, 1440)             # eixo das travessas P10 (40×40)
MAST = ((50, 150), (1450, 1550))     # mastros P9 (100 em x × 50 em y)
MZ = (333, 1500)                     # pé / topo do mastro
CH = (275, 325)                      # longarinas P1
BP = ((0, 300), (1300, 1600))        # chapas base C1
BPZ = (325, 333)
AX = (200, 1360)                     # eixos traseiro / dianteiro (dianteiro 40 atrás do pino-rei)
AZ, RW = 200, 203                    # altura do eixo, raio do pneu 16"
KX = (-2100, 2700)                   # caiaque de referência 4,8 m
KY, KW, KH = 400, 560, 330
BOX = (-1600, -1000)                 # caixa de equipo
BOXZ = (480, 780)
BHW = 175
P7X, P7Z = (-1650, 50), (405, 455)   # viga porta-caixa
TIE = ((50, 900), (-950, 455))       # tirante: ponto no mastro / ponto na viga
PIV = (1665, 230)                    # pino da lança
HANDLE = (3000, 900)
ZTOP = 1830                          # topo dos caiaques


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


STYLE = """<style>
 .v{fill:none;stroke:#000;stroke-width:0.45;stroke-linejoin:round}
 .vf{fill:#e9eef2;stroke:#000;stroke-width:0.45;stroke-linejoin:round}
 .pl{fill:#c9d4de;stroke:#000;stroke-width:0.4;stroke-linejoin:round}
 .wf{fill:#fff;stroke:#000;stroke-width:0.35}
 .wh{fill:#3a3a3a;stroke:#000;stroke-width:0.45}
 .t{fill:none;stroke:#000;stroke-width:0.18}
 .h{fill:none;stroke:#000;stroke-width:0.25;stroke-dasharray:1.2 0.8}
 .ph{fill:none;stroke:#1f5fa8;stroke-width:0.25;stroke-dasharray:4 0.8 0.8 0.8}
 .c{fill:none;stroke:#a00;stroke-width:0.15;stroke-dasharray:5 1 1 1}
 .d{fill:none;stroke:#000;stroke-width:0.15}
 .eva{fill:#f2b84b;stroke:#000;stroke-width:0.3}
 .perf{fill:#fff;stroke:#000;stroke-width:0.1}
 .hole{fill:#fff;stroke:#000;stroke-width:0.3}
 text{font-family:'DejaVu Sans',Arial,sans-serif;fill:#000}
 .dt{font-size:2.1px}
 .lbl{font-size:3.1px;font-weight:bold}
 .sm{font-size:1.9px}
 .xs{font-size:1.6px}
 .tb{font-size:2.3px}
 .bal{fill:#fff;stroke:#000;stroke-width:0.22}
 .bt{font-size:1.55px;font-weight:bold}
</style>
<defs>
 <marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2" markerHeight="2" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,1.5 L10,5 L0,8.5 z" fill="#000"/></marker>
 <pattern id="furos" width="1.5" height="1.3" patternUnits="userSpaceOnUse">
  <rect width="1.5" height="1.3" fill="#e9eef2"/><circle cx="0.75" cy="0.65" r="0.42" fill="#fff" stroke="#888" stroke-width="0.05"/></pattern>
</defs>
"""


class Sheet:
    def __init__(s, num, sub, scale):
        s.num, s.sub, s.scale, s.el = num, sub, scale, []

    def a(s, x):
        s.el.append(x)

    def text(s, x, y, t, cls='sm', anchor='start', extra=''):
        s.a(f'<text class="{cls}" x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" {extra}>{esc(t)}</text>')

    def view(s, ox, oy, sc):
        return View(s, ox, oy, sc)

    def para(s, x, y, rows, dy=3.2, cls='sm'):
        """Linhas de texto; '# ' no início = título em negrito."""
        for i, r in enumerate(rows):
            if r.startswith('# '):
                if i:
                    y += 2
                s.text(x, y, r[2:], 'lbl')
                y += dy + 0.9
            else:
                s.text(x, y, r, cls)
                y += dy
        return y

    def table(s, x, y, widths, rows, rh=4.2, cls='sm'):
        tw = sum(widths)
        for i, row in enumerate(rows):
            yy = y + i * rh
            fill = '#dfe6ec' if i == 0 else 'none'
            s.a(f'<rect x="{x}" y="{yy:.2f}" width="{tw}" height="{rh}" fill="{fill}" stroke="#000" stroke-width="{0.25 if i == 0 else 0.12}"/>')
            xx = x
            for j, c in enumerate(row):
                s.text(xx + 0.9, yy + rh - 1.25, c, cls, extra='font-weight="bold"' if i == 0 else '')
                xx += widths[j]
        xx = x
        for w in widths[:-1]:
            xx += w
            s.a(f'<line class="t" x1="{xx}" y1="{y}" x2="{xx}" y2="{y + len(rows) * rh:.2f}"/>')
        return y + len(rows) * rh

    def svg(s):
        TBX, TBY, TBW, TBH = 233, 252, 177, 35
        tb = [f'<rect x="{TBX}" y="{TBY}" width="{TBW}" height="{TBH}" fill="#fff" stroke="#000" stroke-width="0.5"/>',
              f'<line class="t" x1="{TBX}" y1="{TBY + 13}" x2="{TBX + TBW}" y2="{TBY + 13}"/>',
              f'<line class="t" x1="{TBX}" y1="{TBY + 24}" x2="{TBX + TBW}" y2="{TBY + 24}"/>']
        for xx in (TBX + 45, TBX + 90, TBX + 135):
            tb.append(f'<line class="t" x1="{xx}" y1="{TBY + 13}" x2="{xx}" y2="{TBY + TBH}"/>')
        tb.append(f'<text x="{TBX + 3}" y="{TBY + 6.2}" font-size="4.3" font-weight="bold">CARRETA PORTA-CAIAQUES — 6 UNIDADES</text>')
        tb.append(f'<text class="tb" x="{TBX + 3}" y="{TBY + 10.8}" font-weight="bold">{esc(s.sub)}</text>')
        tb.append(f'<text class="xs" x="{TBX + TBW - 3}" y="{TBY + 10.8}" text-anchor="end">Aqua Terra Paraty · Paraty/RJ</text>')
        cells = [('ESCALA', s.scale), ('FOLHA', f'{s.num} / {NFOLHAS}'), ('UNIDADE', 'mm · 1º diedro'), ('REVISÃO', REV),
                 ('DATA', DATA), ('DESENHO', 'Claude / Lucas'), ('MATERIAL', 'Alum. 6061-T6'), ('FORMATO', 'A3')]
        for i, (k, v) in enumerate(cells):
            cx = TBX + (i % 4) * 45 + 2
            cy = TBY + 13 + (i // 4) * 11
            tb.append(f'<text font-size="1.7" x="{cx}" y="{cy + 3}" fill="#555">{k}</text>')
            tb.append(f'<text class="tb" x="{cx}" y="{cy + 8}" font-weight="bold">{esc(v)}</text>')
        body = '\n'.join(s.el)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="420mm" height="297mm" viewBox="0 0 420 297">\n{STYLE}\n'
                f'<rect x="0" y="0" width="420" height="297" fill="#fff"/>\n'
                f'<rect x="10" y="10" width="400" height="277" fill="none" stroke="#000" stroke-width="0.7"/>\n'
                f'{body}\n' + '\n'.join(tb) + '\n</svg>')


class View:
    """Vista ortográfica: (u, w) reais -> papel. u para a direita, w para cima."""

    def __init__(v, sh, ox, oy, sc):
        v.sh, v.ox, v.oy, v.sc = sh, ox, oy, sc

    def X(v, u):
        return v.ox + u * v.sc

    def Y(v, w):
        return v.oy - w * v.sc

    def rect(v, u1, u2, w1, w2, cls='vf', extra=''):
        x1, x2 = sorted((v.X(u1), v.X(u2)))
        y1, y2 = sorted((v.Y(w1), v.Y(w2)))
        v.sh.a(f'<rect class="{cls}" x="{x1:.2f}" y="{y1:.2f}" width="{x2 - x1:.2f}" height="{y2 - y1:.2f}" {extra}/>')

    def tube(v, u1, u2, w1, w2, t=3, cls='vf'):
        """Seção de tubo retangular (parede t)."""
        v.rect(u1, u2, w1, w2, cls)
        v.rect(u1 + t, u2 - t, w1 + t, w2 - t, 'wf')

    def line(v, u1, w1, u2, w2, cls='v', extra=''):
        v.sh.a(f'<line class="{cls}" x1="{v.X(u1):.2f}" y1="{v.Y(w1):.2f}" x2="{v.X(u2):.2f}" y2="{v.Y(w2):.2f}" {extra}/>')

    def circ(v, u, w, r, cls='v', extra=''):
        v.sh.a(f'<circle class="{cls}" cx="{v.X(u):.2f}" cy="{v.Y(w):.2f}" r="{r * v.sc:.2f}" {extra}/>')

    def poly(v, pts, cls='vf', extra=''):
        p = ' '.join(f'{v.X(u):.2f},{v.Y(w):.2f}' for u, w in pts)
        v.sh.a(f'<polygon class="{cls}" points="{p}" {extra}/>')

    def cmark(v, u, w, r):
        v.line(u - r, w, u + r, w, 'c')
        v.line(u, w - r, u, w + r, 'c')

    def brk_v(v, u, w1, w2):
        """Linha de interrupção vertical (zigue-zague) em u."""
        x = v.X(u)
        y1, y2 = v.Y(w1), v.Y(w2)
        ym = (y1 + y2) / 2
        v.sh.a(f'<polyline class="t" points="{x:.2f},{y1 - 1:.2f} {x:.2f},{ym - 1:.2f} {x + 1:.2f},{ym - 0.4:.2f} '
               f'{x - 1:.2f},{ym + 0.4:.2f} {x:.2f},{ym + 1:.2f} {x:.2f},{y2 + 1:.2f}"/>')

    def brk_h(v, w, u1, u2):
        y = v.Y(w)
        x1, x2 = sorted((v.X(u1), v.X(u2)))
        xm = (x1 + x2) / 2
        v.sh.a(f'<polyline class="t" points="{x1 - 1:.2f},{y:.2f} {xm - 1:.2f},{y:.2f} {xm - 0.4:.2f},{y - 1:.2f} '
               f'{xm + 0.4:.2f},{y + 1:.2f} {xm + 1:.2f},{y:.2f} {x2 + 1:.2f},{y:.2f}"/>')

    def hd(v, u1, w1, u2, w2, yl, txt=None, toff=0):
        """Cota horizontal; yl = y da linha de cota no papel."""
        x1, x2 = v.X(u1), v.X(u2)
        for x, y in ((x1, v.Y(w1)), (x2, v.Y(w2))):
            if abs(y - yl) > 0.4:
                sg = 1 if yl > y else -1
                v.sh.a(f'<line class="d" x1="{x:.2f}" y1="{y + sg * 0.6:.2f}" x2="{x:.2f}" y2="{yl + sg * 1.1:.2f}"/>')
        v.sh.a(f'<line class="d" x1="{x1:.2f}" y1="{yl:.2f}" x2="{x2:.2f}" y2="{yl:.2f}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        t = txt if txt is not None else f'{abs(u2 - u1):.0f}'
        v.sh.text((x1 + x2) / 2 + toff, yl - 0.6, t, 'dt', 'middle')

    def vd(v, w1, u1, w2, u2, xl, txt=None, toff=0):
        """Cota vertical; xl = x da linha de cota no papel."""
        y1, y2 = v.Y(w1), v.Y(w2)
        for x, y in ((v.X(u1), y1), (v.X(u2), y2)):
            if abs(x - xl) > 0.4:
                sg = 1 if xl > x else -1
                v.sh.a(f'<line class="d" x1="{x + sg * 0.6:.2f}" y1="{y:.2f}" x2="{xl + sg * 1.1:.2f}" y2="{y:.2f}"/>')
        v.sh.a(f'<line class="d" x1="{xl:.2f}" y1="{y1:.2f}" x2="{xl:.2f}" y2="{y2:.2f}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        t = txt if txt is not None else f'{abs(w2 - w1):.0f}'
        ym = (y1 + y2) / 2 + toff
        v.sh.a(f'<text class="dt" x="{xl - 0.6:.2f}" y="{ym:.2f}" text-anchor="middle" transform="rotate(-90 {xl - 0.6:.2f} {ym:.2f})">{esc(t)}</text>')

    def bal(v, u, w, dx, dy, n):
        x, y = v.X(u), v.Y(w)
        tx, ty = x + dx, y + dy
        L = math.hypot(dx, dy) or 1
        v.sh.a(f'<line class="d" x1="{x:.2f}" y1="{y:.2f}" x2="{tx - dx / L * 2.4:.2f}" y2="{ty - dy / L * 2.4:.2f}"/>')
        v.sh.a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.35" fill="#000"/>')
        v.sh.a(f'<circle class="bal" cx="{tx:.2f}" cy="{ty:.2f}" r="2.4"/>')
        v.sh.text(tx, ty + 0.55, n, 'bt', 'middle')

    def note(v, u, w, dx, dy, t, anchor='start', cls='xs'):
        x, y = v.X(u), v.Y(w)
        tx, ty = x + dx, y + dy
        v.sh.a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.3" fill="#000"/>')
        tail = 1.5 if anchor == 'start' else -1.5
        v.sh.a(f'<polyline class="d" points="{x:.2f},{y:.2f} {tx:.2f},{ty:.2f} {tx + tail:.2f},{ty:.2f}"/>')
        v.sh.text(tx + tail + (0.5 if tail > 0 else -0.5), ty + 0.6, t, cls, anchor)

    def label(v, x, y, t):
        v.sh.text(x, y, t, 'lbl', 'middle')


# ------------------------------------------------------------ peças comuns
def kayak_side(v, zb):
    x1, x2 = KX
    X, Y = v.X, v.Y
    d = (f'M{X(x1):.2f},{Y(zb + 250):.2f} Q{X(x1 + 700):.2f},{Y(zb):.2f} {X(x1 + 1500):.2f},{Y(zb):.2f} '
         f'L{X(x2 - 1500):.2f},{Y(zb):.2f} Q{X(x2 - 600):.2f},{Y(zb):.2f} {X(x2):.2f},{Y(zb + 270):.2f} '
         f'Q{X(x2 - 900):.2f},{Y(zb + KH):.2f} {X(800):.2f},{Y(zb + KH):.2f} '
         f'Q{X(x1 + 900):.2f},{Y(zb + KH):.2f} {X(x1):.2f},{Y(zb + 250):.2f} Z')
    v.sh.a(f'<path class="ph" d="{d}"/>')


def kayak_top(v, yc):
    x1, x2 = KX
    X, Y = v.X, v.Y
    h = KW / 2
    d = (f'M{X(x1):.2f},{Y(yc):.2f} Q{X(x1 + 1200):.2f},{Y(yc + h):.2f} {X(500):.2f},{Y(yc + h):.2f} '
         f'Q{X(x2 - 1100):.2f},{Y(yc + h):.2f} {X(x2):.2f},{Y(yc):.2f} '
         f'Q{X(x2 - 1100):.2f},{Y(yc - h):.2f} {X(500):.2f},{Y(yc - h):.2f} '
         f'Q{X(x1 + 1200):.2f},{Y(yc - h):.2f} {X(x1):.2f},{Y(yc):.2f} Z')
    v.sh.a(f'<path class="ph" d="{d}"/>')


def kayak_sec(v, yc, zb):
    X, Y = v.X, v.Y
    d = (f'M{X(yc - 280):.2f},{Y(zb + 130):.2f} Q{X(yc - 280):.2f},{Y(zb):.2f} {X(yc):.2f},{Y(zb):.2f} '
         f'Q{X(yc + 280):.2f},{Y(zb):.2f} {X(yc + 280):.2f},{Y(zb + 130):.2f} '
         f'Q{X(yc + 250):.2f},{Y(zb + KH):.2f} {X(yc):.2f},{Y(zb + KH):.2f} '
         f'Q{X(yc - 250):.2f},{Y(zb + KH):.2f} {X(yc - 280):.2f},{Y(zb + 130):.2f} Z')
    v.sh.a(f'<path class="ph" d="{d}"/>')


def cradle_sec(v, yc, c, base_cls='pl'):
    """Berço (base C9 + EVA côncavo) visto em seção y-z, sobre travessa de eixo c."""
    v.rect(yc - 200, yc + 200, c + 20, c + 25, base_cls)
    X, Y = v.X, v.Y
    d = (f'M{X(yc - 200):.2f},{Y(c + 25):.2f} L{X(yc + 200):.2f},{Y(c + 25):.2f} L{X(yc + 200):.2f},{Y(c + 95):.2f} '
         f'Q{X(yc):.2f},{Y(c + 25):.2f} {X(yc - 200):.2f},{Y(c + 95):.2f} Z')
    v.sh.a(f'<path class="eva" d="{d}"/>')


def tie_poly():
    (x0, z0), (x1, z1) = TIE
    L = math.hypot(x1 - x0, z1 - z0)
    dx, dz = (x1 - x0) / L, (z1 - z0) / L
    nx, nz = -dz, dx
    pts = []
    for o in (15, -15):
        bx, bz = x0 + o * nx, z0 + o * nz
        t = (50 - bx) / dx
        pts.append((50, bz + t * dz))
    ends = []
    for o in (-15, 15):
        bx, bz = x0 + o * nx, z0 + o * nz
        t = (P7Z[1] - bz) / dz
        ends.append((bx + t * dx, P7Z[1]))
    # garante que a borda inferior toca a viga: desloca o tirante para cima se preciso
    return [pts[0], pts[1], ends[0], ends[1]]


def tie_len():
    (x0, z0), (x1, z1) = TIE
    return math.hypot(x1 - x0, z1 - z0), math.degrees(math.atan2(z0 - z1, x0 - x1))


def ground(v, u1, u2, hatch=True):
    v.line(u1, 0, u2, 0, 'v')
    if hatch:
        n = int((v.X(u2) - v.X(u1)) / 4)
        for i in range(n + 1):
            xx = v.X(u1) + i * 4
            v.sh.a(f'<line class="t" x1="{xx:.2f}" y1="{v.oy:.2f}" x2="{xx - 1.5:.2f}" y2="{v.oy + 1.5:.2f}"/>')


# ================================================================ FOLHA 1
def folha1():
    sh = Sheet(1, 'Folha 1 — Conjunto geral', '1:25')
    s = 0.04
    G = 116
    # ---------------- vista lateral
    v = sh.view(100, G, s)
    ground(v, -2150, 3080)
    for x in AX:
        v.circ(x, AZ, RW, 'wh')
        v.circ(x, AZ, 120, 'vf')
        v.circ(x, AZ, 13, 'v')
    v.rect(0, 1600, *CH)
    for (b1, b2) in BP:
        v.rect(b1, b2, *BPZ, 'pl')
    for (m1, m2) in MAST:
        v.rect(m1, m2, MZ[0], MZ[1] + 3)
    v.rect(150, 1450, 1450, 1500)
    v.poly([(150, 333), (300, 333), (150, 483)])
    v.poly([(1450, 333), (1300, 333), (1450, 483)])
    for c in TIERS:
        for xm in (100, 1500):
            v.rect(xm - 75, xm + 75, c + 20, c + 95, 'eva')
            v.rect(xm - 20, xm + 20, c - 20, c + 20)
    # direção / lança
    v.rect(1250, 1550, 269, 275, 'pl')
    v.rect(1425, 1625, 205, 255)
    v.rect(1320, 1425, 160, 255, 'pl')
    v.rect(1595, 1695, 200, 260, 'pl')
    ang = math.atan2(HANDLE[1] - PIV[1], HANDLE[0] - PIV[0])
    nx, nz = -math.sin(ang) * 19, math.cos(ang) * 19
    v.poly([(PIV[0] + nx, PIV[1] + nz), (HANDLE[0] + nx, HANDLE[1] + nz), (HANDLE[0] - nx, HANDLE[1] - nz), (PIV[0] - nx, PIV[1] - nz)])
    v.circ(HANDLE[0], HANDLE[1], 22, 'wh')
    v.circ(PIV[0], PIV[1], 15, 'wf')
    # porta-caixa
    v.rect(0, 50, 333, 405)
    v.rect(*P7X, *P7Z)
    v.poly(tie_poly())
    v.rect(BOX[0], BOX[1], *BOXZ, 'vf', 'style="fill:url(#furos)"')
    v.rect(-1575, -1550, 455, 480)
    v.rect(-1050, -1025, 455, 480)
    for c in TIERS:
        kayak_side(v, c + 60)
    # cotas
    v.hd(0, 0, 1600, 0, G + 6)
    v.hd(AX[0], AZ, AX[1], AZ, G + 11, '1160 (entre-eixos)')
    v.hd(1600, CH[0], HANDLE[0], HANDLE[1], G + 6, '1400')
    v.hd(P7X[0], P7Z[0], 0, 0, G + 6, '1650')
    v.hd(BOX[0], BOXZ[1], BOX[1], BOXZ[1], v.Y(BOXZ[1]) - 2.5, '600')
    v.hd(KX[0], 1000, KX[1], 1000, v.Y(ZTOP) - 3, 'caiaque de ref. 4800 (máx. 5200)')
    xl = v.X(-560)
    v.vd(0, -560, TIERS[0] + 20, 80, xl, '500')
    v.vd(TIERS[0] + 20, 80, TIERS[1] + 20, 80, xl, '480')
    v.vd(TIERS[1] + 20, 80, TIERS[2] + 20, 80, xl, '480')
    v.vd(0, -880, MZ[1], 50, v.X(-880), '1500')
    v.vd(0, -1700, BOXZ[0], BOX[0], v.X(-1700), '480')
    v.vd(BOXZ[0], BOX[0], BOXZ[1], BOX[0], v.X(BOX[0]) - 2.2, '300')
    v.vd(0, HANDLE[0] + 60, HANDLE[1], HANDLE[0], v.X(HANDLE[0]) + 3, '≈900')
    sh.text(v.X(0) - 1, v.Y(70), 'Ø406', 'xs', 'end')
    for (u, w, dx, dy, n) in ((800, 300, 0, 9, 'P1'), (100, 1150, 9, -6, 'P9'), (800, 1475, 0, -7, 'P6'),
                              (1500, 960, 9, -4, 'P10'), (1500, TIERS[0] + 60, 10, -3, 'K6'), (-800, 430, 0, 7, 'P7'),
                              (-500, 700, 2, -8, 'P11'), (2300, 230 + 635 * 0.502, 2, 7, 'P12'), (1400, 60, 6, 6, 'K1'),
                              (-1300, 650, 4, -14, 'C10'), (1645, 230, 7, 2, 'C7')):
        v.bal(u, w, dx, dy, n)
    v.label(v.X(450), G + 25, 'VISTA LATERAL — 1:25')

    # ---------------- vista posterior
    r = sh.view(300, G, s)
    ground(r, -900, 900)
    for sg in (-1, 1):
        r.rect(sg * 467, sg * 633, 0, 406, 'wh', 'rx="1.6"')
    r.rect(-430, 430, 225, 275)
    for sg in (-1, 1):
        r.rect(sg * 430, sg * 438, 160, 275, 'pl')
    r.rect(-625, 625, 188, 212)
    r.rect(-200, 200, *CH)
    r.rect(-200, 200, *BPZ, 'pl')
    r.rect(-25, 25, MZ[0], MZ[1] + 3)
    for sg in (-1, 1):
        r.poly([(sg * 25, 333), (sg * 175, 333), (sg * 25, 483)])
    for c in TIERS:
        r.rect(-750, 750, c - 20, c + 20)
        for sg in (-1, 1):
            r.rect(sg * 750, sg * 758, c - 22, c + 22, 'wh')
            cradle_sec(r, sg * KY, c)
            kayak_sec(r, sg * KY, c + 60)
    r.rect(-25, 25, 333, 405)
    r.rect(-25, 25, *P7Z)
    r.rect(-15, 15, 455, 900)
    r.rect(-175, 175, 455, 480)
    r.rect(-BHW, BHW, *BOXZ, 'vf', 'style="fill:url(#furos)"')
    r.hd(-750, TIERS[2] + 20, 750, TIERS[2] + 20, r.Y(ZTOP) - 3, '1500')
    r.hd(-KY, ZTOP, KY, ZTOP, r.Y(ZTOP) - 8, '800 (eixo dos caiaques)')
    r.hd(-BHW, BOXZ[0], BHW, BOXZ[0], G + 6, '350 (caixa)')
    r.hd(-550, 0, 550, 0, G + 11, '1100 (bitola)')
    r.hd(-633, 0, 633, 0, G + 16, '1266')
    r.vd(0, -800, ZTOP, -400, r.X(-820), '≈1830 com caiaques')
    for (u, w, dx, dy, n) in ((650, 960, 8, 6, 'P10'), (0, 1250, 9, -10, 'P9'), (400, TIERS[1] + 60, 13, 9, 'K6'),
                              (-100, 700, 13, 3, 'C10'), (-550, 300, -9, 4, 'K1'), (100, 400, 14, 10, 'C2')):
        r.bal(u, w, dx, dy, n)
    r.label(300, G + 25, 'VISTA POSTERIOR — 1:25')

    # ---------------- vista superior
    t = sh.view(100, 190, s)
    t.line(-2200, 0, 3100, 0, 'c')
    for x in AX:
        for sg in (-1, 1):
            t.rect(x - RW, x + RW, sg * 467, sg * 633, 'wh', 'rx="1"')
    t.rect(175, 225, -438, 438)
    t.rect(1375, 1425, -438, 438)
    for sg in (-1, 1):
        t.rect(0, 1600, sg * 150, sg * 200)
    t.rect(775, 825, -150, 150)
    for (b1, b2) in BP:
        t.rect(b1, b2, -200, 200, 'pl')
    for xm in (100, 1500):
        t.rect(xm - 20, xm + 20, -758, 758)
        for sg in (-1, 1):
            t.rect(xm - 75, xm + 75, sg * 200, sg * 600, 'eva')
    for (m1, m2) in MAST:
        t.rect(m1, m2, -25, 25)
    t.rect(150, 1450, -25, 25)
    t.rect(1600, 1695, -33, 33, 'pl')
    t.rect(1665, HANDLE[0], -19, 19)
    t.rect(HANDLE[0] - 19, HANDLE[0] + 19, -250, 250)
    for sg in (-1, 1):
        t.rect(HANDLE[0] - 22, HANDLE[0] + 22, sg * 120, sg * 250, 'wh')
    t.rect(-1650, 0, -25, 25)
    t.rect(BOX[0], BOX[1], -BHW, BHW, 'vf', 'style="fill:url(#furos)"')
    for sg in (-1, 1):
        kayak_top(t, sg * KY)
        a = math.radians(35) * sg
        t.line(1400, 0, 1400 + 1700 * math.cos(a), 1700 * math.sin(a), 'ph')
    sh.text(t.X(2600), t.Y(560), 'giro ±35°', 'xs', 'middle', 'fill="#1f5fa8"')
    t.vd(-750, -2150, 750, -2150, t.X(-2150), '1500')
    t.vd(-250, HANDLE[0], 250, HANDLE[0], t.X(HANDLE[0]) + 3, '500')
    t.hd(P7X[0], -25, HANDLE[0], -250, t.Y(-760) + 4, '4650 (comprimento total sem caiaques)')
    v.label(v.X(450), 229, 'VISTA SUPERIOR — 1:25')

    # ---------------- imagem 3D
    if IMG and os.path.exists(IMG):
        b64 = base64.b64encode(open(IMG, 'rb').read()).decode()
        sh.a(f'<image x="244" y="144" width="161" height="98.4" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{b64}"/>')
        sh.a('<rect x="244" y="144" width="161" height="98.4" fill="none" stroke="#000" stroke-width="0.3"/>')
        sh.text(245.5, 147, 'Ilustração 3D (fora de escala)', 'xs')

    # ---------------- índice e notas
    sh.a('<rect x="347" y="14" width="60" height="30" fill="#fff" stroke="#000" stroke-width="0.25"/>')
    sh.para(349, 18, ['FOLHAS DESTE CONJUNTO', '1  Conjunto geral', '2  Chassi, eixos e direção', '3  Mastros, travessas e berços',
                      '4  Porta-caixa, caixa e lança', '5  Lista de corte, compras e', '    instruções de fabricação'], dy=3.6, cls='xs')
    sh.para(16, 236, [
        '# NOTAS GERAIS',
        '1. Cotas em mm. Não medir no desenho; usar sempre as cotas. Tolerância geral ±2 mm em comprimentos, ±0,5 mm em furos.',
        '2. Alumínio 6061-T6 (perfis e chapas) salvo indicação. Eixos, pinos e fixadores em inox. Nenhuma peça em aço carbono.',
        '3. Marcas P = perfis, C = chapas, K = itens comprados. Lista completa de corte e compras na folha 5.',
        '4. Capacidade: 6 caiaques (3 níveis × 2 lados) até 5,2 m / 30 kg cada + caixa de equipo ~25 kg. Peso da carreta vazia ≈ 80 kg.',
        '5. ANTES DE CORTAR: conferir com o cliente as rodas compradas e os caiaques reais (checklist na folha 5).',
    ], dy=3.3)
    return sh


# ================================================================ FOLHA 2
def folha2():
    sh = Sheet(2, 'Folha 2 — Chassi, eixos e direção', '1:10 (detalhes 1:5)')
    s = 0.1
    # ---------------- vista lateral do chassi
    G = 84
    v = sh.view(30, G, s)
    v.line(-80, 0, 1720, 0, 't')
    sh.text(v.X(-75), G - 0.8, 'nível do chão', 'xs')
    for x in AX:
        v.circ(x, AZ, RW, 'ph')
    v.rect(-60, 50, *P7Z)
    v.brk_v(-60, P7Z[0], P7Z[1])
    v.rect(0, 50, 333, 405)
    v.rect(0, 1600, *CH)
    for x in (50, 775, 825, 1550):
        v.line(x, CH[0], x, CH[1], 'h')
    for (b1, b2) in BP:
        v.rect(b1, b2, *BPZ, 'pl')
    for (m1, m2) in MAST:
        v.rect(m1, m2, MZ[0], 540)
        v.brk_h(540, m1, m2)
        v.rect(m1 + 30, m2 - 30, TIERS[0] - 20, TIERS[0] + 20, 'vf')
        v.line(m1 + 30, TIERS[0] - 20, m2 - 30, TIERS[0] + 20, 't')
    v.poly([(150, 333), (300, 333), (150, 483)])
    v.poly([(1450, 333), (1300, 333), (1450, 483)])
    # eixo traseiro
    v.rect(175, 225, 225, 275, 'h')
    v.rect(160, 240, 160, 275, 'pl')
    v.circ(200, AZ, 12.75, 'hole')
    v.cmark(200, AZ, 30)
    # direção
    v.rect(1250, 1550, 269, 275, 'pl')
    v.rect(1275, 1525, 261, 269, 'wf')
    v.rect(1275, 1525, 255, 261, 'pl')
    v.rect(1250, 1280, 219, 269)
    v.rect(1425, 1625, 205, 255)
    v.rect(1375, 1425, 205, 255, 'h')
    v.rect(1392, 1408, 189, 285, 'h')
    v.rect(1320, 1425, 160, 255, 'pl')
    v.circ(AX[1], AZ, 12.75, 'hole')
    v.cmark(AX[1], AZ, 30)
    v.line(1400, 150, 1400, 300, 'c')
    ang = math.atan2(HANDLE[1] - PIV[1], HANDLE[0] - PIV[0])
    ux, uz = math.cos(ang), math.sin(ang)
    nx, nz = -uz * 19, ux * 19
    e = (PIV[0] + 330 * ux, PIV[1] + 330 * uz)
    v.poly([(PIV[0] + nx, PIV[1] + nz), (e[0] + nx, e[1] + nz), (e[0] - nx, e[1] - nz), (PIV[0] - nx, PIV[1] - nz)])
    v.circ(PIV[0], PIV[1], 15, 'h')
    v.rect(1595, 1695, 200, 260, 'pl')
    v.circ(PIV[0], PIV[1], 8.25, 'hole')
    v.line(e[0] + nx, e[1] + nz, e[0] - nx, e[1] - nz, 't', 'stroke-dasharray="0.6 0.4"')
    # cotas
    v.hd(0, 0, 1600, 0, G + 6)
    v.hd(0, 0, AX[0], AZ, G + 11, '200')
    v.hd(AX[0], AZ, AX[1], AZ, G + 11)
    v.hd(AX[1], AZ, PIV[0], PIV[1], G + 11)
    v.hd(AX[1], 150, 1400, 150, v.Y(150) + 2, '40')
    xr = v.X(1730)
    v.vd(0, 1700, AZ, 1440, xr + 3, '200')
    v.vd(0, 1700, CH[0], 1600, xr + 7.5, '275')
    v.vd(0, 1700, BPZ[1], 1600, xr + 12, '333')
    v.vd(BPZ[1], 0, P7Z[0], 0, v.X(-60) - 2.5, '72')
    v.vd(PIV[1], 1695, AZ, 1695, v.X(1695) + 3, '30')
    for (u, w, dx, dy, n) in ((900, 300, 0, -14, 'P1'), (800, 290, 4, -16, 'P2'), (225, 330, 8, -12, 'C1'), (230, 380, 9, -10, 'C2'),
                              (100, 500, -8, -6, 'P9'), (25, 380, -7, -6, 'P8'), (-30, 430, -1, -9, 'P7'), (205, 170, -8, 5, 'C3'),
                              (200, 250, -12, -2, 'P3'), (1265, 240, -6, 5, 'P17'), (1440, 180, 1, 6, 'C4'), (1550, 230, 0, 7, 'P5'),
                              (1640, 250, 6, -8, 'C7'), (1770, 290, 6, -4, 'P12')):
        v.bal(u, w, dx, dy, n)
    v.label(v.X(800), G + 17, 'VISTA LATERAL DO CHASSI — 1:10')

    # ---------------- vista de cima do chassi
    T = sh.view(30, 160, s)
    T.line(-80, 0, 1820, 0, 'c')
    T.rect(175, 225, -430, 430)
    T.rect(1375, 1425, -430, 430)
    for sg in (-1, 1):
        T.rect(160, 240, sg * 430, sg * 438, 'pl')
        T.rect(1320, 1425, sg * 430, sg * 438, 'pl')
        T.rect(0, 1600, sg * 150, sg * 200)
    T.rect(1250, 1550, -200, 200, 'h')
    T.circ(1400, 0, 125, 'h')
    for sg in (-1, 1):
        T.rect(1250, 1280, sg * 105, sg * 155, 'h')
    T.rect(775, 825, -150, 150)
    for (b1, b2) in BP:
        T.rect(b1, b2, -200, 200, 'pl')
    for (m1, m2) in MAST:
        T.tube(m1, m2, -25, 25)
    T.rect(150, 300, -3, 3)
    T.rect(1300, 1450, -3, 3)
    for sg in (-1, 1):
        T.rect(97, 103, sg * 25, sg * 175)
        T.rect(1497, 1503, sg * 25, sg * 175)
    T.rect(-60, 50, -25, 25)
    T.brk_v(-60, -25, 25)
    T.rect(1600, 1625, -25, 25)
    for sg in (-1, 1):
        T.rect(1600, 1695, sg * 25, sg * 33, 'pl')
    T.rect(1650, 1680, -24, 24, 'wf')
    T.rect(1657, 1673, -45, 45)
    T.rect(1680, 1800, -19, 19)
    T.brk_v(1800, -19, 19)
    for x in (200, 1400):
        T.line(x, -470, x, 470, 'c')
    for x, n in ((200, 'A'), (1400, 'B')):
        for sg in (-1, 1):
            sh.text(T.X(x) + 2.2, T.Y(sg * 455) + 1, n, 'lbl', 'start')
    T.cmark(1400, 0, 40)
    yt = T.Y(438) - 5
    for (u1, u2) in ((0, 300), (300, 775), (775, 825), (825, 1300), (1300, 1600)):
        T.hd(u1, 200, u2, 200, yt)
    yt2 = yt - 5
    for (u1, u2) in ((0, 50), (50, 150), (150, 1450), (1450, 1550), (1550, 1600)):
        T.hd(u1, 200, u2, 200, yt2)
    yb = T.Y(-438) + 4.5
    T.hd(0, -200, 200, -430, yb)
    T.hd(200, -430, 1250, -200, yb)
    T.hd(1250, -200, 1400, -125, yb)
    T.hd(1400, -125, PIV[0], -24, yb)
    T.vd(-200, -60, 200, -60, T.X(-60) - 3, '400')
    T.vd(-430, 175, 430, 175, T.X(-60) - 8, '860')
    T.vd(-150, 825, 150, 825, T.X(860), '300')
    T.vd(105, 1280, 155, 1280, T.X(1250) - 2, '50')
    T.note(1265, 130, -10, -9, 'P17 — posição final ajustada', 'end')
    T.note(1265, 130, -10, -6.6, 'p/ batente a ±35°', 'end')
    T.label(T.X(800), T.Y(-438) + 11.5, 'VISTA DE CIMA DO CHASSI — 1:10')

    # ---------------- cortes A-A e B-B
    for (oy, nome, xax) in ((84, 'A', AX[0]), (160, 'B', AX[1])):
        c = sh.view(312, oy, s)
        front = nome == 'B'
        c.line(-700, 0, 700, 0, 't')
        for sg in (-1, 1):
            c.rect(sg * 467, sg * 633, 0, 406, 'ph')
            c.rect(sg * 512, sg * 588, 160, 240, 'ph')
        zt = 255 if front else 275
        zb = 205 if front else 225
        for sg in (-1, 1):
            c.rect(sg * 430, sg * 438, 160, zt, 'pl')
            c.rect(sg * 438, sg * 510, 184, 216)
            c.rect(sg * 588, sg * 591, 180, 220, 'pl')
            c.line(sg * 605, 190, sg * 605, 210, 'v', 'stroke-width="0.8"')
        c.rect(-625, 625, 187.5, 212.5)
        c.tube(-430, 430, zb, zt)
        for sg in (-1, 1):
            c.tube(sg * 150, sg * 200, *CH)
        c.rect(-200, 200, *BPZ, 'pl')
        if front:
            c.rect(-200, 200, 269, 275, 'pl')
            c.rect(-125, 125, 261, 269, 'wf')
            c.rect(-125, 125, 255, 261, 'pl')
            c.rect(-8, 8, 202, 275)
            c.rect(-12, 12, 275, 285)
            c.rect(-14, 14, 199, 202, 'pl')
            c.rect(-12, 12, 186, 199)
        c.cmark(0, 250, 0) if False else c.line(0, 150, 0, 350, 'c')
        b = oy
        c.hd(-430, zb, 430, zb, b + 5, f'860 (P{4 if front else 3})')
        c.hd(-438, 160, 438, 160, b + 9.5, '876')
        c.hd(-550, 0, 550, 0, b + 14, '1100 (bitola)')
        c.hd(-625, AZ, 625, AZ, b + 18.5, '1250 (P15)')
        c.vd(0, -700, AZ, -625, c.X(-700) - 1.5, '200')
        c.vd(160, -438, zt, -438, c.X(-470) - 0.5, f'{zt - 160}')
        c.hd(438, 216, 510, 216, c.Y(216) - 1.8, '≈72')
        if front:
            c.hd(-125, 269, 125, 269, c.Y(300) - 3, 'Ø250 (C6 e K3)')
            c.hd(-200, 275, 200, 275, c.Y(300) - 7, '400 (C5)')
            for (u, w, dx, dy, n) in ((0, 280, 13, -10, 'K2'), (100, 265, 25, -3, 'K3'), (110, 258, 30, 2, 'C6'),
                                      (190, 272, 30, -6, 'C5'), (300, 230, 22, 5, 'P4'), (434, 175, -4, 9, 'C4'),
                                      (-470, 200, -3, 9, 'P16'), (-605, 200, -6, -8, 'K5')):
                c.bal(u, w, dx, dy, n)
        else:
            for (u, w, dx, dy, n) in ((300, 250, 22, -4, 'P3'), (434, 175, -4, 9, 'C3'), (-470, 200, -3, 9, 'P16'),
                                      (-605, 200, -6, -8, 'K5'), (-300, AZ, -3, -9, 'P15')):
                c.bal(u, w, dx, dy, n)
        c.label(312, b + 25, f'CORTE {nome}-{nome} — EIXO {"DIANTEIRO (DIREÇÃO, no pino-rei)" if front else "TRASEIRO"} — 1:10')

    # ---------------- chapas (detalhes)
    sh.text(16, 226, 'DETALHES DAS CHAPAS', 'lbl')

    def plate(ox, oy, sc, w, h, holes, name, sub, dims=True):
        p = sh.view(ox, oy, sc)
        p.rect(0, w, 0, h, 'pl')
        for (hx, hy, d) in holes:
            p.circ(hx, hy, d / 2, 'hole')
            p.cmark(hx, hy, d / 2 + 6)
        if dims:
            p.hd(0, 0, w, 0, oy + 3.5)
            p.vd(0, 0, h, 0, ox - 2.5)
        sh.text(ox, oy - h * sc - 3.5, name, 'sm', extra='font-weight="bold"')
        sh.text(ox, oy - h * sc - 1.3, sub, 'xs')
        return p

    p = plate(22, 276, 0.2, 80, 115, [(40, 40, 25.5)], 'C3 — mancal traseiro', '#8 · ×2 · 1:5')
    p.vd(0, 80, 40, 40, p.X(80) + 2.5, '40')
    p.note(52, 52, 6, -3, 'Ø25,5')
    p = plate(48, 276, 0.2, 105, 95, [(40, 40, 25.5)], 'C4 — mancal dianteiro', '#8 · ×2 · 1:5')
    p.vd(0, 105, 40, 40, p.X(105) + 2.5, '40')
    p.hd(0, 0, 40, 40, 276 + 7.5, '40')
    p.note(52, 52, 6, -3, 'Ø25,5')
    p = plate(80, 276, 0.2, 100, 60, [(70, 30, 16.5)], 'C7 — garfo da lança', '#8 · ×2 · 1:5')
    p.hd(70, 30, 100, 0, 276 + 7.5, '30')
    p.vd(0, 100, 30, 70, p.X(100) + 2.5, '30')
    p.note(76, 36, 5, -3, 'Ø16,5')
    p = plate(112, 276, 0.1, 400, 300, [(200, 150, 17)], 'C5 — chapa do pino-rei', '#6 · ×1 · 1:10 · soldar sob P1')
    p.hd(0, 150, 200, 150, p.Y(150) - 1.5, '200')
    p.note(200, 150, 6, -6, 'Ø17 (centro)')
    p = sh.view(172, 263.5, 0.1)
    p.circ(0, 0, 125, 'pl')
    p.circ(0, 0, 8.5, 'hole')
    p.cmark(0, 0, 140)
    p.hd(-125, 0, 125, 0, 276 + 3.5, 'Ø250')
    sh.text(159.5, 245.2, 'C6 — disco do pino-rei', 'sm', extra='font-weight="bold"')
    sh.text(159.5, 247.4, '#6 · ×1 · 1:10 · furo Ø17 · soldar sobre P4', 'xs')
    sh.para(196, 256, ['P17 — batente de giro', 'tubo 30×30×3 · L50 · ×2', 'soldar sob C5 (ver vista', 'de cima); posição final', 'na montagem: ±35°'], dy=2.6, cls='xs')
    sh.para(196, 272, ['K3 — disco PEAD/UHMW', 'Ø250 × 8 · furo Ø17', '(comprado / torneado)'], dy=2.6, cls='xs')

    # ---------------- notas
    sh.para(236, 196, [
        '# COTAS DE ALTURA (do chão)',
        '160 = base dos mancais C3 / C4 · 200 = eixo das rodas P15',
        '205 a 255 = viga P4 · 255 a 261 = disco C6 · 261 a 269 = disco PEAD K3',
        '269 a 275 = chapa C5 · 225 a 275 = viga P3 · 275 a 325 = longarinas P1',
        '325 a 333 = chapas base C1 · 333 = pé do mastro P9',
        '# MONTAGEM DA DIREÇÃO',
        '1. C5 soldada sob as longarinas; C6 soldada sobre a viga P4 (centrada).',
        '2. Pino-rei K2 (M16 inox) de cima p/ baixo: C5 › K3 › C6 › P4, porca travante.',
        '   Apertar até encostar e voltar 1/6 de volta: girar livre, sem folga vertical.',
        '3. P4 recebe bucha interna (tubo Ø22×2,5, L44) no furo Ø17 p/ não amassar.',
        '4. Eixo dianteiro 40 mm ATRÁS do pino-rei (furo de C4 deslocado): a roda segue a lança.',
        '5. Eixos P15 fixos; rodas giram no próprio rolamento. Cortar P16 após medir o cubo.',
    ], dy=3.0, cls='xs')
    return sh


# ================================================================ FOLHA 3
def folha3():
    sh = Sheet(3, 'Folha 3 — Mastros, travessas e berços', '1:10 (indicadas)')
    s = 0.1
    # ---------------- quadro de ponta (vista posterior)
    Z0 = 200
    q = sh.view(112, Z0, s)
    q.line(-800, 0, 800, 0, 't')
    sh.text(q.X(-790), Z0 - 0.8, 'nível do chão (referência)', 'xs')
    q.rect(-150, 150, *CH)
    for sg in (-1, 1):
        q.tube(sg * 150, sg * 200, *CH)
    q.rect(-200, 200, *BPZ, 'pl')
    q.rect(-25, 25, MZ[0], MZ[1])
    q.rect(-25, 25, MZ[1], MZ[1] + 3, 'pl')
    for sg in (-1, 1):
        q.poly([(sg * 25, 333), (sg * 175, 333), (sg * 25, 483)])
    for c in TIERS:
        q.rect(-750, 750, c - 20, c + 20)
        for sg in (-1, 1):
            q.rect(sg * 750, sg * 758, c - 22, c + 22, 'wh')
            cradle_sec(q, sg * KY, c)
            for yb in (sg * 250, sg * 550):
                q.line(yb, c - 26, yb, c + 25, 'h')
                q.rect(yb - 7, yb + 7, c - 26, c - 20, 'wh')
    xl = q.X(-760)
    for i, c in enumerate(TIERS):
        q.vd(0, -800, c, -750, xl - 3 - 4.5 * i, f'{c}')
    q.vd(0, -800, MZ[1], -25, xl - 16.5, '1500')
    q.hd(-750, TIERS[2] + 20, 750, TIERS[2] + 20, q.Y(1535) - 3, '1500 (P10)')
    q.hd(-KY, 1535, KY, 1535, q.Y(1535) - 8, '800 (eixo dos berços)')
    q.hd(-550, 1460, 550, 1460, q.Y(1535) - 13, '1100 (furos externos)')
    q.hd(-250, 1460, 250, 1460, q.Y(1535) - 18, '500 (furos internos)')
    q.hd(-200, CH[0], 200, CH[0], q.Y(CH[0]) + 4, '400 (C1)')
    for (u, w, dx, dy, n) in ((0, 1250, 9, -6, 'P9'), (-600, 960, -6, -7, 'P10'), (-754, 480, -5, 6, 'K10'),
                              (-400, TIERS[0] + 70, -10, -10, 'K6'), (-500, TIERS[0] + 22, -14, 6, 'C9'),
                              (100, 380, 9, -3, 'C2'), (150, 329, 9, 6, 'C1'), (0, 1501, 6, -5, 'C8'), (-550, TIERS[1] - 23, 6, 7, 'K8')):
        q.bal(u, w, dx, dy, n)
    q.label(112, Z0 + 8, 'QUADRO DE PONTA — VISTA POSTERIOR — 1:10')
    sh.text(112, Z0 + 11.5, 'Quadro dianteiro idêntico. Viga porta-caixa (folha 4) omitida.', 'xs', 'middle')

    # ---------------- mastro P9
    m = sh.view(207, q.Y(MZ[0]), s)
    L9 = MZ[1] - MZ[0]
    m.rect(0, 100, 0, L9)
    for hc in (c - MZ[0] for c in TIERS):
        m.rect(29.5, 70.5, hc - 20.5, hc + 20.5, 'wf')
        m.cmark(50, hc, 32)
    xr = m.X(100)
    for i, c in enumerate(TIERS):
        hc = c - MZ[0]
        m.vd(0, 100, hc, 70.5, xr + 3 + 4.5 * i, f'{hc}')
    m.vd(0, 100, L9, 100, xr + 16.5, f'{L9}')
    m.hd(0, 0, 100, 0, m.Y(0) + 4)
    m.hd(29.5, TIERS[2] - MZ[0] + 20.5, 70.5, TIERS[2] - MZ[0] + 20.5, m.Y(L9) - 3, '41')
    sh.para(m.X(0) - 1, m.Y(L9) - 18, ['P9 — MASTRO (×2)', 'tubo 100×50×3 · L1167', '3 janelas 41×41 nas', 'faces de 100 (passantes)'], dy=2.5, cls='xs')
    m.label(m.X(50) + 6, m.Y(0) + 9, 'P9 — 1:10')

    # ---------------- vista lateral dos mastros 1:20
    sl = sh.view(265, 108, 0.05)
    sl.rect(0, 1600, *CH)
    for (b1, b2) in BP:
        sl.rect(b1, b2, *BPZ, 'pl')
    for (m1, m2) in MAST:
        sl.rect(m1, m2, *MZ)
        for c in TIERS:
            xm = (m1 + m2) / 2
            sl.rect(xm - 75, xm + 75, c + 20, c + 95, 'eva')
            sl.rect(xm - 20, xm + 20, c - 20, c + 20)
    sl.rect(150, 1450, 1450, 1500)
    sl.poly([(150, 333), (300, 333), (150, 483)])
    sl.poly([(1450, 333), (1300, 333), (1450, 483)])
    sl.rect(-100, 50, *P7Z, 'h')
    sl.rect(0, 50, 333, 405, 'h')
    sl.hd(150, 1500, 1450, 1500, sl.Y(1535) - 3, '1300 (P6)')
    sl.hd(MAST[0][0], CH[0], MAST[1][1], CH[0], sl.Y(CH[0]) + 4, '1500 (face externa dos mastros)')
    sl.hd(150, 333, 300, 333, sl.Y(333) - 9, '150')
    sl.vd(1450, 1450, 1500, 1450, sl.X(1450) - 2, '50')
    sl.bal(800, 1475, 0, 6, 'P6')
    sl.bal(225, 380, 8, -4, 'C2')
    sl.label(sl.X(800), sl.Y(CH[0]) + 10, 'VISTA LATERAL DOS MASTROS — 1:20')

    # ---------------- travessa P10
    tv = sh.view(330, 134, s)
    tv.rect(-750, 750, -20, 20)
    for yb in (-550, -250, 250, 550):
        tv.circ(yb, 0, 4.25, 'hole')
    tv.line(-25, -30, -25, 30, 'h')
    tv.line(25, -30, 25, 30, 'h')
    tv.line(0, -35, 0, 35, 'c')
    tv.hd(-750, -20, 750, -20, tv.Y(-20) + 4, '1500')
    tv.hd(-550, 0, 550, 0, tv.Y(20) - 2.5, '1100')
    tv.hd(-250, 0, 250, 0, tv.Y(20) - 6.5, '500')
    sh.text(330, tv.Y(-20) + 8.5, 'P10 — TRAVESSA 40×40×3 (×6) — VISTA DE CIMA 1:10', 'lbl', 'middle')
    sh.text(330, tv.Y(-20) + 11.5, '4 furos Ø8,5 verticais · passa centrada pelo mastro (faces tracejadas) · solda contínua nas 2 faces', 'xs', 'middle')

    # ---------------- detalhe berço 1:5
    b = sh.view(300, 178, 0.2)
    b.rect(-230, 230, -20, 20)
    b.brk_v(-230, -20, 20)
    b.brk_v(230, -20, 20)
    cradle_sec(b, 0, 0)
    b.sh.a(f'<path class="ph" d="M{b.X(-280):.2f},{b.Y(120):.2f} Q{b.X(-280):.2f},{b.Y(62):.2f} {b.X(0):.2f},{b.Y(62):.2f} '
           f'Q{b.X(280):.2f},{b.Y(62):.2f} {b.X(280):.2f},{b.Y(120):.2f}"/>')
    for yb in (-150, 150):
        b.line(yb, -28, yb, 40, 'h')
        b.rect(yb - 7, yb + 7, -28, -20, 'wh')
        b.rect(yb - 7, yb + 7, 25, 31, 'h')
    b.hd(-200, 95, 200, 95, b.Y(95) - 3, '400 (C9 e K6)')
    b.hd(-150, -28, 150, -28, b.Y(-28) + 3.5, '300 (furos Ø8,5)')
    b.vd(25, 200, 95, 200, b.X(200) + 3, '70')
    b.vd(25, 0, 60, 0, b.X(0) + 1.5, '35')
    b.vd(20, -200, 25, -200, b.X(-200) - 2, '5')
    b.note(-120, 40, -12, -6, 'K6 EVA alta densidade colado (cola PU)', 'end')
    b.note(-60, 22, -18, 9, 'C9 chapa #5 · 400×150 · ×12', 'end')
    b.note(150, -24, 8, 4, 'K8 M8 inox c/ arruela nylon', 'start')
    b.note(150, 10, 10, 2, 'bucha interna L34 (K12)', 'start')
    b.label(300, 196, 'DETALHE A — BERÇO 1:5 (×12) · largura 150')

    # ---------------- C1 e C2
    c1 = sh.view(372, 236, 0.1)
    c1.rect(-200, 200, 0, 300, 'pl')
    c1.rect(-25, 25, 50, 150, 'h')
    c1.line(-3, 150, -3, 300, 'h')
    c1.line(3, 150, 3, 300, 'h')
    for sg in (-1, 1):
        c1.line(sg * 25, 97, sg * 175, 97, 'h')
    c1.hd(-200, 0, 200, 0, 236 + 3.5, '400')
    c1.vd(0, -200, 300, -200, c1.X(-200) - 2.5, '300')
    c1.vd(0, 200, 50, 25, c1.X(200) + 2.5, '50')
    c1.vd(50, 200, 150, 25, c1.X(200) + 6, '100')
    sh.text(352, 202, 'C1 — base do mastro #8 ×2 (1:10)', 'xs', extra='font-weight="bold"')
    sh.text(352, 204.2, 'tracejado = mastro e mãos-francesas', 'xs')
    c2 = sh.view(254, 240, 0.2)
    c2.poly([(0, 0), (150, 0), (0, 150)], 'pl')
    c2.sh.a(f'<rect x="{c2.X(0):.2f}" y="{c2.Y(15):.2f}" width="{15 * 0.2:.2f}" height="{15 * 0.2:.2f}" fill="#fff" stroke="none"/>')
    c2.line(0, 15, 15, 0, 'v')
    c2.hd(0, 0, 150, 0, 240 + 3.5, '150')
    c2.vd(0, 0, 150, 0, c2.X(0) - 2.5, '150')
    c2.note(7, 7, -8, 3, 'chanfro 15', 'end')
    sh.text(254, 206.5, 'C2 — mão-francesa', 'xs', extra='font-weight="bold"')
    sh.text(254, 208.7, '#6 · ×6 · 1:5', 'xs')

    sh.para(16, 222, [
        '# MONTAGEM DOS MASTROS',
        '1. Soldar C1 sobre as longarinas (posições na folha 2). Mastro P9 sobre C1, no prumo (≤ 1 mm/m) nos dois sentidos.',
        '2. Mãos-francesas C2: traseiro = 1 à frente + 2 laterais; dianteiro = 1 atrás + 2 laterais (total 6).',
        '3. Travessas P10 passam pelas janelas do mastro, centradas (diferença entre as pontas ≤ 2 mm), niveladas;',
        '   solda contínua em volta da travessa nas DUAS faces do mastro. Tampa C8 soldada no topo (mastro estanque).',
        '4. Viga superior P6 soldada de topo entre os mastros, conferindo 1300 entre faces em cima e embaixo.',
        '5. Berços: EVA K6 colado em C9; C9 parafusado na travessa com M8 + bucha interna (não esmagar o tubo).',
        '6. Furos Ø8,5 das travessas: fazer ANTES de soldar. Rebarbar tudo que encosta no caiaque.',
    ], dy=3.1, cls='xs')
    return sh


# ================================================================ FOLHA 4
def folha4():
    sh = Sheet(4, 'Folha 4 — Porta-caixa, caixa e lança', '1:10 (indicadas)')
    s = 0.1
    # ---------------- conjunto porta-caixa
    v = sh.view(190, 124, s)
    v.rect(0, 200, *CH)
    v.brk_v(200, CH[0], CH[1])
    v.rect(0, 220, *BPZ, 'pl')
    v.rect(50, 150, MZ[0], 1000)
    v.brk_h(1000, 50, 150)
    for c in TIERS[:2]:
        v.rect(80, 120, c - 20, c + 20)
        v.line(80, c - 20, 120, c + 20, 't')
    v.poly([(150, 333), (220, 333), (150, 403)])
    v.rect(0, 50, 333, 405)
    v.rect(*P7X, *P7Z)
    v.poly(tie_poly())
    v.rect(BOX[0], BOX[1], *BOXZ, 'vf', 'style="fill:url(#furos)"')
    v.rect(BOX[0] - 5, BOX[1] + 5, BOXZ[1] - 20, BOXZ[1] + 2, 'pl')
    v.rect(BOX[0], BOX[0] + 25, BOXZ[0], BOXZ[1] - 20, 'v')
    v.rect(BOX[1] - 25, BOX[1], BOXZ[0], BOXZ[1] - 20, 'v')
    for xr in (-1575, -1050):
        v.tube(xr, xr + 25, 455, 480, 2)
    for xb in (-1562, -1038):
        v.line(xb, 395, xb, 492, 'h')
        v.rect(xb - 7, xb + 7, 395, 405, 'wh')
    v.circ(BOX[0] - 5, BOXZ[1] - 5, 8, 'wh')
    v.rect(BOX[1] + 5, BOX[1] + 15, BOXZ[1] - 50, BOXZ[1] - 10, 'wh')
    L, a = tie_len()
    yr = v.Y(CH[0]) - 1
    v.hd(P7X[0], P7Z[0], -1562, 405, yr + 5, '88')
    v.hd(-1562, 405, -1038, 405, yr + 5, '524')
    v.hd(TIE[1][0], P7Z[1], 50, P7Z[0], yr + 5, '1000')
    v.hd(P7X[0], P7Z[0], BOX[0], P7Z[0], yr + 10, '50')
    v.hd(BOX[0], P7Z[0], BOX[1], P7Z[0], yr + 10, '600 (caixa)')
    v.hd(BOX[1], P7Z[0], 50, P7Z[0], yr + 10, '1050')
    v.hd(P7X[0], P7Z[0], 50, P7Z[0], yr + 15, '1700 (P7)')
    v.vd(BPZ[1], 0, P7Z[0], 0, v.X(0) - 2, '72')
    v.vd(*P7Z[:1], -1650, P7Z[1], -1650, v.X(-1650) - 2.5, '50')
    v.vd(455, BOX[0], 480, BOX[0], v.X(BOX[0]) - 2.5, '25')
    v.vd(BOXZ[0], BOX[0], BOXZ[1], BOX[0], v.X(BOX[0]) - 2.5, '300')
    v.vd(BPZ[1], 150, TIE[0][1], 50, v.X(150) + 4, f'{TIE[0][1] - BPZ[1]}')
    sh.text(v.X(-700), v.Y(505), f'P11 ≈ {L:.0f} (eixo) · α ≈ {a:.0f}°', 'xs')
    sh.text(v.X(-820), v.Y(462), 'α', 'sm')
    v.line(-950, 455, -720, 455, 't')
    for (u, w, dx, dy, n) in ((-400, 430, 0, 8, 'P7'), (25, 370, -9, 3, 'P8'), (-300, 600, 3, -9, 'P11'),
                              (-1562, 467, -8, 6, 'P19'), (BOX[0] + 100, 770, -3, -9, 'C11'), (-1300, 600, 4, -14, 'C10'),
                              (BOX[1] - 12, 600, 8, -10, 'P20'), (-1200, 782, 6, -12, 'P18'), (BOX[0] - 5, 775, -6, -8, 'K11'),
                              (-1038, 400, 5, 6, 'K8'), (100, 800, 8, -4, 'P9')):
        v.bal(u, w, dx, dy, n)
    v.label(115, yr + 22, 'CONJUNTO PORTA-CAIXA — VISTA LATERAL — 1:10')

    # ---------------- planificação da caixa
    pc = sh.view(80, 200, s)
    pts = [(-300, -475), (300, -475), (300, -175), (600, -175), (600, 175), (300, 175), (300, 475),
           (-300, 475), (-300, 175), (-600, 175), (-600, -175), (-300, -175)]
    pc.poly(pts, 'vf', 'style="fill:url(#furos)"')
    for sgx in (-1, 1):
        pc.line(sgx * 300, -175, sgx * 300, 175, 'h')
    for sgy in (-1, 1):
        pc.line(-300, sgy * 175, 300, sgy * 175, 'h')
        for sgx in (-1, 1):
            pc.circ(sgx * 300, sgy * 175, 4, 'hole')
    for (u, w, t) in ((0, 0, 'FUNDO 600×350'), (0, 325, 'LATERAL'), (0, -325, 'LATERAL'), (-450, 0, 'TESTEIRA'), (450, 0, 'TESTEIRA')):
        sh.a(f'<rect x="{pc.X(u) - 9:.2f}" y="{pc.Y(w) - 2:.2f}" width="18" height="3" fill="#fff" opacity="0.85"/>')
        sh.text(pc.X(u), pc.Y(w) + 0.5, t, 'xs', 'middle')
    pc.hd(-600, 175, 600, 175, pc.Y(475) - 7, '1200')
    pc.hd(-600, 175, -300, 475, pc.Y(475) - 2.5, '300')
    pc.hd(-300, 475, 300, 475, pc.Y(475) - 2.5, '600')
    pc.hd(300, 475, 600, 175, pc.Y(475) - 2.5, '300')
    pc.vd(-475, 300, 475, 300, pc.X(600) + 7, '950')
    pc.vd(-475, 300, -175, 600, pc.X(600) + 2.5, '300')
    pc.vd(-175, 600, 175, 600, pc.X(600) + 2.5, '350')
    pc.vd(175, 600, 475, 300, pc.X(600) + 2.5, '300')
    sh.text(80, pc.Y(-475) + 4.5, 'C10 — CORPO DA CAIXA (planificação) 1:10', 'lbl', 'middle')
    sh.text(80, pc.Y(-475) + 7.5, 'chapa perfurada 2 mm (furo Ø10, passo 15) · dobrar 4 abas 90° p/ cima · alívios Ø8 nos cantos', 'xs', 'middle')

    # ---------------- tampa
    tp = sh.view(185, 165, s)
    pts = [(-305, -200), (305, -200), (305, -180), (325, -180), (325, 180), (305, 180), (305, 200),
           (-305, 200), (-305, 180), (-325, 180), (-325, -180), (-305, -180)]
    tp.poly(pts, 'vf', 'style="fill:url(#furos)"')
    tp.line(-305, -180, -305, 180, 'h')
    tp.line(305, -180, 305, 180, 'h')
    tp.line(-305, 180, 305, 180, 'h')
    tp.line(-305, -180, 305, -180, 'h')
    tp.hd(-325, 180, 325, 180, tp.Y(200) - 3, '650')
    tp.vd(-200, 325, 200, 325, tp.X(325) + 3, '400')
    tp.hd(305, 200, 325, 180, tp.Y(200) - 7, '20')
    sh.text(185, tp.Y(-200) + 4.5, 'C11 — TAMPA (planif.) 1:10', 'lbl', 'middle')
    sh.text(185, tp.Y(-200) + 7.3, 'abas de 20 dobradas p/ baixo · dobradiça piano', 'xs', 'middle')
    sh.text(185, tp.Y(-200) + 9.8, 'K11 na testeira externa (lado x = −1600)', 'xs', 'middle')

    # ---------------- lança (vista de cima)
    ln = sh.view(250, 56, s)
    D = math.hypot(HANDLE[0] - PIV[0], HANDLE[1] - PIV[1])
    ln.rect(-15, 15, -24, 24)
    ln.line(-8.25, -24, -8.25, 24, 'h')
    ln.line(8.25, -24, 8.25, 24, 'h')
    ln.rect(15, D - 19, -19, 19)
    ln.rect(D - 19, D + 19, -250, 250)
    for sg in (-1, 1):
        ln.rect(D - 22, D + 22, sg * 120, sg * 250, 'wh')
    ln.line(-30, 0, D + 40, 0, 'c')
    ln.hd(0, -24, D, -250, ln.Y(-250) + 4, f'{D:.0f} (eixo do pino → eixo da manopla)')
    ln.hd(15, 19, D - 19, 19, ln.Y(19) - 3, f'≈{D - 34:.0f} (P12, boca-de-lobo nas 2 pontas)')
    ln.vd(-250, D + 19, 250, D + 19, ln.X(D + 19) + 3, '500 (P13)')
    ln.vd(120, D + 22, 250, D + 22, ln.X(D + 22) + 7.5, '130')
    ln.vd(-24, -15, 24, -15, ln.X(-15) - 2.5, '48')
    ln.bal(0, 24, -4, -6, 'P14')
    ln.bal(700, 0, 0, 8, 'P12')
    ln.bal(D, 60, -8, -5, 'P13')
    ln.bal(D, -185, -8, 4, 'K9')
    sh.text(330, ln.Y(-250) + 9.5, 'LANÇA — VISTA DE CIMA 1:10', 'lbl', 'middle')
    sh.text(330, ln.Y(-250) + 12.5, 'Manopla P13 soldada a 90° e PARALELA ao furo da bucha P14 (eixo do pino).', 'xs', 'middle')

    # ---------------- articulação 1:5
    ar = sh.view(250 - 1560 * 0.2, 112, 0.2)
    ar.rect(1560, 1625, -25, 25)
    ar.brk_v(1560, -25, 25)
    for sg in (-1, 1):
        ar.rect(1595, 1695, sg * 25, sg * 33, 'pl')
    ar.rect(1650, 1680, -24, 24, 'wf')
    ar.rect(1680, 1740, -19, 19)
    ar.brk_v(1740, -19, 19)
    ar.rect(1657, 1673, -47, 47)
    ar.circ(1665, -55, 7, 'v')
    ar.vd(-25, 1700, 25, 1700, ar.X(1745) + 2, '50')
    ar.hd(1595, 33, 1695, 33, ar.Y(47) - 2.5, '100')
    ar.hd(1665, 33, 1695, 33, ar.Y(47) - 6.5, '30')
    ar.note(1665, 44, 8, -2, 'K4 pino Ø16 inox + trava R', 'start')
    ar.note(1695, -29, 6, 6, 'C7 #8 (×2) soldado nas laterais de P5', 'start')
    ar.note(1665, 10, 16, 4, 'P14 bucha Ø30×48, furo Ø16,5', 'start')
    ar.note(1590, 0, -2, 11, 'P5 braço 50×50×3 L200', 'end')
    sh.text(285, 129, 'DETALHE B — ARTICULAÇÃO DA LANÇA 1:5 (vista de cima)', 'lbl', 'middle')

    # ---------------- tirante P11
    ti = sh.view(262, 148, s)
    k = math.tan(math.radians(a))
    Lc = L
    pts = [(30 / 2 / k, 15), (Lc - 15 * k, 15), (Lc + 15 * k, -15), (-30 / 2 / k, -15)]
    ti.poly(pts, 'vf')
    ti.line(-60, 0, Lc + 40, 0, 'c')
    ti.hd(0, 0, Lc, 0, ti.Y(-15) + 4, f'≈{Lc:.0f} (no eixo)')
    sh.text(ti.X(0) - 2, ti.Y(15) - 1.5, f'corte {a:.0f}° (apoia na viga P7)', 'xs')
    sh.text(ti.X(Lc) + 1, ti.Y(15) - 1.5, f'corte {90 - a:.0f}° (face do mastro)', 'xs', 'end')
    sh.text(ti.X(Lc / 2), ti.Y(-15) + 9, 'P11 — TIRANTE 30×30×3 (×1) 1:10 · traçar no gabarito com a carreta montada', 'lbl', 'middle')

    sh.para(236, 172, [
        '# MONTAGEM DO PORTA-CAIXA E CAIXA',
        '1. P7 soldada na face traseira do mastro (3 lados) e sobre o calço P8;',
        '   2 furos Ø8,5 verticais (cotas 88 / 524) com bucha interna L44 (K12).',
        '2. P11 soldado no mastro (z 900) e sobre P7 a 1000 da face do mastro.',
        '3. Caixa: dobrar C10; cantos internos com P20 (3 rebites por aba);',
        '   borda superior P18 (cantos 45°) rebitada; base P19 (tubo 25×25×2)',
        '   rebitada sob o fundo e parafusada em P7 com K8.',
        '4. Tampa C11 com dobradiça piano K11 na testeira externa, fecho inox',
        '   na testeira do lado do mastro. Rebites pop alumínio Ø4,8.',
        '5. CONFERIR com os caiaques montados: folga ≥ 30 mm entre a caixa e',
        '   as popas do nível de baixo. Se faltar, reduzir largura p/ 300.',
        '# LANÇA',
        '6. Bucha P14 soldada na ponta do tubo P12 (boca-de-lobo Ø30);',
        '   manopla P13 soldada na outra ponta (boca-de-lobo Ø38).',
    ], dy=2.9, cls='xs')
    return sh


# ================================================================ FOLHA 5
def folha5():
    sh = Sheet(5, 'Folha 5 — Lista de corte, compras e fabricação', 'sem escala')
    L, a = tie_len()
    sh.text(16, 18, 'LISTA DE CORTE — PERFIS E CHAPAS (alumínio 6061-T6 salvo indicação)', 'lbl')
    rows = [('Marca', 'Peça', 'Perfil / material', 'Medida', 'Qtd', 'Cortes / furos / observação', 'Fl.'),
            ('P1', 'Longarina do chassi', 'Tubo 50×50×3', '1600', '2', 'corte 90°; pontas com tampão K10', '2'),
            ('P2', 'Travessa do chassi', 'Tubo 50×50×3', '300', '3', '90°; entre as longarinas', '2'),
            ('P3', 'Viga do eixo traseiro', 'Tubo 50×50×3', '860', '1', '90°; soldada sob P1', '2'),
            ('P4', 'Viga do eixo dianteiro', 'Tubo 50×50×3', '860', '1', '90°; furo Ø17 vertical no centro', '2'),
            ('P5', 'Braço da lança', 'Tubo 50×50×3', '200', '1', '90°; soldado na frente de P4', '2/4'),
            ('P6', 'Viga superior', 'Tubo 50×50×3', '1300', '1', '90°; ajustar entre mastros', '3'),
            ('P7', 'Viga porta-caixa', 'Tubo 50×50×3', '1700', '1', '2 furos Ø8,5 verticais; tampão na ponta', '4'),
            ('P8', 'Calço da viga', 'Tubo 50×50×3', '72', '1', '90°', '4'),
            ('P9', 'Mastro', 'Tubo 100×50×3', '1167', '2', '3 janelas 41×41 passantes (faces de 100)', '3'),
            ('P10', 'Travessa porta-caiaque', 'Tubo 40×40×3', '1500', '6', '4 furos Ø8,5 verticais; tampões K10', '3'),
            ('P11', 'Tirante', 'Tubo 30×30×3', f'≈{L:.0f}', '1', f'cortes {a:.0f}° / {90 - a:.0f}° — traçar no gabarito', '4'),
            ('P12', 'Lança', 'Tubo Ø38×3', '≈1460', '1', 'boca-de-lobo Ø30 e Ø38', '4'),
            ('P13', 'Manopla T', 'Tubo Ø38×3', '500', '1', '90°; pegas K9', '4'),
            ('P14', 'Bucha da lança', 'Barra redonda Ø30', '48', '1', 'furo Ø16,5 passante', '4'),
            ('P15', 'Eixo das rodas', 'Barra inox 304 Ø25', '1250', '2', 'furo Ø5 a 20 de cada ponta (cupilha)', '2'),
            ('P16', 'Espaçador de roda', 'Tubo inox Ø32×3,5', '≈72', '4', 'cortar após medir o cubo da roda', '2'),
            ('P17', 'Batente de giro', 'Tubo 30×30×3', '50', '2', 'posição final na montagem (±35°)', '2'),
            ('P18', 'Borda superior da caixa', 'Cantoneira 25×25×3', '600 / 350', '2+2', 'cantos 45°', '4'),
            ('P19', 'Base da caixa', 'Tubo 25×25×2', '350', '2', 'furo Ø8,5 central vertical', '4'),
            ('P20', 'Canto da caixa', 'Cantoneira 25×25×3', '300', '4', '90°', '4'),
            ('C1', 'Base do mastro', 'Chapa #8', '400×300', '2', '—', '3'),
            ('C2', 'Mão-francesa', 'Chapa #6', '150×150 triâng.', '6', 'chanfro 15 no canto reto', '3'),
            ('C3', 'Mancal traseiro', 'Chapa #8', '80×115', '2', 'furo Ø25,5 (40 da base)', '2'),
            ('C4', 'Mancal dianteiro', 'Chapa #8', '105×95', '2', 'furo Ø25,5 (40 da base / 40 da borda tras.)', '2'),
            ('C5', 'Chapa do pino-rei', 'Chapa #6', '400×300', '1', 'furo Ø17 no centro', '2'),
            ('C6', 'Disco do pino-rei', 'Chapa #6', 'Ø250', '1', 'furo Ø17 no centro', '2'),
            ('C7', 'Garfo da lança', 'Chapa #8', '100×60', '2', 'furo Ø16,5', '2/4'),
            ('C8', 'Tampa do mastro', 'Chapa #3', '100×50', '2', 'solda contínua (mastro estanque)', '3'),
            ('C9', 'Base do berço', 'Chapa #5', '400×150', '12', '2 furos Ø8,5 (passo 300)', '3'),
            ('C10', 'Corpo da caixa', 'Chapa perfurada #2', '1200×950 planif.', '1', 'dobrar 4 abas 90°', '4'),
            ('C11', 'Tampa da caixa', 'Chapa perfurada #2', '650×400 planif.', '1', 'abas 20', '4')]
    y = sh.table(15, 21, (10, 42, 36, 27, 9, 76, 8), rows, rh=4.55, cls='sm')

    sh.text(16, y + 5, 'COMPRA DE MATERIAL BRUTO (com sobra p/ corte)', 'lbl')
    rows2 = [('Material', 'Necessário', 'Comprar'),
             ('Tubo alum. 50×50×3', '9,1 m', '2 barras de 6 m'),
             ('Tubo alum. 100×50×3', '2,4 m', '1 barra de 3 m'),
             ('Tubo alum. 40×40×3', '9,0 m', '2 barras de 6 m'),
             ('Tubo alum. 30×30×3', '1,2 m', '1 barra (retalho)'),
             ('Tubo alum. Ø38×3', '2,0 m', '1 barra de 3 m'),
             ('Cantoneira 25×25×3 + tubo 25×25×2', '3,1 m + 0,7 m', '1 barra de cada'),
             ('Barra inox 304 Ø25', '2,5 m', '1 barra de 3 m'),
             ('Chapa alum. #8 / #6 / #5', '0,29 / 0,24 / 0,72 m²', 'conforme retalho'),
             ('Chapa alum. perfurada #2 (Ø10 p15)', '1200×950 + 650×400', '1 chapa 1250×2500')]
    sh.table(15, y + 7, (66, 46, 44), rows2, rh=4.3, cls='sm')

    sh.text(236, 18, 'ITENS COMPRADOS (K)', 'lbl')
    rows3 = [('Marca', 'Item', 'Qtd'),
             ('K1', 'Roda balão 16×6.50-8 c/ rolamento, furo Ø25', '4'),
             ('K2', 'Parafuso M16×100 inox A4 + porca travante + 2 arruelas', '1'),
             ('K3', 'Disco PEAD/UHMW Ø250×8, furo Ø17', '1'),
             ('K4', 'Pino engate Ø16×70 inox c/ trava R', '1'),
             ('K5', 'Cupilha inox 4×40 + arruela lisa Ø25 inox', '4+8'),
             ('K6', 'Bloco EVA alta densidade 400×150×70', '12'),
             ('K7', 'Cinta com fivela cam 25 mm × 3 m', '12'),
             ('K8', 'Parafuso M8×70 inox A4 + porca trav. + arr. nylon', '26'),
             ('K9', 'Manopla emborrachada p/ tubo Ø38', '2'),
             ('K10', 'Tampão plástico 40×40 (12) e 50×50 (5)', '17'),
             ('K11', 'Dobradiça piano inox 350 + fecho inox + rebites Ø4,8', '1 cj'),
             ('K12', 'Bucha interna tubo alum. Ø14×2 (L34 / L44)', '26')]
    y3 = sh.table(235, 21, (12, 147, 13), rows3, rh=4.4, cls='sm')

    y4 = sh.para(236, y3 + 6, [
        '# INSTRUÇÕES DE FABRICAÇÃO',
        'SOLDA: TIG CA, vareta ER5356 (ou ER4043). Filete contínuo a = 3 mm em todas as uniões estruturais.',
        'Escovar com escova de inox exclusiva e desengraxar antes de soldar. Tubos fechados e estanques',
        '(solda em todo o contorno; pontas abertas com tampão K10) p/ não acumular água salgada.',
        'CORROSÃO: inox × alumínio sempre isolado com arruela de nylon ou pasta isolante.',
        'ACABAMENTO: rebarbar todas as arestas; alumínio natural ou anodizado. Não usar aço carbono.',
        'TOLERÂNCIAS: comprimentos ±2; furos ±0,5; prumo dos mastros ≤ 1 mm/m; diagonais do chassi iguais ±2.',
    ], dy=3.4, cls='sm')
    sh.para(236, y4 + 2, [
        '# CONFERIR ANTES DE CORTAR (com o cliente)',
        '☐ Roda comprada: diâmetro (projeto 406, máx. 420), largura ≤ 165, furo Ø25, comprimento do cubo (≈75).',
        '☐ Caiaque mais largo: boca ≤ 600 mm · mais alto (casco + convés): ≤ 350 mm · comprimento ≤ 5,2 m.',
        '☐ Altura da manopla (≈ 900) confortável para quem puxa.',
        '☐ Teste final: 6 caiaques carregados, direção no batente (±35°): folga lança × casco e pneu × travessa ≥ 40.',
    ], dy=3.4, cls='sm')

    sh.para(16, 236, [
        '# SEQUÊNCIA DE MONTAGEM',
        '1. Chassi P1+P2 em gabarito plano; conferir diagonais.  2. P3 + mancais C3; C5 + batentes P17 (pontear).',
        '3. Chapas C1; mastros P9 no prumo; mãos-francesas C2.  4. Travessas P10 passantes; viga superior P6.',
        '5. Porta-caixa: P8, P7, tirante P11.  6. Eixo dianteiro: P4 + C4 + C6 + braço P5 + garfo C7.',
        '7. Lança P12 + bucha P14 + manopla P13.  8. Caixa C10/C11 + P18–P20 (rebitada), fixar em P7.',
        '9. Rodas, pino-rei com disco K3, berços, tampões e cintas.  10. Teste com carga (checklist ao lado).',
        'Peso estimado da carreta vazia ≈ 80 kg (sem caiaques e sem caixa cheia).',
    ], dy=3.5, cls='sm')
    return sh


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, f in enumerate((folha1, folha2, folha3, folha4, folha5), 1):
        with open(os.path.join(OUT, f'folha{i}.svg'), 'w') as fh:
            fh.write(f().svg())
    print('ok')


if __name__ == '__main__':
    main()
