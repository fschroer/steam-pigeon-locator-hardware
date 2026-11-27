"""Generate simplified 3D models (STEP) for parts that have no KiCad stock model.

Bodies use datasheet outline dimensions; terminals follow the footprint pads.
Coordinates: footprint frame (x right, y down), so model y = -footprint y.
Run with CadQuery 2.x:  python tools/gen_3dmodels.py lib/3dmodels
"""
import sys, os, math
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else "lib/3dmodels"
os.makedirs(OUT, exist_ok=True)

C = {
    "black": cq.Color(0.10, 0.10, 0.10),
    "body": cq.Color(0.15, 0.15, 0.17),
    "metal": cq.Color(0.80, 0.80, 0.82),
    "gold": cq.Color(0.86, 0.70, 0.30),
    "tin": cq.Color(0.75, 0.75, 0.78),
    "white": cq.Color(0.95, 0.95, 0.93),
    "lens": cq.Color(0.95, 0.95, 0.80),
    "ceramic": cq.Color(0.82, 0.74, 0.58),
    "silver": cq.Color(0.90, 0.90, 0.90),
    "green": cq.Color(0.10, 0.35, 0.15),
    "mark": cq.Color(0.55, 0.55, 0.55),
    "silicon": cq.Color(0.25, 0.25, 0.35),
}


def box(w, h, t, x=0.0, y=0.0, z=0.0):
    """Box centred at footprint (x, y), bottom at z."""
    return cq.Workplane("XY").box(w, h, t, centered=(True, True, False)).translate((x, -y, z))


def cyl(d, t, x=0.0, y=0.0, z=0.0):
    return cq.Workplane("XY").circle(d / 2).extrude(t).translate((x, -y, z))


def pin1_dot(x, y, z, d=0.2):
    return cyl(d, 0.01, x, y, z)


def pads_flush(pads, shrink=0.85, t=0.03):
    """Terminals of a no-lead package: thin plates under the body at pad positions."""
    w = None
    for (x, y, sx, sy) in pads:
        p = box(sx * shrink, sy * shrink, t, x, y, 0)
        w = p if w is None else w.union(p)
    return w


def save(name, parts):
    a = cq.Assembly(name=name)
    for i, (shape, col) in enumerate(parts):
        if shape is not None:
            a.add(shape, name=f"{name}_{i}", color=C[col])
    path = os.path.join(OUT, name + ".step")
    a.save(path, exportType="STEP")
    print("wrote", path)


def no_lead(name, bw, bh, height, pads, pin1, standoff=0.03, col="body", trim=None):
    """QFN/DFN/SON/LGA style: body on top of flush terminals clipped to the body outline."""
    term = pads_flush(pads, t=standoff + 0.001)
    clip = box(bw, bh, 1, 0, 0, -0.5)
    term = term.intersect(clip)
    body = box(bw, bh, height - standoff, 0, 0, standoff)
    dot = pin1_dot(pin1[0], pin1[1], height, 0.25 * min(bw, bh) if min(bw, bh) < 2 else 0.5)
    save(name, [(body, col), (term, "tin"), (dot, "mark")])


# ---- D4, D5: XINGLIGHT XL-Z1921RGBA-SG RGB LED (approx. 2.1 x 1.9 x 0.75) ----
led_pads = [(0.83, 0.6, 0.66, 0.7), (0.83, -0.6, 0.66, 0.7), (-0.83, -0.6, 0.66, 0.7), (-0.83, 0.6, 0.66, 0.7)]
term = pads_flush(led_pads, t=0.05).intersect(box(2.1, 1.9, 1, 0, 0, -0.5))
save("LED_XL-Z1912RGBA-SG", [
    (box(2.1, 1.9, 0.35, 0, 0, 0.05), "white"),
    (box(1.8, 1.6, 0.35, 0, 0, 0.4), "lens"),
    (term, "tin"),
    (pin1_dot(0.83, 0.6, 0.751, 0.25), "mark"),
])

