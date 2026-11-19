#!/usr/bin/env python3
"""Generate the IKEA furniture pack source for NeonPlan 3D (box/cyl/loft parts)."""
import json
from pathlib import Path


def box(x, z, w, d, y, h, color, **kw):
    return {"shape": "box", "x": x, "z": z, "w": w, "d": d, "y": y, "h": h, "color": color, **kw}


def cyl(x, z, w, d, y, h, color, **kw):
    return {"shape": "cyl", "x": x, "z": z, "w": w, "d": d, "y": y, "h": h, "color": color, **kw}


def item(id, name_de, name_en, size, parts, group, room, tags, **kw):
    return {
        "id": id, "name": {"de": name_de, "en": name_en}, "size": size,
        "group": group, "room": room, "tags": tags, "parts": parts, **kw,
    }


# ---------- archetypes ----------

def table_parts(leg_w=0.05, top_h=0.06, top_color="wood", leg_color="wood", inset=0.05):
    p = [box(0, 0, 1, 1, 1 - top_h, top_h, top_color, edges=True)]
    for x in (-1, 1):
        for z in (-1, 1):
            p.append(box(x * (0.5 - inset - leg_w / 2), z * (0.5 - inset - leg_w / 2),
                         leg_w, leg_w, 0, 1 - top_h, leg_color))
    return p


def chest_parts(drawers, plinth_h=0.06):
    p = [box(0, 0, 1, 1, plinth_h, 1 - plinth_h, "wood", edges=True),
         box(0, 0, 0.92, 0.92, 0, plinth_h, "dark")]
    n = drawers
    gap = 0.02
    fh = (0.96 - plinth_h - gap * n) / n
    for i in range(n):
        y = plinth_h + gap / 2 + i * (fh + gap)
        p.append(box(0, 0.48, 0.9, 0.04, y, fh, "front", edges="faint"))
    return p


def shelf_parts(cols, rows, thick=0.035, color="white", feet_h=0.0):
    """Cube shelf: outer frame + dividers, feet optional (fraction of height)."""
    y0, hh = feet_h, 1 - feet_h
    p = [box(0, 0, 1, 1, y0 + hh - thick, thick, color, edges=True),          # top
         box(0, 0, 1, 1, y0, thick, color),                                   # bottom
         box(-0.5 + thick / 2, 0, thick, 1, y0, hh, color, edges=True),       # left
         box(0.5 - thick / 2, 0, thick, 1, y0, hh, color, edges=True)]        # right
    for i in range(1, cols):
        x = -0.5 + i / cols
        p.append(box(x, 0, thick, 0.96, y0 + thick, hh - 2 * thick, color))
    for j in range(1, rows):
        y = y0 + thick + j * (hh - 2 * thick) / rows + thick / 2
        p.append(box(0, 0, 1 - 2 * thick, 0.96, y, thick, color))
    if feet_h:
        for x in (-0.44, 0.44):
            for z in (-0.42, 0.42):
                p.append(box(x, z, 0.03, 0.05, 0, feet_h, "dark"))
    return p


def sofa_parts(seat_top=0.65, arm_top=0.85, leg_h=0.167, cushions=2):
    p = []
    for x in (-0.42, 0.42):
        for z in (-0.38, 0.38):
            p.append(cyl(x, z, 0.022, 0.045, 0, leg_h, "metal"))
    p += [box(0, 0, 1, 1, leg_h, 0.45 - leg_h + 0.133, "fabric", edges=True),
          box(-0.44, 0, 0.12, 1, leg_h, arm_top - leg_h, "fabric", edges=True),
          box(0.44, 0, 0.12, 1, leg_h, arm_top - leg_h, "fabric", edges=True),
          box(0, -0.42, 0.76, 0.16, 0.4, 0.6, "fabric", edges=True)]
    step = 0.76 / cushions
    for i in range(cushions):
        x = -0.38 + step / 2 + i * step
        w = step - 0.02
        p.append(box(x, 0.14, w, 0.68, 0.45, 0.2, "cushion", edges="faint"))
        p.append(box(x, -0.25, w, 0.18, 0.5, 0.45, "cushion", edges="faint"))
    return p


