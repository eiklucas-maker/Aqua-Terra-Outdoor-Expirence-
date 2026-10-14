#!/usr/bin/env python3
"""Gera a planta técnica (A3, SVG) da carreta porta-caiaques."""
import sys

S = 1 / 25  # escala principal 1:25 (mm reais -> mm no papel)
out = []
def a(s): out.append(s)

# ---------- estilos ----------
STYLE = """
<style>
 .v{fill:none;stroke:#000;stroke-width:0.45;stroke-linejoin:round}
 .vf{fill:#e9eef2;stroke:#000;stroke-width:0.45;stroke-linejoin:round}
 .wh{fill:#3a3a3a;stroke:#000;stroke-width:0.45}
 .t{fill:none;stroke:#000;stroke-width:0.18}
 .h{fill:none;stroke:#000;stroke-width:0.22;stroke-dasharray:1.2 0.8}
 .ph{fill:none;stroke:#1f5fa8;stroke-width:0.25;stroke-dasharray:4 0.8 0.8 0.8}
 .c{fill:none;stroke:#a00;stroke-width:0.15;stroke-dasharray:5 1 1 1}
 .d{fill:none;stroke:#000;stroke-width:0.15}
 .eva{fill:#f2b84b;stroke:#000;stroke-width:0.3}
 .perf{fill:#fff;stroke:#000;stroke-width:0.1}
 text{font-family:'DejaVu Sans',Arial,sans-serif;fill:#000}
 .dt{font-size:2.2px}
 .lbl{font-size:3.2px;font-weight:bold}
 .sm{font-size:1.9px}
 .tb{font-size:2.3px}
 .bal{fill:#fff;stroke:#000;stroke-width:0.2}
</style>
<defs>
 <marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.2" markerHeight="2.2" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,1.5 L10,5 L0,8.5 z" fill="#000"/></marker>
</defs>
"""