# ---- TPS22950 YBH: DSBGA-6, 0.8 x 1.2 mm, 0.4 mm pitch, ~0.5 mm high ----
balls = None
for x in (-0.2, 0.2):
    for y in (-0.4, 0.0, 0.4):
        s = cq.Workplane("XY").sphere(0.11).translate((x, -y, 0.1))
        balls = s if balls is None else balls.union(s)
balls = balls.intersect(box(2, 2, 0.2, 0, 0, 0))
save("Texas_DSBGA-6_YBH_0.8x1.2mm_P0.4mm", [
    (box(0.78, 1.18, 0.30, 0, 0, 0.19), "silicon"),
    (balls, "tin"),
    (pin1_dot(-0.2, -0.4, 0.491, 0.12), "mark"),
])

# ---- U3: DRV5032 X2SON-4 (DMR), 1.1 x 1.4 x 0.4 ----
no_lead("TI_X2SON-4-1EP_1.1x1.4mm", 1.1, 1.4, 0.4,
        [(-0.25, -0.7, 0.22, 0.4), (-0.25, 0.7, 0.22, 0.4), (0.25, 0.7, 0.22, 0.4), (0.25, -0.7, 0.22, 0.4), (0, 0, 0.8, 0.6)],
        (-0.25, -0.45))

# ---- Q4-Q7: Nexperia PMXB43UNE DFN1010D-3 (SOT1215), 1.0 x 1.1 x 0.37 ----
no_lead("Nexperia_DFN1010D-3_SOT1215", 1.0, 1.1, 0.37,
        [(0.375, -0.45, 0.35, 0.4), (-0.375, -0.45, 0.35, 0.4), (0, 0.45, 0.35, 0.4)],
        (0.3, -0.3))

# ---- Q1, Q3: DFN1006-3 (SOT883-like), 1.0 x 0.6 x 0.48 ----
no_lead("DFN1006-3L_1.0x0.6mm", 1.0, 0.6, 0.48,
        [(-0.35, -0.225, 0.45, 0.25), (-0.35, 0.225, 0.45, 0.25), (0.35, 0, 0.45, 0.7)],
        (-0.2, -0.15))

# ---- U12: SN74HCS00 BQA WQFN-14 2.5 x 3.0 x 0.8 ----
p = [(-0.25, -1.4, 0.25, 0.6)] + [(-1.15, y, 0.6, 0.25) for y in (-1, -0.5, 0, 0.5, 1)] + \
    [(-0.25, 1.4, 0.25, 0.6), (0.25, 1.4, 0.25, 0.6)] + [(1.15, y, 0.6, 0.25) for y in (1, 0.5, 0, -0.5, -1)] + \
    [(0.25, -1.4, 0.25, 0.6), (0, 0, 1.0, 1.5)]
no_lead("Texas_BQA_WQFN-14-1EP_2.5x3mm_P0.5mm", 2.5, 3.0, 0.8, p, (-0.75, -1.1))

# ---- U13: Diodes UDFN2020-6 Type F (DMP2021UFDF), 2 x 2 x 0.6 ----
p = [(-0.9375, y, 0.425, 0.4) for y in (-0.65, 0, 0.65)] + [(0.9375, y, 0.425, 0.4) for y in (0.65, 0, -0.65)] + \
    [(0, -0.325, 1.15, 0.95), (0, 0.7, 0.8, 0.48)]
no_lead("Diodes_UDFN2020-6_Type-F", 2.0, 2.0, 0.6, p, (-0.6, -0.75))

# ---- U5: STM32WL5MOC LGA-92 module, 10 x 10 x 1.6, metal shield ----
lga = []
for i in range(15):
    y = -3.85 + i * 0.55
    lga += [(-4.525, y, 0.35, 0.35), (4.525, y, 0.35, 0.35), (y, -4.525, 0.35, 0.35), (y, 4.525, 0.35, 0.35)]