def armchair_parts(seat_top=0.5, arm_top=0.72, leg_h=0.1):
    p = []
    for x in (-0.4, 0.4):
        for z in (-0.4, 0.4):
            p.append(cyl(x, z, 0.03, 0.05, 0, leg_h, "wood"))
    p += [box(0, 0, 0.92, 0.92, leg_h, 0.35, "fabric", edges=True),
          box(-0.42, 0, 0.14, 0.95, leg_h, arm_top, "fabric", edges=True),
          box(0.42, 0, 0.14, 0.95, leg_h, arm_top, "fabric", edges=True),
          box(0, -0.4, 0.72, 0.18, 0.3, 0.7, "fabric", edges=True),
          box(0, 0.12, 0.6, 0.6, leg_h + 0.35, 0.15, "cushion", edges="faint"),
          box(0, -0.28, 0.6, 0.15, 0.5, 0.42, "cushion", edges="faint")]
    return p


def bed_parts(head_h=0.62, rail_h=0.28, mattress_h=0.18):
    return [box(0, -0.47, 1, 0.06, 0, head_h, "wood", edges=True),               # headboard
            box(0, 0.47, 1, 0.06, 0, rail_h, "wood", edges=True),                # footboard
            box(-0.47, 0, 0.06, 0.94, 0.05, rail_h - 0.05, "wood"),              # side rails
            box(0.47, 0, 0.06, 0.94, 0.05, rail_h - 0.05, "wood"),
            box(0, 0, 0.9, 0.88, rail_h - 0.08, mattress_h, "fabric"),           # mattress
            box(-0.44, -0.44, 0.05, 0.05, 0, 0.05, "dark"),
            box(0.44, -0.44, 0.05, 0.05, 0, 0.05, "dark"),
            box(-0.44, 0.44, 0.05, 0.05, 0, 0.05, "dark"),
            box(0.44, 0.44, 0.05, 0.05, 0, 0.05, "dark")]


def wardrobe_parts(doors=2):
    p = [box(0, 0, 1, 1, 0.04, 0.96, "wood", edges=True),
         box(0, 0, 0.96, 0.96, 0, 0.04, "dark")]
    step = 0.94 / doors
    for i in range(doors):
        x = -0.47 + step / 2 + i * step
        p.append(box(x, 0.48, step - 0.01, 0.04, 0.06, 0.9, "front", edges="faint"))
        p.append(cyl(x + step / 4, 0.5, 0.008, 0.01, 0.5, 0.1, "metal"))
    return p


def chair_parts(back_h=0.55):
    p = [box(0, 0, 0.9, 0.9, 0.42, 0.08, "wood", edges=True),
         box(0, -0.42, 0.85, 0.06, 0.42, back_h, "wood", edges=True)]
    for x in (-0.38, 0.38):
        for z in (-0.38, 0.38):
            p.append(box(x, z, 0.05, 0.05, 0, 0.42, "wood"))
    return p


def desk_pedestal_parts():
    """Desk: top, right drawer pedestal, left leg."""
    return [box(0, 0, 1, 1, 0.93, 0.07, "wood", edges=True),
            box(0.36, 0, 0.24, 0.92, 0.06, 0.87, "white", edges=True),
            box(-0.44, 0, 0.05, 0.9, 0, 0.93, "wood"),
            box(0.36, 0, 0.2, 0.85, 0, 0.06, "dark"),
            box(0.36, 0.44, 0.2, 0.04, 0.14, 0.72, "front", edges="faint"),
            box(0.36, 0.44, 0.2, 0.04, 0.14, 0.2, "front", edges="faint")]


def office_chair_parts():
    return [cyl(0, 0, 0.07, 0.07, 0.1, 0.32, "metal"),
            cyl(0, 0, 0.5, 0.5, 0.06, 0.05, "metal", axis="x"),
            box(0, 0.03, 0.55, 0.5, 0.38, 0.09, "dark", edges=True),
            box(0, -0.28, 0.55, 0.08, 0.45, 0.5, "dark", edges=True),
            box(0, -0.28, 0.4, 0.08, 0.95, 0.05, "dark")]


def trolley_parts():
    p = []
    for i in range(3):
        y = 0.18 + i * 0.33
        p.append(box(0, 0, 0.9, 0.85, y, 0.12, "metal", edges=True))
    for x in (-0.4, 0.4):
        for z in (-0.35, 0.35):
            p.append(cyl(x, z, 0.04, 0.04, 0.14, 0.86, "metal"))
            p.append(cyl(x, z, 0.06, 0.06, 0.02, 0.1, "dark"))
    return p


def shoe_cabinet_parts(comp=2):
    p = [box(0, 0, 1, 1, 0, 1, "white", edges=True)]
    fh = 0.94 / comp
    for i in range(comp):
        p.append(box(0, 0.46, 0.92, 0.06, 0.03 + i * fh, fh - 0.02, "front", edges="faint"))
    return p