# ---------- utilidades de cota ----------
def dim_h(x1, x2, y, txt, yref1=None, yref2=None, up=True, toff=0):
    """Cota horizontal no papel. yref = y da peça (para linha de chamada)."""
    for x, yr in ((x1, yref1), (x2, yref2)):
        if yr is not None:
            sgn = -1 if y < yr else 1
            a(f'<line class="d" x1="{x:.2f}" y1="{yr + sgn*0.8:.2f}" x2="{x:.2f}" y2="{y + sgn*1.2:.2f}"/>')
    a(f'<line class="d" x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    a(f'<text class="dt" x="{(x1+x2)/2+toff:.2f}" y="{y-0.7:.2f}" text-anchor="middle">{txt}</text>')

def dim_v(y1, y2, x, txt, xref1=None, xref2=None):
    for yy, xr in ((y1, xref1), (y2, xref2)):
        if xr is not None:
            sgn = -1 if x < xr else 1
            a(f'<line class="d" x1="{xr + sgn*0.8:.2f}" y1="{yy:.2f}" x2="{x + sgn*1.2:.2f}" y2="{yy:.2f}"/>')
    a(f'<line class="d" x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    ym = (y1 + y2) / 2
    a(f'<text class="dt" x="{x-0.7:.2f}" y="{ym:.2f}" text-anchor="middle" transform="rotate(-90 {x-0.7:.2f} {ym:.2f})">{txt}</text>')

def balloon(x, y, n, tx, ty):
    a(f'<line class="d" x1="{x:.2f}" y1="{y:.2f}" x2="{tx:.2f}" y2="{ty:.2f}"/>')
    a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.5" fill="#000"/>' if False else '')
    a(f'<circle class="bal" cx="{tx:.2f}" cy="{ty:.2f}" r="2"/>')
    a(f'<text class="sm" x="{tx:.2f}" y="{ty+0.7:.2f}" text-anchor="middle" font-weight="bold">{n}</text>')
    a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.35" fill="#000"/>')

# ---------- geometria real (mm) ----------
L = 1600            # chassi (espinha central)
CHW = 200           # meia-largura do chassi (400 total, livra as rodas dianteiras no giro)
WB = (200, 1400)    # eixos traseiro / dianteiro
RW = 200            # raio roda (Ø400)
CH = (275, 325)     # tubo chassi 50x50
BOXES = ((-1600, -1000),)   # caixa de equipo traseira (x1,x2)
BZ = (480, 780)     # caixas na altura do caiaque de baixo
BHW = 175           # meia-largura das caixas (350)
BEAMS = ((-1650, 80),)      # viga porta-caixa, z 430..480
TIES = (((80, 860), (-950, 480)),)  # tirante
MAST_X = ((80, 120), (1480, 1520))
MAST_TOP = 1460
TIERS = (440, 920, 1400)      # eixo das travessas 40x40
BAR_HALF = 750
KY = 400            # centro do caiaque em y (±)
KW, KH = 560, 330   # boca / altura do caiaque
KX = (-2100, 2700)  # caiaque 4,8 m (fantasma)
PIV = (1650, 230)   # pino da lança
ELBOW = PIV        # lança reta
HANDLE = (3000, 900)
ZTOP = 1830         # topo dos caiaques (para cotas)

def perf(fx, fz, xa, xb, za, zb, step=40):
    for i in range(int(xa) + 30, int(xb) - 15, step):
        for j in range(int(za) + 30, int(zb) - 15, step):
            a(f'<circle class="perf" cx="{fx(i):.2f}" cy="{fz(j):.2f}" r="0.25"/>')

# ======================================================================
# VISTA LATERAL (principal)  — x real -> papel
X0, G1 = 101, 115   # origem x=0 ; linha de solo
px = lambda x: X0 + x * S
pz = lambda z: G1 - z * S

def rect_side(x1, x2, z1, z2, cls="v"):
    a(f'<rect class="{cls}" x="{px(x1):.2f}" y="{pz(z2):.2f}" width="{(x2-x1)*S:.2f}" height="{(z2-z1)*S:.2f}"/>')

a(f'<line class="v" x1="{px(-2150):.2f}" y1="{G1}" x2="{px(3100):.2f}" y2="{G1}"/>')
for i in range(0, 52):
    xx = px(-2150) + i * 4.1
    a(f'<line class="t" x1="{xx:.2f}" y1="{G1:.2f}" x2="{xx-1.5:.2f}" y2="{G1+1.5:.2f}"/>')

# rodas
for xw in WB:
    a(f'<circle class="wh" cx="{px(xw):.2f}" cy="{pz(RW):.2f}" r="{RW*S:.2f}"/>')
    a(f'<circle class="vf" cx="{px(xw):.2f}" cy="{pz(RW):.2f}" r="{120*S:.2f}"/>')
    a(f'<circle class="v" cx="{px(xw):.2f}" cy="{pz(RW):.2f}" r="{25*S:.2f}"/>')
    a(f'<line class="c" x1="{px(xw):.2f}" y1="{pz(RW+260):.2f}" x2="{px(xw):.2f}" y2="{pz(RW-260):.2f}"/>')
# suportes de eixo
rect_side(180, 220, 200, 275, "vf")
rect_side(1300, 1500, 245, 275, "vf")   # prato giratório
rect_side(1380, 1420, 200, 245, "vf")
# chassi
rect_side(0, L, *CH, "vf")
# mastros, viga superior, mãos-francesas
for (m1, m2) in MAST_X:
    rect_side(m1, m2, CH[1], MAST_TOP, "vf")
rect_side(120, 1480, MAST_TOP - 40, MAST_TOP, "vf")
for base, sgn in ((120, 1), (1480, -1)):
    a(f'<polygon class="vf" points="{px(base):.2f},{pz(CH[1]):.2f} {px(base+sgn*150):.2f},{pz(CH[1]):.2f} {px(base):.2f},{pz(CH[1]+150):.2f}"/>')
# vigas porta-caixa + tirantes
for (b1, b2) in BEAMS:
    rect_side(b1, b2, 430, 480, "vf")
for (p1, p2) in TIES:
    a(f'<line class="v" x1="{px(p1[0]):.2f}" y1="{pz(p1[1]):.2f}" x2="{px(p2[0]):.2f}" y2="{pz(p2[1]):.2f}" stroke-width="0.9"/>')
# lança de reboque (com cotovelo, passa por baixo da caixa dianteira)
a(f'<line class="v" x1="{px(1500):.2f}" y1="{pz(PIV[1]):.2f}" x2="{px(PIV[0]):.2f}" y2="{pz(PIV[1]):.2f}" stroke-width="1"/>')
a(f'<polyline class="v" points="{px(PIV[0]):.2f},{pz(PIV[1]):.2f} {px(ELBOW[0]):.2f},{pz(ELBOW[1]):.2f} {px(HANDLE[0]):.2f},{pz(HANDLE[1]):.2f}" stroke-width="1.1"/>')
a(f'<circle class="vf" cx="{px(PIV[0]):.2f}" cy="{pz(PIV[1]):.2f}" r="0.9"/>')
a(f'<circle class="wh" cx="{px(HANDLE[0]):.2f}" cy="{pz(HANDLE[1]):.2f}" r="1.1"/>')
# caixas de equipo drenáveis
for (b1, b2) in BOXES:
    rect_side(b1, b2, BZ[0], BZ[1], "vf")
    perf(px, pz, b1, b2, BZ[0], BZ[1] - 30)
    a(f'<line class="t" x1="{px(b1):.2f}" y1="{pz(BZ[1]-30):.2f}" x2="{px(b2):.2f}" y2="{pz(BZ[1]-30):.2f}"/>')  # tampa
# travessas (em vista: seção) + berços
for c in TIERS:
    for (m1, m2) in MAST_X:
        rect_side(m1 - 55, m2 + 55, c + 20, c + 70, "eva")
        rect_side(m1, m2, c - 20, c + 20, "vf")
        a(f'<line class="t" x1="{px(m1):.2f}" y1="{pz(c-20):.2f}" x2="{px(m2):.2f}" y2="{pz(c+20):.2f}"/>')
    for xs in (100, 1500):
        a(f'<line class="h" x1="{px(xs):.2f}" y1="{pz(c+20):.2f}" x2="{px(xs):.2f}" y2="{pz(c+70+KH):.2f}"/>')
# caiaques fantasma (3 níveis)
for c in TIERS:
    zb = c + 70
    x1, x2 = KX
    d = (f'M{px(x1):.2f},{pz(zb+250):.2f} Q{px(x1+700):.2f},{pz(zb):.2f} {px(x1+1500):.2f},{pz(zb):.2f} '
         f'L{px(x2-1500):.2f},{pz(zb):.2f} Q{px(x2-600):.2f},{pz(zb):.2f} {px(x2):.2f},{pz(zb+270):.2f} '
         f'Q{px(x2-900):.2f},{pz(zb+KH):.2f} {px(800):.2f},{pz(zb+KH):.2f} '
         f'Q{px(x1+900):.2f},{pz(zb+KH):.2f} {px(x1):.2f},{pz(zb+250):.2f} Z')
    a(f'<path class="ph" d="{d}"/>')
    a(f'<line class="ph" x1="{px(500):.2f}" y1="{pz(zb+KH+25):.2f}" x2="{px(1300):.2f}" y2="{pz(zb+KH+25):.2f}"/>')

# cotas vista lateral
dim_h(px(0), px(L), G1 + 6, "1600", G1, G1)
dim_h(px(WB[0]), px(WB[1]), G1 + 11, "1200 (entre-eixos)", pz(RW), pz(RW))
dim_h(px(L), px(HANDLE[0]), G1 + 6, "1400 (lança)", pz(CH[0]), pz(HANDLE[1]))
dim_h(px(KX[0]), px(KX[1]), pz(ZTOP) - 4, "caiaque máx. 5200 (ref. 4800)", pz(1000), pz(980))
dim_h(px(BOXES[0][0]), px(BOXES[0][1]), G1 + 6, "600", pz(430), pz(430))
dim_h(px(BEAMS[0][0]), px(0), G1 + 11, "1650 (balanço viga)", pz(430), G1)
dim_v(pz(BZ[0]), pz(BZ[1]), px(BOXES[0][0]) - 2.5, "300", px(BOXES[0][0]), px(BOXES[0][0]))
dim_v(G1, pz(BZ[0]), px(-1750), "480", None, None)
a(f'<line class="d" x1="{px(-1800):.2f}" y1="{pz(BZ[0]):.2f}" x2="{px(BOXES[0][0])-0.8:.2f}" y2="{pz(BZ[0]):.2f}"/>')
dim_v(G1, pz(TIERS[0] + 20), px(-300), "460", None, None)
dim_v(pz(TIERS[0] + 20), pz(TIERS[1] + 20), px(-300), "480", None, None)
dim_v(pz(TIERS[1] + 20), pz(TIERS[2] + 20), px(-300), "480", None, None)
for c in TIERS:
    a(f'<line class="d" x1="{px(-350):.2f}" y1="{pz(c+20):.2f}" x2="{px(75):.2f}" y2="{pz(c+20):.2f}"/>')
dim_v(G1, pz(MAST_TOP), px(-650), "1460", None, None)
a(f'<line class="d" x1="{px(-700):.2f}" y1="{pz(MAST_TOP):.2f}" x2="{px(75):.2f}" y2="{pz(MAST_TOP):.2f}"/>')
dim_v(G1, pz(ZTOP), px(-2000), "≈1830 c/ caiaques", None, None)
a(f'<line class="d" x1="{px(-2050):.2f}" y1="{pz(ZTOP):.2f}" x2="{px(-400):.2f}" y2="{pz(ZTOP):.2f}"/>')
dim_v(G1, pz(HANDLE[1]), px(HANDLE[0]) + 5, "900", px(3080), px(HANDLE[0]))
a(f'<text class="sm" x="{px(PIV[0]):.2f}" y="{pz(PIV[1])+3.5:.2f}">pino Ø16</text>')
a(f'<text class="sm" x="{px(0)-1:.2f}" y="{pz(60):.2f}" text-anchor="end">Ø400</text>')

# balões vista lateral
balloon(px(800), pz(300), 1, px(800), G1 + 17)
balloon(px(1600) - 1, pz(245) + 0.3, 3, px(1750), pz(-150) + 0)
balloon(px(100), pz(1150), 5, px(400), pz(1650))
balloon(px(800), pz(MAST_TOP - 20), 6, px(1150), pz(1650))
balloon(px(2400), pz(602), 12, px(2400), pz(250))
balloon(px(195), pz(CH[1]+40), 11, px(500), pz(380))
balloon(px(-1300), pz(650), 10, px(-1300), pz(1150))
balloon(px(-1500), pz(455), 15, px(-1400), pz(250))
balloon(px(-450), pz(660), 16, px(-800), pz(1050))

a(f'<text class="lbl" x="{px(450):.2f}" y="{G1+29:.2f}" text-anchor="middle">VISTA LATERAL — ESC. 1:25</text>')

# ======================================================================
# VISTA POSTERIOR (lateral esq. no 1º diedro) — y real -> papel
FX = 293
qy = lambda y: FX + y * S

def rect_f(y1, y2, z1, z2, cls="v", rx=0):
    a(f'<rect class="{cls}" x="{qy(y1):.2f}" y="{pz(z2):.2f}" width="{(y2-y1)*S:.2f}" height="{(z2-z1)*S:.2f}" rx="{rx}"/>')

a(f'<line class="v" x1="{qy(-900):.2f}" y1="{G1}" x2="{qy(900):.2f}" y2="{G1}"/>')
for i in range(0, 18):
    xx = qy(-900) + i * 4
    a(f'<line class="t" x1="{xx:.2f}" y1="{G1:.2f}" x2="{xx-1.5:.2f}" y2="{G1+1.5:.2f}"/>')
a(f'<line class="c" x1="{qy(0):.2f}" y1="{pz(-100):.2f}" x2="{qy(0):.2f}" y2="{pz(1900):.2f}"/>')

# rodas
for sg in (-1, 1):
    y1, y2 = sorted((sg * 475, sg * 625))
    rect_f(y1, y2, 0, 400, "wh", 1.8)
    a(f'<line class="v" x1="{qy(y1)+0.8:.2f}" y1="{pz(200):.2f}" x2="{qy(y2)-0.8:.2f}" y2="{pz(200):.2f}" stroke="#fff"/>')
rect_f(-475, 475, 188, 212, "vf")         # eixo
for sg in (-1, 1):
    y1, y2 = sorted((sg * 160, sg * 200))
    rect_f(y1, y2, 200, 275, "vf")
rect_f(-CHW, CHW, *CH, "vf")
# mastro duplo
for sg in (-1, 1):
    y1, y2 = sorted((sg * 40, sg * 80))
    rect_f(y1, y2, CH[1], MAST_TOP, "vf")
rect_f(-40, 40, MAST_TOP - 40, MAST_TOP, "vf")
# travessas + mãos-francesas + berços
for c in TIERS:
    rect_f(-BAR_HALF, BAR_HALF, c - 20, c + 20, "vf")
    for sg in (-1, 1):
        a(f'<polygon class="vf" points="{qy(sg*80):.2f},{pz(c-20):.2f} {qy(sg*170):.2f},{pz(c-20):.2f} {qy(sg*80):.2f},{pz(c-110):.2f}"/>')
        yc = sg * KY
        d = (f'M{qy(yc-200):.2f},{pz(c+20):.2f} L{qy(yc+200):.2f},{pz(c+20):.2f} L{qy(yc+200):.2f},{pz(c+90):.2f} '
             f'Q{qy(yc):.2f},{pz(c+20):.2f} {qy(yc-200):.2f},{pz(c+90):.2f} Z')
        a(f'<path class="eva" d="{d}"/>')
    for sg in (-1, 1):
        y1, y2 = sorted((sg * BAR_HALF, sg * (BAR_HALF + 8)))
        rect_f(y1, y2, c - 22, c + 22, "wh")
# caixa traseira (em primeiro plano) + viga
rect_f(-25, 25, 430, 480, "vf")
rect_f(-BHW, BHW, BZ[0], BZ[1], "vf")
perf(qy, pz, -BHW, BHW, BZ[0], BZ[1] - 30)
a(f'<line class="t" x1="{qy(-BHW):.2f}" y1="{pz(BZ[1]-30):.2f}" x2="{qy(BHW):.2f}" y2="{pz(BZ[1]-30):.2f}"/>')
# caiaques (seção)
for c in TIERS:
    zb = c + 60
    for yc in (-KY, KY):
        d = (f'M{qy(yc-280):.2f},{pz(zb+130):.2f} Q{qy(yc-280):.2f},{pz(zb):.2f} {qy(yc):.2f},{pz(zb):.2f} '
             f'Q{qy(yc+280):.2f},{pz(zb):.2f} {qy(yc+280):.2f},{pz(zb+130):.2f} '
             f'Q{qy(yc+250):.2f},{pz(zb+KH):.2f} {qy(yc):.2f},{pz(zb+KH):.2f} '
             f'Q{qy(yc-250):.2f},{pz(zb+KH):.2f} {qy(yc-280):.2f},{pz(zb+130):.2f} Z')
        a(f'<path class="ph" d="{d}"/>')
        a(f'<path class="h" d="M{qy(yc-210):.2f},{pz(c+20):.2f} L{qy(yc-300):.2f},{pz(zb+140):.2f} Q{qy(yc-270):.2f},{pz(zb+KH+30):.2f} {qy(yc):.2f},{pz(zb+KH+15):.2f} Q{qy(yc+270):.2f},{pz(zb+KH+30):.2f} {qy(yc+300):.2f},{pz(zb+140):.2f} L{qy(yc+210):.2f},{pz(c+20):.2f}"/>')

# cotas vista posterior
dim_h(qy(-BAR_HALF), qy(BAR_HALF), pz(ZTOP) - 4, "1500", pz(TIERS[2] + 22), pz(TIERS[2] + 22))
dim_h(qy(-KY), qy(KY), pz(ZTOP) - 9.5, "800 (eixo caiaques)", None, None)
dim_h(qy(-625), qy(625), G1 + 6, "1250", G1, G1)
dim_h(qy(-550), qy(550), G1 + 11, "1100 (bitola)", pz(0), pz(0))
dim_h(qy(-CHW), qy(CHW), G1 + 16, "400 (chassi)", pz(CH[0]), pz(CH[0]), toff=15)
dim_h(qy(-BHW), qy(BHW), G1 + 21, "350 (caixa)", pz(BZ[0]), pz(BZ[0]), toff=15)
balloon(qy(-600), pz(TIERS[1]), 7, qy(-900), pz(TIERS[1]) + 1)
balloon(qy(-480), pz(TIERS[0] + 60), 8, qy(-900), pz(TIERS[0] + 140))
balloon(qy(130), pz(TIERS[0] - 40), 13, qy(-900), pz(TIERS[0] - 150))
balloon(qy(560), pz(300), 4, qy(830), pz(320))
balloon(qy(100), pz(560), 10, qy(830), pz(640))
balloon(qy(380), pz(200), 2, qy(830), pz(130))
balloon(qy(-380), pz(TIERS[2]+KH), 9, qy(-900), pz(TIERS[2]+250))
a(f'<text class="lbl" x="{FX:.2f}" y="{G1+29:.2f}" text-anchor="middle">VISTA POSTERIOR — ESC. 1:25</text>')

# ======================================================================
# VISTA SUPERIOR — x real -> px ; y real -> papel (y+ para cima)
TY = 182
ty = lambda y: TY - y * S

def rect_t(x1, x2, y1, y2, cls="v", rx=0):
    a(f'<rect class="{cls}" x="{px(x1):.2f}" y="{ty(y2):.2f}" width="{(x2-x1)*S:.2f}" height="{(y2-y1)*S:.2f}" rx="{rx}"/>')

a(f'<line class="c" x1="{px(-2200):.2f}" y1="{TY}" x2="{px(3150):.2f}" y2="{TY}"/>')
for xw in WB:
    for sg in (-1, 1):
        y1, y2 = sorted((sg * 475, sg * 625))
        rect_t(xw - 200, xw + 200, y1, y2, "wh", 1)
    a(f'<line class="v" x1="{px(xw):.2f}" y1="{ty(475):.2f}" x2="{px(xw):.2f}" y2="{ty(-475):.2f}" stroke-width="0.9"/>')
rect_t(0, L, -CHW, CHW, "vf")
rect_t(50, L - 50, -CHW + 50, CHW - 50, "v")
a(f'<circle class="h" cx="{px(1400):.2f}" cy="{ty(0):.2f}" r="{150*S:.2f}"/>')
# lança + manopla T
a(f'<line class="v" x1="{px(1500):.2f}" y1="{TY}" x2="{px(HANDLE[0]):.2f}" y2="{TY}" stroke-width="1.1"/>')
a(f'<line class="v" x1="{px(HANDLE[0]):.2f}" y1="{ty(250):.2f}" x2="{px(HANDLE[0]):.2f}" y2="{ty(-250):.2f}" stroke-width="1.1"/>')
for sg in (-1, 1):
    a(f'<line class="v" x1="{px(HANDLE[0]):.2f}" y1="{ty(sg*120):.2f}" x2="{px(HANDLE[0]):.2f}" y2="{ty(sg*250):.2f}" stroke-width="1.8" stroke="#333"/>')
# vigas + caixas
for (b1, b2) in BEAMS:
    rect_t(b1, b2, -25, 25, "vf")
for (b1, b2) in BOXES:
    rect_t(b1, b2, -BHW, BHW, "vf")
    perf(px, ty, b1, b2, -BHW, BHW)
for (m1, m2) in MAST_X:
    rect_t(m1, m2, -BAR_HALF, BAR_HALF, "vf")
    for sg in (-1, 1):
        rect_t(m1 - 55, m2 + 55, sg * KY - 200, sg * KY + 200, "eva")
rect_t(120, 1480, -20, 20, "vf")
# giro ±35°
import math
for sg in (-1, 1):
    ang = math.radians(35) * sg
    ex = 1650 + 1350 * math.cos(ang); ey = 1350 * math.sin(ang)
    a(f'<line class="ph" x1="{px(1650):.2f}" y1="{TY}" x2="{px(ex):.2f}" y2="{ty(ey):.2f}"/>')
a(f'<text class="sm" x="{px(2350):.2f}" y="{ty(560):.2f}" fill="#1f5fa8">giro ±35°</text>')
# caiaques fantasma
for sg in (-1, 1):
    yc = sg * KY
    x1, x2 = KX
    d = (f'M{px(x1):.2f},{ty(yc):.2f} Q{px(x1+1200):.2f},{ty(yc+KW/2):.2f} {px(500):.2f},{ty(yc+KW/2):.2f} '
         f'Q{px(x2-1100):.2f},{ty(yc+KW/2):.2f} {px(x2):.2f},{ty(yc):.2f} '
         f'Q{px(x2-1100):.2f},{ty(yc-KW/2):.2f} {px(500):.2f},{ty(yc-KW/2):.2f} '
         f'Q{px(x1+1200):.2f},{ty(yc-KW/2):.2f} {px(x1):.2f},{ty(yc):.2f} Z')
    a(f'<path class="ph" d="{d}"/>')
    a(f'<ellipse class="ph" cx="{px(800):.2f}" cy="{ty(yc):.2f}" rx="{420*S:.2f}" ry="{200*S:.2f}"/>')
# cotas vista superior
dim_v(ty(BAR_HALF), ty(-BAR_HALF), px(-2150) + 0, "1500", None, None)
for yy in (BAR_HALF, -BAR_HALF):
    a(f'<line class="d" x1="{px(-2200):.2f}" y1="{ty(yy):.2f}" x2="{px(75):.2f}" y2="{ty(yy):.2f}"/>')
dim_v(ty(250), ty(-250), px(HANDLE[0]) + 4, "500", px(HANDLE[0]), px(HANDLE[0]))
dim_v(ty(BHW), ty(-BHW), px(BOXES[0][0]) - 3, "350", px(BOXES[0][0]), px(BOXES[0][0]))
dim_h(px(MAST_X[0][0]), px(MAST_X[1][1]), ty(-BAR_HALF) + 5, "1440 (vão entre berços)", ty(-BAR_HALF), ty(-BAR_HALF))
balloon(px(1400), ty(-60), 3, px(1900), ty(-650))
balloon(px(-1300), ty(100), 10, px(-1300), ty(-650))
a(f'<text class="lbl" x="{px(450):.2f}" y="{ty(-BAR_HALF)+12:.2f}" text-anchor="middle">VISTA SUPERIOR — ESC. 1:25</text>')

# ======================================================================
# DETALHE A — berço (esc. 1:10)
DS = 0.1
DX, DZ = 371, 62
dx = lambda y: DX + y * DS
dz = lambda z: DZ - z * DS
a(f'<rect class="t" x="333" y="18" width="75" height="62" rx="1" stroke-dasharray="2 1"/>')
a(f'<rect class="vf" x="{dx(-200):.2f}" y="{dz(20):.2f}" width="{400*DS:.2f}" height="{40*DS:.2f}"/>')
a(f'<line class="t" x1="{dx(-200):.2f}" y1="{dz(17):.2f}" x2="{dx(200):.2f}" y2="{dz(17):.2f}"/>')
a(f'<line class="t" x1="{dx(-200):.2f}" y1="{dz(-17):.2f}" x2="{dx(200):.2f}" y2="{dz(-17):.2f}"/>')
a(f'<rect class="vf" x="{dx(-200):.2f}" y="{dz(25):.2f}" width="{400*DS:.2f}" height="{5*DS:.2f}"/>')
d = (f'M{dx(-200):.2f},{dz(25):.2f} L{dx(200):.2f},{dz(25):.2f} L{dx(200):.2f},{dz(95):.2f} '
     f'Q{dx(0):.2f},{dz(25):.2f} {dx(-200):.2f},{dz(95):.2f} Z')
a(f'<path class="eva" d="{d}"/>')
# casco fantasma
a(f'<path class="ph" d="M{dx(-280):.2f},{dz(220):.2f} Q{dx(-280):.2f},{dz(60):.2f} {dx(0):.2f},{dz(60):.2f} Q{dx(280):.2f},{dz(60):.2f} {dx(280):.2f},{dz(220):.2f}"/>')
# parafusos
for yb in (-140, 140):
    a(f'<line class="v" x1="{dx(yb):.2f}" y1="{dz(55):.2f}" x2="{dx(yb):.2f}" y2="{dz(-30):.2f}"/>')
    a(f'<rect class="wh" x="{dx(yb)-0.9:.2f}" y="{dz(-25):.2f}" width="1.8" height="0.8"/>')
# fivela/catraca
a(f'<rect class="wh" x="{dx(205):.2f}" y="{dz(10):.2f}" width="1.6" height="2.5"/>')
a(f'<line class="h" x1="{dx(214):.2f}" y1="{dz(30):.2f}" x2="{dx(290):.2f}" y2="{dz(200):.2f}"/>')
dim_h(dx(-200), dx(200), dz(95) - 6, "400", dz(95), dz(95))
dim_v(dz(-20), dz(20), dx(-200) - 4, "40", dx(-200), dx(-200))
dim_v(dz(25), dz(95), dx(200) + 6, "70", dx(200), dx(200))
a(f'<text class="sm" x="{dx(-200):.2f}" y="{dz(-60):.2f}">EVA 30 mm colado + base alum. 5 mm</text>')
a(f'<text class="sm" x="{dx(-200):.2f}" y="{dz(-85):.2f}">2× parafuso inox M8 c/ arruela nylon</text>')
a(f'<text class="sm" x="{dx(-200):.2f}" y="{dz(-110):.2f}">cinta cam 25 mm presa à travessa</text>')
a(f'<text class="lbl" x="{DX:.2f}" y="23.5" text-anchor="middle">DETALHE A — BERÇO 1:10</text>')

# ======================================================================
# LISTA DE MATERIAIS
BOM = [
 ("1", "Chassi espinha 400: 2 longarinas 1600 + 3 trav. 300", "Tubo alum. 6061-T6 50×50×3", "1 cj"),
 ("2", "Eixo traseiro 1250 + mancais", "Aço inox 304 Ø25", "1"),
 ("3", "Eixo dianteiro c/ prato giratório Ø300", "Rolamento axial + batente ±35°", "1 cj"),
 ("4", "Roda balão 16×6.50-8 (Ø400) c/ rolamento", "Pneu baixa pressão p/ areia", "4"),
 ("5", "Mastro (duplo, 2 tubos por ponta) 1135", "Tubo alum. 40×40×3", "4"),
 ("6", "Viga superior de ligação 1360", "Tubo alum. 40×40×3", "1"),
 ("7", "Travessa porta-caiaque 1500 c/ tampas", "Tubo alum. 40×40×3", "6"),
 ("8", "Berço 400×150 (ver Detalhe A)", "Chapa alum. 5 + EVA 30", "12"),
 ("9", "Cinta cam/catraca 25 mm × 3 m", "Poliéster c/ fivela inox", "12"),
 ("10", "Caixa equipo 600×350×300, tampa na ponta", "Chapa alum. perfurada 2 mm Ø10", "1"),
 ("11", "Mão-francesa base mastro 150×150", "Chapa alum. 6 mm", "4"),
 ("12", "Lança 1500 + manopla T 500 c/ pegas", "Tubo alum. Ø38×3", "1"),
 ("13", "Mão-francesa travessa 90×90", "Chapa alum. 5 mm", "12"),
 ("14", "Fixadores M8/M10 autotravantes", "Inox A4 + arruelas nylon", "1 cj"),
 ("15", "Viga porta-caixa traseira 1730", "Tubo alum. 50×50×3", "1"),
 ("16", "Tirante viga–mastro 1120", "Tubo alum. 30×30×3", "1"),
]
BX, BY = 233, 150
cw = (8, 72, 64, 12)
rh = 4.6
tw = sum(cw)
a(f'<text class="lbl" x="{BX:.2f}" y="{BY-2:.2f}">LISTA DE MATERIAIS</text>')
hdr = ("Item", "Descrição", "Material / especificação", "Qtd")
yy = BY
a(f'<rect x="{BX}" y="{yy}" width="{tw}" height="{rh}" fill="#dfe6ec" stroke="#000" stroke-width="0.25"/>')
for rowi, row in enumerate([hdr] + BOM):
    xx = BX
    if rowi:
        a(f'<rect x="{BX}" y="{yy}" width="{tw}" height="{rh}" fill="none" stroke="#000" stroke-width="0.15"/>')
    for j, cell in enumerate(row):
        anchor = "middle" if j in (0, 3) else "start"
        tx = xx + cw[j] / 2 if j in (0, 3) else xx + 1
        wt = ' font-weight="bold"' if rowi == 0 else ''
        a(f'<text class="sm" x="{tx:.2f}" y="{yy+3.1:.2f}" text-anchor="{anchor}"{wt}>{cell}</text>')
        xx += cw[j]
    yy += rh
xx = BX
for w in cw[:-1]:
    xx += w
    a(f'<line class="t" x1="{xx}" y1="{BY}" x2="{xx}" y2="{yy}"/>')

# ======================================================================
# NOTAS
NOTES = [
 "NOTAS",
 "1. Cotas em mm. Medidas ESTIMADAS a partir de fotografia — conferir com os caiaques reais (boca, comprimento, peso) antes de cortar material.",
 "2. Capacidade: 6 caiaques (3 níveis × 2 lados), até 5,2 m e 30 kg cada + 1 caixa de equipo (~25 kg). Carga de projeto: 250 kg.",
 "3. Estrutura em alumínio 6061-T6 soldado TIG. Ambiente marinho: fixadores inox A4 isolados com arruelas de nylon (evita corrosão galvânica alumínio × inox).",
 "4. Rodas balão de baixa pressão (~8–12 psi) para areia fofa. Eixo dianteiro giratório com batente ±35°; lança reta articulada em pino Ø16 (sobe/desce com o terreno).",
 "5. 1 caixa de equipo (63 L) atrás, entre os cascos, na altura do caiaque de baixo. Chapa perfurada Ø10 p/ drenar; tampa articulada na ponta externa.",
 "6. Carregar de baixo para cima e descarregar de cima para baixo, alternando lados. Caixa é opcional: sem ela, equipo vai dentro do caiaque.",
 "7. Travessas a 460 / 940 / 1420 do solo (face superior), 200 mm mais baixas que a rev. 0. Folga travessa × pneu = 20 mm; casco × travessa de cima ≈ 50 mm.",
]
ny = 233
for i, n in enumerate(NOTES):
    cls = "lbl" if i == 0 else "sm"
    a(f'<text class="{cls}" x="16" y="{ny:.2f}">{n}</text>')
    ny += 4.0 if i == 0 else 3.4

# ======================================================================
# LEGENDA de linhas
LX, LY = 233, 234
a(f'<line class="v" x1="{LX}" y1="{LY}" x2="{LX+10}" y2="{LY}"/><text class="sm" x="{LX+12}" y="{LY+0.7}">contorno visível</text>')
a(f'<line class="ph" x1="{LX+40}" y1="{LY}" x2="{LX+50}" y2="{LY}"/><text class="sm" x="{LX+52}" y="{LY+0.7}">caiaque / posição alternativa (referência)</text>')
a(f'<line class="h" x1="{LX+40}" y1="{LY+4}" x2="{LX+50}" y2="{LY+4}"/><text class="sm" x="{LX+52}" y="{LY+4.7}">cinta / oculto</text>')
a(f'<rect class="eva" x="{LX}" y="{LY+3}" width="10" height="2"/><text class="sm" x="{LX+12}" y="{LY+4.7}">berço EVA</text>')

# ======================================================================
# CARIMBO
TBX, TBY, TBW, TBH = 233, 252, 177, 35
a(f'<rect x="{TBX}" y="{TBY}" width="{TBW}" height="{TBH}" fill="none" stroke="#000" stroke-width="0.5"/>')
a(f'<line class="t" x1="{TBX}" y1="{TBY+13}" x2="{TBX+TBW}" y2="{TBY+13}"/>')
a(f'<line class="t" x1="{TBX}" y1="{TBY+24}" x2="{TBX+TBW}" y2="{TBY+24}"/>')
for xx in (TBX + 45, TBX + 90, TBX + 135):
    a(f'<line class="t" x1="{xx}" y1="{TBY+13}" x2="{xx}" y2="{TBY+TBH}"/>')
a(f'<text x="{TBX+3}" y="{TBY+6.5}" font-size="4.6" font-weight="bold">CARRETA PORTA-CAIAQUES — 6 UNIDADES</text>')
a(f'<text class="tb" x="{TBX+3}" y="{TBY+10.8}">Aqua Terra Paraty · sea kayak &amp; trekking · Paraty/RJ</text>')
cells = [("ESCALA", "1:25 (Det. A 1:10)"), ("FORMATO", "A3 · 1º diedro"), ("UNIDADE", "mm"), ("REVISÃO", "2 — 1 caixa traseira"),
         ("DATA", "14/10/2026"), ("DESENHO", "Claude / Lucas"), ("MATERIAL", "Alum. 6061-T6"), ("FOLHA", "1 / 1")]
for i, (k, v) in enumerate(cells):
    cx = TBX + (i % 4) * 45 + 2
    cy = TBY + 13 + (i // 4) * 11
    a(f'<text font-size="1.7" x="{cx}" y="{cy+3}" fill="#555">{k}</text>')
    a(f'<text class="tb" x="{cx}" y="{cy+8}" font-weight="bold">{v}</text>')

# moldura
body = "\n".join(s for s in out if s)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
{STYLE}
<rect x="0" y="0" width="420" height="297" fill="#fff"/>
<rect x="10" y="10" width="400" height="277" fill="none" stroke="#000" stroke-width="0.7"/>
{body}
</svg>'''
open(sys.argv[1], "w").write(svg)
print("ok")
