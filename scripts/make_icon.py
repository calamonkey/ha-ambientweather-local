"""Generate the integration icon (custom_components/ambientweather_local/brand/).

Run: python scripts/make_icon.py   (needs Pillow)
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "custom_components" / "ambientweather_local" / "brand"
SS = 4  # supersampling factor for smooth edges


def draw(size: int) -> Image.Image:
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    # Rounded-square background with a vertical sky gradient.
    grad = Image.new("RGBA", (s, s))
    gp = grad.load()
    top, bot = (38, 132, 214), (92, 190, 240)
    for y in range(s):
        t = y / (s - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(s):
            gp[x, y] = c
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)

    def p(v: float) -> int:
        return int(v * s)

    # Sun peeking out behind the cloud.
    sun = (255, 205, 60, 255)
    d.ellipse((p(0.50), p(0.14), p(0.82), p(0.46)), fill=sun)

    # Cloud.
    white = (255, 255, 255, 255)
    d.ellipse((p(0.14), p(0.40), p(0.42), p(0.68)), fill=white)
    d.ellipse((p(0.28), p(0.30), p(0.62), p(0.64)), fill=white)
    d.ellipse((p(0.50), p(0.38), p(0.80), p(0.68)), fill=white)
    d.rounded_rectangle((p(0.22), p(0.50), p(0.72), p(0.68)), radius=p(0.09), fill=white)

    # "Local" mark: Wi-Fi style arcs under the cloud (data stays on the LAN).
    cx, cy = p(0.50), p(0.86)
    arc = (30, 95, 170, 255)
    for r, w in ((0.20, 0.04), (0.13, 0.04)):
        box = (cx - p(r), cy - p(r), cx + p(r), cy + p(r))
        d.arc(box, 225, 315, fill=white, width=p(w))
    d.ellipse((cx - p(0.03), cy - p(0.03), cx + p(0.03), cy + p(0.03)), fill=white)

    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    draw(256).save(OUT / "icon.png")
    draw(512).save(OUT / "icon@2x.png")
    print("wrote", OUT)
