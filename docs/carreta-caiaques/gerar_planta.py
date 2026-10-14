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
def dim_h(x1, x2, y, txt, yref1=None, yref2=None, up=True):
    """Cota horizontal no papel. yref = y da peça (para linha de chamada)."""
    for x, yr in ((x1, yref1), (x2, yref2)):
        if yr is not None:
            sgn = -1 if y < yr else 1
            a(f'<line class="d" x1="{x:.2f}" y1="{yr + sgn*0.8:.2f}" x2="{x:.2f}" y2="{y + sgn*1.2:.2f}"/>')
    a(f'<line class="d" x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    a(f'<text class="dt" x="{(x1+x2)/2:.2f}" y="{y-0.7:.2f}" text-anchor="middle">{txt}</text>')

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
L = 1600            # chassi
WB = (200, 1400)    # eixos traseiro / dianteiro
RW = 200            # raio roda (Ø400)
CH = (275, 325)     # tubo chassi 50x50
BOX = (300, 1300, 325, 625)   # x1,x2,z1,z2  (largura 600)
MAST_X = ((80, 120), (1480, 1520))
MAST_TOP = 1650
TIERS = (640, 1120, 1600)     # eixo das travessas 40x40
BAR_HALF = 750
KY = 400            # centro do caiaque em y (±)
KW, KH = 560, 330   # boca / altura do caiaque
KX = (-2100, 2700)  # caiaque 4,8 m (fantasma)
PIV = (1650, 230)   # pino da lança
HANDLE = (3000, 900)

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

# caiaques fantasma (3 níveis)
for c in TIERS:
    zb = c + 70
    x1, x2 = KX
    d = (f'M{px(x1):.2f},{pz(zb+250):.2f} Q{px(x1+700):.2f},{pz(zb):.2f} {px(x1+1500):.2f},{pz(zb):.2f} '
         f'L{px(x2-1500):.2f},{pz(zb):.2f} Q{px(x2-600):.2f},{pz(zb):.2f} {px(x2):.2f},{pz(zb+270):.2f} '
         f'Q{px(x2-900):.2f},{pz(zb+KH):.2f} {px(800):.2f},{pz(zb+KH):.2f} '
         f'Q{px(x1+900):.2f},{pz(zb+KH):.2f} {px(x1):.2f},{pz(zb+250):.2f} Z')
    a(f'<path class="ph" d="{d}"/>')
    # cockpit
    a(f'<line class="ph" x1="{px(500):.2f}" y1="{pz(zb+KH+25):.2f}" x2="{px(1300):.2f}" y2="{pz(zb+KH+25):.2f}"/>')

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
# caixa perfurada
rect_side(BOX[0], BOX[1], BOX[2], BOX[3], "vf")
for ix in range(BOX[0] + 40, BOX[1] - 20, 40):
    for iz in range(BOX[2] + 60, BOX[3] - 20, 40):
        a(f'<circle class="perf" cx="{px(ix):.2f}" cy="{pz(iz):.2f}" r="0.25"/>')
a(f'<line class="t" x1="{px(BOX[0]+20):.2f}" y1="{pz(BOX[2]+30):.2f}" x2="{px(BOX[1]-20):.2f}" y2="{pz(BOX[2]+30):.2f}"/>')  # dobradiça porta
a(f'<line class="t" x1="{px(BOX[0]+20):.2f}" y1="{pz(BOX[3]-10):.2f}" x2="{px(BOX[1]-20):.2f}" y2="{pz(BOX[3]-10):.2f}"/>')
rect_side(780, 820, BOX[3]-40, BOX[3]-10, "v")  # trinco
# mastros, viga superior, mãos-francesas
for (m1, m2) in MAST_X:
    rect_side(m1, m2, CH[1], MAST_TOP, "vf")
rect_side(120, 1480, MAST_TOP - 40, MAST_TOP, "vf")
for base, sgn in ((120, 1), (1480, -1)):
    a(f'<polygon class="vf" points="{px(base):.2f},{pz(CH[1]):.2f} {px(base+sgn*150):.2f},{pz(CH[1]):.2f} {px(base):.2f},{pz(CH[1]+150):.2f}"/>')
# travessas (em vista: seção) + berços
for c in TIERS:
    for (m1, m2) in MAST_X:
        rect_side(m1 - 55, m2 + 55, c + 20, c + 70, "eva")
        rect_side(m1, m2, c - 20, c + 20, "vf")
        a(f'<line class="t" x1="{px(m1):.2f}" y1="{pz(c-20):.2f}" x2="{px(m2):.2f}" y2="{pz(c+20):.2f}"/>')
    # cinta (catraca) sobre o caiaque, nos dois mastros
    for xs in (100, 1500):
        a(f'<line class="h" x1="{px(xs):.2f}" y1="{pz(c+20):.2f}" x2="{px(xs):.2f}" y2="{pz(c+70+KH):.2f}"/>')
# lança de reboque
a(f'<line class="v" x1="{px(1500):.2f}" y1="{pz(PIV[1]):.2f}" x2="{px(PIV[0]):.2f}" y2="{pz(PIV[1]):.2f}" stroke-width="1"/>')
a(f'<circle class="vf" cx="{px(PIV[0]):.2f}" cy="{pz(PIV[1]):.2f}" r="0.9"/>')
a(f'<line class="v" x1="{px(PIV[0]):.2f}" y1="{pz(PIV[1]):.2f}" x2="{px(HANDLE[0]):.2f}" y2="{pz(HANDLE[1]):.2f}" stroke-width="1.1"/>')
a(f'<line class="v" x1="{px(HANDLE[0]):.2f}" y1="{pz(HANDLE[1])-0.1:.2f}" x2="{px(HANDLE[0]):.2f}" y2="{pz(HANDLE[1]):.2f}"/>')
a(f'<circle class="wh" cx="{px(HANDLE[0]):.2f}" cy="{pz(HANDLE[1]):.2f}" r="1.1"/>')
# posição recolhida (fantasma)
a(f'<line class="ph" x1="{px(PIV[0]):.2f}" y1="{pz(PIV[1]):.2f}" x2="{px(PIV[0]+250):.2f}" y2="{pz(PIV[1]+1480):.2f}"/>')

# cotas vista lateral
dim_h(px(0), px(L), G1 + 6, "1600", G1, G1)
dim_h(px(WB[0]), px(WB[1]), G1 + 11, "1200 (entre-eixos)", pz(RW), pz(RW))
dim_h(px(L), px(HANDLE[0]), G1 + 6, "1400 (lança)", pz(CH[0]), pz(HANDLE[1]))
dim_h(px(KX[0]), px(KX[1]), pz(2020) - 4, "caiaque máx. 5200 (ref. 4800)", pz(KX[0] and 1000), pz(980))
xd = px(-2100) - 4
dim_v(G1, pz(TIERS[0] + 20), px(-300), "660", None, None)
dim_v(pz(TIERS[0] + 20), pz(TIERS[1] + 20), px(-300), "480", None, None)
dim_v(pz(TIERS[1] + 20), pz(TIERS[2] + 20), px(-300), "480", None, None)
for c in TIERS:
    a(f'<line class="d" x1="{px(-350):.2f}" y1="{pz(c+20):.2f}" x2="{px(75):.2f}" y2="{pz(c+20):.2f}"/>')
dim_v(G1, pz(MAST_TOP), px(-700), "1650", None, None)
a(f'<line class="d" x1="{px(-750):.2f}" y1="{pz(MAST_TOP):.2f}" x2="{px(75):.2f}" y2="{pz(MAST_TOP):.2f}"/>')
dim_v(G1, pz(CH[1]), px(-1100), "325", None, None)
a(f'<line class="d" x1="{px(-1150):.2f}" y1="{pz(CH[1]):.2f}" x2="{px(-5):.2f}" y2="{pz(CH[1]):.2f}"/>')
dim_v(pz(BOX[2]), pz(BOX[3]), px(BOX[0]) - 2.5, "300", px(BOX[0]), px(BOX[0]))
dim_h(px(BOX[0]), px(BOX[1]), pz(BOX[3]) - 2.5, "1000", pz(BOX[3]), pz(BOX[3]))
dim_v(G1, pz(HANDLE[1]), px(HANDLE[0]) + 5, "900", px(3080), pz(HANDLE[1]) and px(HANDLE[0]))
a(f'<text class="sm" x="{px(PIV[0])+1.5:.2f}" y="{pz(PIV[1])+3.5:.2f}">pino Ø16</text>')
a(f'<text class="sm" x="{px(xw):.2f}" y="{pz(RW)+9.3:.2f}" text-anchor="middle"></text>')
a(f'<text class="sm" x="{px(0)-1:.2f}" y="{pz(60):.2f}" text-anchor="end">Ø400</text>')
a(f'<text class="sm" x="{px(PIV[0]+250)+1:.2f}" y="{pz(PIV[1]+1480)+1:.2f}" fill="#1f5fa8">lança recolhida</text>')

# balões vista lateral
balloon(px(800), pz(300), 1, px(800), G1 + 17)
balloon(px(700), pz(480), 10, px(650), pz(1000) + 2) if False else None
balloon(px(1600) - 1, pz(245) + 0.3, 3, px(1650), pz(470))
balloon(px(100), pz(1250), 5, px(-1050), pz(1350))
balloon(px(800), pz(MAST_TOP - 20), 6, px(800), pz(1850))
balloon(px(2300), pz(PIV[1] + (2300-PIV[0])/(HANDLE[0]-PIV[0])*(HANDLE[1]-PIV[1])), 12, px(2300), pz(500))
balloon(px(400), pz(1300) , 10, px(400), pz(1300)) if False else None
balloon(px(1100), pz(480), 10, px(1100), pz(480)) if False else None
balloon(px(1100), pz(450), 10, px(1100) , pz(450)) if False else None
balloon(px(195), pz(CH[1]+40), 11, px(-450), pz(450))

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
a(f'<line class="c" x1="{qy(0):.2f}" y1="{pz(-100):.2f}" x2="{qy(0):.2f}" y2="{pz(2080):.2f}"/>')

# caiaques (seção)
for c in TIERS:
    zb = c + 60
    for yc in (-KY, KY):
        d = (f'M{qy(yc-280):.2f},{pz(zb+130):.2f} Q{qy(yc-280):.2f},{pz(zb):.2f} {qy(yc):.2f},{pz(zb):.2f} '
             f'Q{qy(yc+280):.2f},{pz(zb):.2f} {qy(yc+280):.2f},{pz(zb+130):.2f} '
             f'Q{qy(yc+250):.2f},{pz(zb+KH):.2f} {qy(yc):.2f},{pz(zb+KH):.2f} '
             f'Q{qy(yc-250):.2f},{pz(zb+KH):.2f} {qy(yc-280):.2f},{pz(zb+130):.2f} Z')
        a(f'<path class="ph" d="{d}"/>')
        # cinta
        a(f'<path class="h" d="M{qy(yc-210):.2f},{pz(c+20):.2f} L{qy(yc-300):.2f},{pz(zb+140):.2f} Q{qy(yc-270):.2f},{pz(zb+KH+30):.2f} {qy(yc):.2f},{pz(zb+KH+15):.2f} Q{qy(yc+270):.2f},{pz(zb+KH+30):.2f} {qy(yc+300):.2f},{pz(zb+140):.2f} L{qy(yc+210):.2f},{pz(c+20):.2f}"/>')
# rodas
for sg in (-1, 1):
    y1, y2 = sorted((sg * 475, sg * 625))
    rect_f(y1, y2, 0, 400, "wh", 1.8)
    a(f'<line class="v" x1="{qy(y1)+0.8:.2f}" y1="{pz(200):.2f}" x2="{qy(y2)-0.8:.2f}" y2="{pz(200):.2f}" stroke="#fff"/>')
rect_f(-475, 475, 188, 212, "vf")         # eixo
for sg in (-1, 1):
    y1, y2 = sorted((sg * 330, sg * 350))
    rect_f(y1, y2, 200, 275, "vf")
rect_f(-350, 350, *CH, "vf")
rect_f(-300, 300, BOX[2], BOX[3], "vf")
for iy in range(-260, 280, 40):
    for iz in range(BOX[2] + 60, BOX[3] - 20, 40):
        a(f'<circle class="perf" cx="{qy(iy):.2f}" cy="{pz(iz):.2f}" r="0.25"/>')
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
    # tampas nas pontas
    for sg in (-1, 1):
        y1, y2 = sorted((sg * BAR_HALF, sg * (BAR_HALF + 8)))
        rect_f(y1, y2, c - 22, c + 22, "wh")

# cotas vista posterior
dim_h(qy(-BAR_HALF), qy(BAR_HALF), pz(2020) - 4, "1500", pz(TIERS[2] + 22), pz(TIERS[2] + 22))
dim_h(qy(-KY), qy(KY), pz(2020) - 9.5, "800 (eixo caiaques)", None, None)
dim_h(qy(-625), qy(625), G1 + 6, "1250", G1, G1)
dim_h(qy(-550), qy(550), G1 + 11, "1100 (bitola)", pz(0), pz(0))
dim_h(qy(-300), qy(300), G1 + 21, "600 (caixa)", pz(BOX[2]), pz(BOX[2]))
dim_h(qy(-350), qy(350), G1 + 16, "700 (chassi)", pz(CH[0]), pz(CH[0]))
balloon(qy(-600), pz(TIERS[1]), 7, qy(-900), pz(TIERS[1]) + 1)
balloon(qy(-480), pz(TIERS[0] + 60), 8, qy(-900), pz(TIERS[0] + 140))
balloon(qy(130), pz(TIERS[0] - 40), 13, qy(-900), pz(TIERS[0] - 150))
balloon(qy(560), pz(300), 4, qy(830), pz(450))
balloon(qy(250), pz(500), 10, qy(830), pz(700))
balloon(qy(380), pz(240), 2, qy(830), pz(130) )
balloon(qy(60), pz(1400), 5, qy(830), pz(1420) - 0.0) if False else None
balloon(qy(-320+(-60)), pz(TIERS[2]+KH), 9, qy(-900), pz(TIERS[2]+250))
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
rect_t(0, L, -350, 350, "vf")
rect_t(50, L - 50, -300, 300, "v")
rect_t(BOX[0], BOX[1], -300, 300, "vf")
for ix in range(BOX[0] + 40, BOX[1] - 20, 40):
    for iy in range(-260, 280, 40):
        a(f'<circle class="perf" cx="{px(ix):.2f}" cy="{ty(iy):.2f}" r="0.25"/>')
a(f'<circle class="h" cx="{px(1400):.2f}" cy="{ty(0):.2f}" r="{150*S:.2f}"/>')
for (m1, m2) in MAST_X:
    rect_t(m1, m2, -BAR_HALF, BAR_HALF, "vf")
    for sg in (-1, 1):
        rect_t(m1 - 55, m2 + 55, sg * KY - 200, sg * KY + 200, "eva")
rect_t(120, 1480, -20, 20, "vf")
# lança + manopla T
a(f'<line class="v" x1="{px(1500):.2f}" y1="{TY}" x2="{px(HANDLE[0]):.2f}" y2="{TY}" stroke-width="1.1"/>')
a(f'<line class="v" x1="{px(HANDLE[0]):.2f}" y1="{ty(250):.2f}" x2="{px(HANDLE[0]):.2f}" y2="{ty(-250):.2f}" stroke-width="1.1"/>')
for sg in (-1, 1):
    a(f'<line class="v" x1="{px(HANDLE[0]):.2f}" y1="{ty(sg*120):.2f}" x2="{px(HANDLE[0]):.2f}" y2="{ty(sg*250):.2f}" stroke-width="1.8" stroke="#333"/>')
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
dim_h(px(MAST_X[0][0]), px(MAST_X[1][1]), ty(-BAR_HALF) + 5, "1440 (vão entre berços)", ty(-BAR_HALF), ty(-BAR_HALF))
balloon(px(1400), ty(-60), 3, px(1900), ty(-650))
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
 ("1", "Chassi: 2 longarinas 1600 + 3 travessas 600", "Tubo alum. 6061-T6 50×50×3", "1 cj"),
 ("2", "Eixo traseiro 1250 + mancais", "Aço inox 304 Ø25", "1"),
 ("3", "Eixo dianteiro c/ prato giratório Ø300", "Rolamento axial + batente ±35°", "1 cj"),
 ("4", "Roda balão 16×6.50-8 (Ø400) c/ rolamento", "Pneu baixa pressão p/ areia", "4"),
 ("5", "Mastro (duplo, 2 tubos por ponta) 1325", "Tubo alum. 40×40×3", "4"),
 ("6", "Viga superior de ligação 1360", "Tubo alum. 40×40×3", "1"),
 ("7", "Travessa porta-caiaque 1500 c/ tampas", "Tubo alum. 40×40×3", "6"),
 ("8", "Berço 400×150 (ver Detalhe A)", "Chapa alum. 5 + EVA 30", "12"),
 ("9", "Cinta cam/catraca 25 mm × 3 m", "Poliéster c/ fivela inox", "12"),
 ("10", "Caixa carga 1000×600×300, porta basculante", "Chapa alum. perfurada 2 mm Ø10", "1"),
 ("11", "Mão-francesa base mastro 150×150", "Chapa alum. 6 mm", "4"),
 ("12", "Lança 1500 + manopla T 500 c/ pegas", "Tubo alum. Ø38×3", "1"),
 ("13", "Mão-francesa travessa 90×90", "Chapa alum. 5 mm", "12"),
 ("14", "Fixadores M8/M10 autotravantes", "Inox A4 + arruelas nylon", "1 cj"),
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
 "2. Capacidade: 6 caiaques (3 níveis × 2 lados), até 5,2 m e 30 kg cada. Carga de projeto: 250 kg (caiaques + caixa).",
 "3. Estrutura em alumínio 6061-T6 soldado TIG. Ambiente marinho: fixadores inox A4 isolados com arruelas de nylon (evita corrosão galvânica alumínio × inox).",
 "4. Rodas balão de baixa pressão (~8–12 psi) para areia fofa. Eixo dianteiro giratório com batente ±35°; lança articulada em pino Ø16 (recolhe na vertical).",
 "5. Caixa com chapa perfurada (furos Ø10, passo 40) para drenar água e areia; porta basculante nos dois lados, trinco inox.",
 "6. Carregar de baixo para cima e descarregar de cima para baixo, alternando lados. Centro de gravidade alto: passo de caminhada, evitar rampa lateral.",
 "7. Travessas a 660 / 1140 / 1620 do solo (face superior). Folga entre casco e travessa de cima ≈ 50 mm — validar com o caiaque mais alto da frota.",
]
ny = 233
for i, n in enumerate(NOTES):
    cls = "lbl" if i == 0 else "sm"
    a(f'<text class="{cls}" x="16" y="{ny:.2f}">{n}</text>')
    ny += 4.0 if i == 0 else 3.4

# ======================================================================
# LEGENDA de linhas
LX, LY = 233, 222
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
cells = [("ESCALA", "1:25 (Det. A 1:10)"), ("FORMATO", "A3 · 1º diedro"), ("UNIDADE", "mm"), ("REVISÃO", "0 — anteprojeto"),
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
