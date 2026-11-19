#!/usr/bin/env python3
"""Generate the JYSK furniture pack source for NeonPlan 3D.

Reuses the archetype helpers from gen_ikea_pack.py (same directory).
Dimensions are the official JYSK "size assembled" specs (W x D x H metres).
"""
import json
from pathlib import Path

from gen_ikea_pack import (bed_parts, chair_parts, chest_parts, item,
                           office_chair_parts, shelf_parts, shoe_cabinet_parts,
                           sofa_parts, table_parts, tv_bench_parts,
                           wardrobe_parts, LIVING)

DINING, BEDROOM, OFFICE, HALL = "dining", "bedroom", "office", "hall"

ITEMS = [
    # sofas & sofa beds
    item("falslev_3", "JYSK Falslev Sofa", "JYSK Falslev 3-seat sofa", [2.16, 0.84, 0.78],
         sofa_parts(seat_top=0.55, arm_top=0.65, cushions=3), "sofa", [LIVING],
         ["jysk", "falslev", "sofa"]),
    item("vejlby_sofa_bed", "JYSK Vejlby Schlafsofa", "JYSK Vejlby 3-seat sofa bed", [2.4, 0.88, 0.86],
         sofa_parts(seat_top=0.57, arm_top=0.6, cushions=3), "sofa", [LIVING],
         ["jysk", "vejlby", "schlafsofa", "sofa bed"]),

    # dining room
    item("kalby_table", "JYSK Kalby Tisch", "JYSK Kalby dining table", [1.6, 0.9, 0.76],
         table_parts(), "table", [DINING], ["jysk", "kalby", "esstisch", "dining"]),
    item("munkeby_table", "JYSK Munkeby Tisch", "JYSK Munkeby dining table", [1.8, 0.9, 0.75],
         table_parts(), "table", [DINING], ["jysk", "munkeby", "esstisch", "dining"]),
    item("tylstrup_table", "JYSK Tylstrup Tisch", "JYSK Tylstrup dining table", [1.18, 0.75, 0.73],
         table_parts(), "table", [DINING], ["jysk", "tylstrup", "esstisch", "dining"]),
    item("tylstrup_chair", "JYSK Tylstrup Stuhl", "JYSK Tylstrup chair", [0.42, 0.5, 0.86],
         chair_parts(), "seating", [DINING], ["jysk", "tylstrup", "stuhl", "chair"]),
    item("jonstrup_chair", "JYSK Jonstrup Stuhl", "JYSK Jonstrup dining chair", [0.45, 0.54, 0.88],
         chair_parts(), "seating", [DINING], ["jysk", "jonstrup", "stuhl", "chair"]),

    # bedroom
    item("vedde_bed", "JYSK Vedde Bett 160", "JYSK Vedde bed 160x200", [1.7, 2.07, 1.01],
         bed_parts(head_h=1.0, rail_h=0.38, mattress_h=0.22), "bed", [BEDROOM],
         ["jysk", "vedde", "bett", "bed"]),
    item("kabdrup_night", "JYSK Kabdrup Nachttisch", "JYSK Kabdrup bedside table", [0.41, 0.32, 0.48],
         chest_parts(1), "storage", [BEDROOM], ["jysk", "kabdrup", "nachttisch", "nightstand"]),
    item("limfjorden_chest4", "JYSK Limfjorden Kommode", "JYSK Limfjorden chest of 4 drawers",
         [0.81, 0.48, 1.01], chest_parts(4), "storage", [BEDROOM],
         ["jysk", "limfjorden", "kommode", "chest"]),
    item("jenslev_wardrobe", "JYSK Jenslev Schrank", "JYSK Jenslev wardrobe 3 doors",
         [1.44, 0.5, 1.76], wardrobe_parts(doors=3), "storage", [BEDROOM],
         ["jysk", "jenslev", "kleiderschrank", "wardrobe"]),

    # office
    item("stavanger_desk", "JYSK Stavanger Schreibtisch", "JYSK Stavanger desk", [1.6, 0.8, 0.75],
         table_parts(), "office", [OFFICE], ["jysk", "stavanger", "schreibtisch", "desk"]),
    item("dalmose_chair", "JYSK Dalmose Bürostuhl", "JYSK Dalmose office chair", [0.62, 0.61, 0.98],
         office_chair_parts(), "office", [OFFICE], ["jysk", "dalmose", "buerostuhl", "office chair"]),

    # storage & living
    item("horsens_shelf", "JYSK Horsens Regal", "JYSK Horsens bookcase 5 shelves", [0.7, 0.3, 1.97],
         shelf_parts(1, 5), "storage", [LIVING], ["jysk", "horsens", "regal", "bookcase"]),
    item("haldager_16", "JYSK Haldager Raumteiler", "JYSK Haldager room divider 16 cubes",
         [1.4, 0.35, 1.47], shelf_parts(4, 4), "storage", [LIVING],
         ["jysk", "haldager", "raumteiler", "room divider", "cube shelf"]),
    item("farsund_tv", "JYSK Farsund TV-Bank", "JYSK Farsund TV bench", [1.6, 0.4, 0.55],
         tv_bench_parts(), "media", [LIVING], ["jysk", "farsund", "tv", "tv bench"]),
    item("bagenkop_shoe", "JYSK Bagenkop Schuhschrank", "JYSK Bagenkop shoe cabinet 3 comp",
         [0.65, 0.26, 1.0], shoe_cabinet_parts(3), "storage", [HALL],
         ["jysk", "bagenkop", "schuhschrank", "shoe cabinet"]),
    item("lejre_coffee", "JYSK Lejre Couchtisch", "JYSK Lejre coffee table", [1.2, 0.6, 0.45],
         table_parts(), "table", [LIVING], ["jysk", "lejre", "couchtisch", "coffee table"]),
    item("vedde_coffee", "JYSK Vedde Couchtisch", "JYSK Vedde coffee table", [1.1, 0.6, 0.45],
         table_parts(), "table", [LIVING], ["jysk", "vedde", "couchtisch", "coffee table"]),
]


def main():
    pack = {
        "format": "fp3dpack",
        "version": 1,
        "id": "mohnen.jysk",
        "name": "JYSK",
        "publisher": "mohnen",
        "release": 1,
        "description": "JYSK furniture: Falslev, Vejlby, Kalby, Tylstrup, Vedde, Jenslev and more",
        "items": ITEMS,
    }
    out = Path(__file__).with_name("jysk.json")
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(ITEMS)} items -> {out}")


if __name__ == "__main__":
    main()