def crib_parts():
    p = [box(0, 0, 0.94, 0.88, 0.35, 0.1, "wood")]          # mattress base
    for x in (-0.46, 0.46):
        p.append(box(x, 0, 0.05, 0.95, 0, 0.85, "wood", edges=True))
    for z in (-0.44, 0.44):
        p.append(box(0, z, 0.97, 0.05, 0, 0.85, "wood", edges=True))
    for i in range(-4, 5):
        for z in (-0.44, 0.44):
            p.append(cyl(i * 0.1, z, 0.015, 0.02, 0.35, 0.45, "wood"))
        for x in (-0.46, 0.46):
            p.append(cyl(x, i * 0.09, 0.015, 0.02, 0.35, 0.45, "wood"))
    p.append(box(0, 0, 0.85, 0.8, 0.45, 0.1, "fabric"))
    return p


def loft_bed_parts():
    p = [box(0, -0.44, 1, 0.08, 0, 0.62, "wood", edges=True),
         box(0, 0.44, 1, 0.08, 0, 0.62, "wood", edges=True),
         box(-0.46, 0, 0.08, 0.96, 0, 0.62, "wood", edges=True),
         box(0.46, 0, 0.08, 0.96, 0, 0.62, "wood", edges=True),
         box(0, 0, 0.9, 0.85, 0.5, 0.12, "fabric"),
         box(0.3, 0.4, 0.15, 0.12, 0, 0.55, "wood")]        # ladder
    for i in range(1, 4):
        p.append(box(0.3, 0.4, 0.15, 0.05, i * 0.14, 0.03, "wood"))
    return p


def tv_bench_parts():
    return [box(0, 0, 1, 1, 0.18, 0.76, "white", edges=True),
            box(0, 0, 0.94, 0.9, 0.1, 0.08, "dark"),
            box(-0.25, 0.48, 0.44, 0.04, 0.22, 0.68, "front", edges="faint"),
            box(0.25, 0.48, 0.44, 0.04, 0.22, 0.68, "front", edges="faint"),
            cyl(-0.44, -0.4, 0.02, 0.04, 0, 0.1, "metal"),
            cyl(0.44, -0.4, 0.02, 0.04, 0, 0.1, "metal"),
            cyl(-0.44, 0.4, 0.02, 0.04, 0, 0.1, "metal"),
            cyl(0.44, 0.4, 0.02, 0.04, 0, 0.1, "metal")]


def open_shelf_parts(shelves=4, color="wood", leg="metal"):
    p = []
    for x in (-0.45, 0.45):
        for z in (-0.4, 0.4):
            p.append(box(x, z, 0.04, 0.05, 0, 1, leg))
    for i in range(shelves):
        y = 0.06 + i * (0.94 / (shelves - 1)) if shelves > 1 else 0.5
        p.append(box(0, 0, 1, 0.9, min(y, 0.95), 0.04, color, edges=True))
    return p


def klippan_parts():
    """Klippan 2-seat (180 x 88 x 66 cm): 11 cm leg clearance, seat 43 cm,
    ~54 cm seat depth with 16 cm back cushions flush against the backrest."""
    legs = [cyl(x, z, 0.022, 0.045, 0, 0.167, "metal")
            for z in (-0.38, 0.38) for x in (-0.42, 0.42)]
    return legs + [
        box(0, 0, 1, 1, 0.167, 0.283, "fabric", edges=True),                   # base
        box(-0.44, 0, 0.12, 1, 0.167, 0.683, "fabric", edges=True),            # armrests
        box(0.44, 0, 0.12, 1, 0.167, 0.683, "fabric", edges=True),
        box(0, -0.42, 0.76, 0.16, 0.4, 0.6, "fabric", edges=True),             # backrest
        box(-0.19, 0.14, 0.36, 0.68, 0.45, 0.2, "cushion", edges="faint"),     # seats
        box(0.19, 0.14, 0.36, 0.68, 0.45, 0.2, "cushion", edges="faint"),
        box(-0.19, -0.25, 0.36, 0.18, 0.5, 0.45, "cushion", edges="faint"),    # back cushions
        box(0.19, -0.25, 0.36, 0.18, 0.5, 0.45, "cushion", edges="faint"),
    ]


KLIPPAN_SYMBOL = [{"shape": "rect", "x": 0, "z": 0, "w": 1.0, "d": 1.0},
                  {"shape": "line", "x1": 0, "z1": -0.28, "x2": 0, "z2": 0.42}]


