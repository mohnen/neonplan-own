"""Generate brand icons for neonplan_ownkeys (icon.png / icon@2x.png).

Design: an isometric neon "room" (matching the neonplan3d brand icon) acts
as the bow of a key; shaft and teeth extend to the right. Everything is
drawn in the same neon-wireframe style: dark navy squircle, cyan glow,
purple partition wall, orange dot.

All geometry is specified in 256px user space and supersampled by S.

Run:  uv run --with pillow python tools/make_icon.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

S = 4  # supersampling factor; final icon is 256px
SZ = 256 * S

BG = (9, 18, 35, 255)
CYAN = (0, 214, 255, 255)
CYAN_CORE = (220, 250, 255, 255)
PURPLE = (140, 96, 250, 255)
PURPLE_CORE = (230, 215, 255, 255)
ORANGE = (255, 181, 69, 255)
ORANGE_CORE = (255, 240, 215, 255)

W = 10 * S          # wireframe line width
GLOW1, GLOW2 = 6 * S, 16 * S


def neon(img, draw_fn, color, core):
    """Composite draw_fn as neon: colored glow + bright core."""
    for blur in (GLOW2, GLOW1):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(layer), color, W)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), core, int(W * 0.55))
    img.alpha_composite(layer)


def neon_fill(img, draw_fn, color, core, blur1=8 * S, blur2=22 * S):
    """Like neon(), for filled shapes (dot)."""
    for blur in (blur2, blur1):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(layer), color)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), core)
    img.alpha_composite(layer)


def main() -> None:
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        [2 * S, 2 * S, SZ - 2 * S, SZ - 2 * S], radius=56 * S, fill=BG
    )

    # --- key bow: isometric wireframe room ---
    cx, cy, hw, hh, wdep = 78 * S, 116 * S, 38 * S, 19 * S, 28 * S
    L = (cx - hw, cy)
    T = (cx, cy - hh)
    R = (cx + hw, cy)
    B = (cx, cy + hh)
    Ld, Bd, Rd = (L[0], L[1] + wdep), (B[0], B[1] + wdep), (R[0], R[1] + wdep)

    def room(dd, col, w):
        dd.line([L, T, R, B, L], fill=col, width=w, joint="curve")
        dd.line([L, Ld, Bd, Rd, R], fill=col, width=w, joint="curve")
        dd.line([B, Bd], fill=col, width=w)

    neon(img, room, CYAN, CYAN_CORE)

    # purple partition wall (like the neonplan icon)
    mid_rb = ((R[0] + B[0]) // 2, (R[1] + B[1]) // 2)
    neon(img, lambda dd, col, w: dd.line([T, mid_rb], fill=col, width=w),
         PURPLE, PURPLE_CORE)

    # --- key shaft + teeth (cyan neon), centered on the room's right vertex ---
    shaft = 10 * S
    y0 = cy - shaft // 2
    x_end = 220 * S

    def key(dd, col, w):
        dd.rounded_rectangle(
            [R[0] - 5 * S, y0, x_end, y0 + shaft],
            radius=shaft // 2, fill=col,
        )
        for x1, depth in ((172, 16), (196, 22)):
            dd.rounded_rectangle(
                [x1 * S, y0, x1 * S + 9 * S, y0 + shaft + depth * S],
                radius=4 * S, fill=col,
            )

    neon(img, key, CYAN, CYAN_CORE)

    # --- orange dot on the room floor ---
    r = 5 * S
    dx, dy = cx - 12 * S, cy + 12 * S
    neon_fill(
        img,
        lambda dd, col: dd.ellipse([dx - r, dy - r, dx + r, dy + r], fill=col),
        ORANGE, ORANGE_CORE,
    )

    out = Path(__file__).resolve().parent.parent / "custom_components" / "neonplan_ownkeys" / "brand"
    out.mkdir(parents=True, exist_ok=True)
    img.resize((256, 256), Image.LANCZOS).save(out / "icon.png")
    img.resize((512, 512), Image.LANCZOS).save(out / "icon@2x.png")
    print(f"wrote {out / 'icon.png'} and icon@2x.png")


if __name__ == "__main__":
    main()