term = pads_flush(lga, shrink=1.0, t=0.05)
save("ST_LGA-92_10x10mm_STM32WL5MOC", [
    (box(10, 10, 0.75, 0, 0, 0.05), "green"),
    (box(9.6, 9.6, 0.8, 0, 0, 0.8), "metal"),
    (term, "gold"),
    (pin1_dot(-4.0, -4.0, 1.601, 0.6), "black"),
])

# ---- U2: u-blox SAM-M10Q, 15.5 x 15.5 x 6.3 (shielded module + 15 x 15 patch) ----
sam = [(-6.6, y, 1.8, 1.5) for y in (-3.8, -1.9, 0, 1.9, 3.8)] + [(6.6, y, 1.8, 1.5) for y in (-3.8, -1.9, 0, 1.9, 3.8)] + \
      [(x, 6.6, 1.5, 1.8) for x in (-3.8, -1.9, 0, 1.9, 3.8)] + [(x, -6.6, 1.5, 1.8) for x in (-3.8, -1.9, 0, 1.9, 3.8)]
term = pads_flush(sam, shrink=0.8, t=0.05).intersect(box(15.5, 15.5, 1, 0, 0, -0.5))
save("u-blox_SAM-M10Q", [
    (box(15.5, 15.5, 0.8, 0, 0, 0.05), "green"),
    (box(15.3, 15.3, 1.5, 0, 0, 0.85), "metal"),
    (box(15.0, 15.0, 3.9, 0, 0, 2.35), "ceramic"),
    (box(11.0, 11.0, 0.05, 0, 0, 6.25), "silver"),
    (cyl(1.0, 0.1, -1.2, 0, 6.25), "silver"),
    (term, "gold"),
])

# ---- LS1: 14 mm through-hole piezo buzzer (CPT-1404 / PT-1407 class), pins 7.6 mm apart ----
b = cq.Workplane("XY").circle(7.0).extrude(7.0).faces(">Z").workplane().hole(2.5, 2.0)
pins = cyl(0.6, 3.5, -3.8, 0, -3.5).union(cyl(0.6, 3.5, 3.8, 0, -3.5))
save("Buzzer_Piezo_D14mm_H7mm_RM7.6", [
    (b, "black"),
    (pins, "tin"),
    (cyl(1.0, 0.01, -5.5, 0, 7.0), "white"),   # "+" marker near pin 1
])

# ---- J1: Palconn UTC16-G mid-profile USB-C receptacle (approximate) ----
# Shell 8.94 wide, ~7.3 deep, 3.2 high; mating face toward +y (footprint), i.e. the board edge.
outer = cq.Workplane("XZ").rect(8.94, 3.2).extrude(-7.35).edges("|Y").fillet(1.2)
inner = cq.Workplane("XZ").rect(8.34, 2.6).extrude(-7.6).edges("|Y").fillet(0.9)
# XZ workplane normal is -Y, so a negative extrude runs toward +Y: shell spans model y 0..7.35.
# Shift so the mouth sits at footprint y=+5.35 (model y=-5.35).
sh = outer.cut(inner).translate((0, -5.35, 1.6))
tongue = box(6.6, 4.6, 0.7, 0, 2.95, 1.25)
back = box(8.54, 0.6, 2.6, 0, -1.7, 0.3)
legs = None
for (x, y) in ((-4.32, -1.93), (4.32, -1.93), (-4.32, 2.24), (4.32, 2.24)):
    l = box(0.5, 0.9, 1.6, x, y, -1.4)
    legs = l if legs is None else legs.union(l)
smd = None
for x in (-3.2, -2.4, -1.75, -1.25, -0.75, -0.25, 0.25, 0.75, 1.25, 1.75, 2.4, 3.2):
    w = 0.5 if abs(x) >= 2.4 else 0.25
    s = box(w, 1.0, 0.1, x, -2.51, 0)
    smd = s if smd is None else smd.union(s)
save("USB_C_Receptacle_Palconn_UTC16-G", [
    (sh, "metal"), (legs, "metal"), (tongue, "black"), (back, "black"), (smd, "gold"),
])