# ---------- the catalogue (W x D x H in metres) ----------

LIVING = "living"
ITEMS = [
    # sofas & chairs
    item("klippan_sofa", "IKEA Klippan Sofa", "IKEA Klippan sofa", [1.8, 0.88, 0.66],
         klippan_parts(), "sofa", [LIVING], ["ikea", "klippan", "couch", "sofa"],
         symbol=KLIPPAN_SYMBOL),
    item("kivik_2", "IKEA Kivik Sofa", "IKEA Kivik 2-seat sofa", [1.9, 0.95, 0.83],
         sofa_parts(seat_top=0.6, arm_top=0.6, cushions=2), "sofa", [LIVING], ["ikea", "kivik", "sofa"]),
    item("soderhamn_3", "IKEA Söderhamn Sofa", "IKEA Söderhamn 3-seat sofa", [1.98, 0.99, 0.83],
         sofa_parts(seat_top=0.5, arm_top=0.55, cushions=3), "sofa", [LIVING], ["ikea", "soderhamn", "sofa"]),
    item("vimle_3", "IKEA Vimle Sofa", "IKEA Vimle 3-seat sofa", [2.41, 0.98, 0.83],
         sofa_parts(seat_top=0.6, arm_top=0.68, cushions=3), "sofa", [LIVING], ["ikea", "vimle", "sofa"]),
    item("ektorp_3", "IKEA Ektorp Sofa", "IKEA Ektorp 3-seat sofa", [2.18, 0.88, 0.88],
         sofa_parts(seat_top=0.55, arm_top=0.75, leg_h=0.05, cushions=3), "sofa", [LIVING], ["ikea", "ektorp", "sofa"]),
    item("friheten", "IKEA Friheten Schlafsofa", "IKEA Friheten sofa bed", [2.25, 1.05, 0.83],
         sofa_parts(seat_top=0.55, arm_top=0.62, cushions=3), "sofa", [LIVING], ["ikea", "friheten", "sofa", "schlafsofa", "sofa bed"]),
    item("poang", "IKEA Poäng Sessel", "IKEA Poäng armchair", [0.68, 0.82, 1.0],
         armchair_parts(seat_top=0.42, arm_top=0.55, leg_h=0.08), "seating", [LIVING], ["ikea", "poang", "sessel", "armchair"]),
    item("strandmon", "IKEA Strandmon Ohrensessel", "IKEA Strandmon wing chair", [0.82, 0.96, 1.01],
         armchair_parts(seat_top=0.45, arm_top=0.7, leg_h=0.12), "seating", [LIVING], ["ikea", "strandmon", "ohrensessel", "wing chair"]),
    # shelves
    item("kallax_4x4", "IKEA Kallax Regal 4x4", "IKEA Kallax shelf 4x4", [1.47, 0.39, 1.47],
         shelf_parts(4, 4), "storage", [LIVING, "office", "kids"], ["ikea", "kallax", "regal", "shelf"]),
    item("kallax_2x4", "IKEA Kallax Regal 2x4", "IKEA Kallax shelf 2x4", [1.47, 0.39, 0.77],
         shelf_parts(4, 2), "storage", [LIVING, "office", "kids"], ["ikea", "kallax", "regal", "shelf"]),
    item("kallax_1x4", "IKEA Kallax Regal 1x4", "IKEA Kallax shelf 1x4", [0.42, 0.39, 1.47],
         shelf_parts(1, 4), "storage", [LIVING, "office"], ["ikea", "kallax", "regal", "shelf"]),
    item("billy", "IKEA Billy Bücherregal", "IKEA Billy bookcase", [0.8, 0.28, 2.02],
         shelf_parts(1, 6, thick=0.03, color="wood"), "storage", [LIVING, "office"], ["ikea", "billy", "regal", "bookcase", "bücherregal"]),
    item("billy_low", "IKEA Billy Regal niedrig", "IKEA Billy bookcase low", [0.8, 0.28, 1.06],
         shelf_parts(1, 3, thick=0.03, color="wood"), "storage", [LIVING, "office"], ["ikea", "billy", "regal", "bookcase"]),
    item("ivar", "IKEA Ivar Regal", "IKEA Ivar shelving unit", [0.89, 0.5, 1.79],
         open_shelf_parts(5), "storage", [LIVING, "utility", "garage"], ["ikea", "ivar", "regal", "shelf"]),
    item("bror", "IKEA Bror Regal", "IKEA Bror shelving unit", [0.85, 0.4, 1.9],
         open_shelf_parts(4, color="dark", leg="dark"), "storage", ["utility", "garage", "office"], ["ikea", "bror", "regal", "shelf"]),
    # tables
    item("lack_side", "IKEA Lack Beistelltisch", "IKEA Lack side table", [0.55, 0.55, 0.45],
         table_parts(leg_w=0.09, top_h=0.1, top_color="white", leg_color="white", inset=0.02), "table", [LIVING], ["ikea", "lack", "beistelltisch", "side table"]),
    item("lack_coffee", "IKEA Lack Couchtisch", "IKEA Lack coffee table", [1.18, 0.78, 0.45],
         table_parts(leg_w=0.07, top_h=0.1, top_color="white", leg_color="white", inset=0.02), "table", [LIVING], ["ikea", "lack", "couchtisch", "coffee table"]),
    item("besta_tv", "IKEA Bestå TV-Bank", "IKEA Bestå TV bench", [1.2, 0.4, 0.48],
         tv_bench_parts(), "media", [LIVING], ["ikea", "besta", "tv", "tv bank", "tv bench"]),
    item("besta_tall", "IKEA Bestå Schrank", "IKEA Bestå storage combination", [1.2, 0.4, 1.92],
         wardrobe_parts(3), "storage", [LIVING, "office"], ["ikea", "besta", "schrank", "storage"]),
    # bedroom
    item("malm_bed_160", "IKEA Malm Bett 160", "IKEA Malm bed 160x200", [1.76, 2.09, 1.0],
         bed_parts(), "bed", ["bedroom"], ["ikea", "malm", "bett", "bed"]),
    item("malm_chest4", "IKEA Malm Kommode 4", "IKEA Malm chest of 4 drawers", [0.8, 0.48, 1.0],
         chest_parts(4), "storage", ["bedroom"], ["ikea", "malm", "kommode", "chest of drawers"]),
    item("malm_chest6", "IKEA Malm Kommode 6", "IKEA Malm chest of 6 drawers", [0.8, 0.48, 1.23],
         chest_parts(6), "storage", ["bedroom"], ["ikea", "malm", "kommode", "chest of drawers"]),
    item("malm_chest6w", "IKEA Malm Kommode breit", "IKEA Malm wide chest of 6", [1.6, 0.48, 0.78],
         chest_parts(3), "storage", ["bedroom"], ["ikea", "malm", "kommode", "chest of drawers"]),
    item("malm_night", "IKEA Malm Nachttisch", "IKEA Malm nightstand", [0.4, 0.48, 0.55],
         chest_parts(2, plinth_h=0.08), "storage", ["bedroom"], ["ikea", "malm", "nachttisch", "nightstand"]),
    item("pax_100", "IKEA Pax Schrank 100", "IKEA Pax wardrobe 100", [1.0, 0.6, 2.36],
         wardrobe_parts(2), "storage", ["bedroom"], ["ikea", "pax", "kleiderschrank", "wardrobe"]),
    item("pax_75", "IKEA Pax Schrank 75", "IKEA Pax wardrobe 75", [0.75, 0.58, 2.36],
         wardrobe_parts(2), "storage", ["bedroom"], ["ikea", "pax", "kleiderschrank", "wardrobe"]),
    item("hemnes_chest8", "IKEA Hemnes Kommode", "IKEA Hemnes chest of 8 drawers", [1.6, 0.5, 0.96],
         chest_parts(4), "storage", ["bedroom"], ["ikea", "hemnes", "kommode", "chest of drawers"]),
    # office
    item("micke_desk", "IKEA Micke Schreibtisch", "IKEA Micke desk", [1.05, 0.5, 0.75],
         desk_pedestal_parts(), "office", ["office"], ["ikea", "micke", "schreibtisch", "desk"]),
    item("alex_unit", "IKEA Alex Rollcontainer", "IKEA Alex drawer unit", [0.36, 0.58, 0.7],
         chest_parts(5, plinth_h=0.04), "office", ["office"], ["ikea", "alex", "rollcontainer", "drawer unit"]),
    item("alex_desk", "IKEA Alex Schreibtisch", "IKEA Alex desk", [1.32, 0.58, 0.76],
         desk_pedestal_parts(), "office", ["office"], ["ikea", "alex", "schreibtisch", "desk"]),
    item("linnmon", "IKEA Linnmon/Adils Tisch", "IKEA Linnmon/Adils table", [1.2, 0.6, 0.74],
         table_parts(leg_w=0.05, top_h=0.05, inset=0.04), "table", ["office"], ["ikea", "linnmon", "adils", "tisch", "table", "desk"]),
    item("markus", "IKEA Markus Bürostuhl", "IKEA Markus office chair", [0.62, 0.6, 1.35],
         office_chair_parts(), "office", ["office"], ["ikea", "markus", "bürostuhl", "office chair"]),
    # dining
    item("jokkmokk", "IKEA Jokkmokk Tisch", "IKEA Jokkmokk table", [1.18, 0.74, 0.74],
         table_parts(leg_w=0.06, top_h=0.05), "table", ["dining", "kitchen"], ["ikea", "jokkmokk", "esstisch", "dining table"]),
    item("lisabo", "IKEA Lisabo Tisch", "IKEA Lisabo table", [1.4, 0.78, 0.74],
         table_parts(leg_w=0.05, top_h=0.05, inset=0.08), "table", ["dining"], ["ikea", "lisabo", "esstisch", "dining table"]),
    item("melltorp", "IKEA Melltorp Tisch", "IKEA Melltorp table", [1.25, 0.75, 0.74],
         table_parts(leg_w=0.05, top_h=0.04, top_color="white", leg_color="metal", inset=0.03), "table", ["dining", "kitchen"], ["ikea", "melltorp", "esstisch", "dining table"]),
    item("ekedalen", "IKEA Ekedalen Tisch", "IKEA Ekedalen extendable table", [1.2, 0.8, 0.75],
         table_parts(leg_w=0.07, top_h=0.05, inset=0.06), "table", ["dining"], ["ikea", "ekedalen", "esstisch", "dining table"]),
    item("stefan", "IKEA Stefan Stuhl", "IKEA Stefan chair", [0.42, 0.49, 0.9],
         chair_parts(0.5), "seating", ["dining", "kitchen"], ["ikea", "stefan", "stuhl", "chair"]),
    item("adde", "IKEA Adde Stuhl", "IKEA Adde chair", [0.39, 0.47, 0.77],
         chair_parts(0.45), "seating", ["dining", "kitchen"], ["ikea", "adde", "stuhl", "chair"]),
    # hallway & misc
    item("raskog", "IKEA Råskog Rollwagen", "IKEA Råskog trolley", [0.35, 0.45, 0.78],
         trolley_parts(), "storage", ["kitchen", "bath", "office"], ["ikea", "raskog", "rollwagen", "trolley"]),
    item("trones", "IKEA Trones Schuhschrank", "IKEA Trones shoe cabinet", [0.52, 0.18, 0.39],
         shoe_cabinet_parts(2), "storage", ["hall"], ["ikea", "trones", "schuhschrank", "shoe cabinet"]),
    item("hemnes_shoe", "IKEA Hemnes Schuhschrank", "IKEA Hemnes shoe cabinet", [1.07, 0.22, 1.01],
         shoe_cabinet_parts(4), "storage", ["hall"], ["ikea", "hemnes", "schuhschrank", "shoe cabinet"]),
    # kids
    item("kura", "IKEA Kura Bett", "IKEA Kura reversible bed", [0.99, 2.09, 1.16],
         loft_bed_parts(), "kids", ["kids"], ["ikea", "kura", "kinderbett", "kids bed"]),
    item("mammut_table", "IKEA Mammut Kindertisch", "IKEA Mammut children's table", [0.77, 0.55, 0.48],
         table_parts(leg_w=0.08, top_h=0.1, inset=0.06), "kids", ["kids"], ["ikea", "mammut", "kindertisch", "kids table"]),
    item("mammut_chair", "IKEA Mammut Kinderstuhl", "IKEA Mammut children's chair", [0.39, 0.36, 0.67],
         chair_parts(0.4), "kids", ["kids"], ["ikea", "mammut", "kinderstuhl", "kids chair"]),
    item("gulliver", "IKEA Gulliver Babybett", "IKEA Gulliver cot", [0.66, 1.24, 0.8],
         crib_parts(), "kids", ["kids", "bedroom"], ["ikea", "gulliver", "babybett", "cot", "crib"]),
]


def main():
    items = ITEMS
    pack = {
        "format": "fp3dpack",
        "version": 1,
        "id": "mohnen.ikea",
        "name": "IKEA",
        "publisher": "mohnen",
        "release": 6,
        "description": "IKEA furniture: Klippan, Kallax, Billy, Malm, Pax, Lack, Besta and more",
        "items": items,
    }
    out = Path(__file__).with_name("ikea.json")
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    main()
