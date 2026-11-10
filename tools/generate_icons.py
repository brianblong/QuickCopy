"""Regenerate the neutral copy artwork. Developer-only dependency: Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def draw_mark(size, color, tile=None):
    scale = 4
    image = Image.new("RGBA", (size * scale, size * scale))
    draw = ImageDraw.Draw(image)
    unit = size * scale / 24
    box = lambda values: tuple(round(value * unit) for value in values)
    if tile:
        draw.rounded_rectangle(box((0, 0, 24, 24)), radius=round(5 * unit), fill=tile)
    for rectangle in [(9, 3, 21, 15), (3, 9, 15, 21)]:
        draw.rounded_rectangle(box(rectangle), radius=round(2 * unit),
                               fill=tile or (0, 0, 0, 0), outline=color, width=round(1.7 * unit))
    return image.resize((size, size), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    logo = draw_mark(256, "#292d33")
    logo.save(ASSETS / "quickcopy.png")
    logo.save(ASSETS / "quickcopy.ico", sizes=[(16, 16), (24, 24), (32, 32),
                                              (48, 48), (64, 64), (128, 128), (256, 256)])
    draw_mark(20, "#d5d9df").save(ASSETS / "copy-light.png")
    check = Image.new("RGBA", (80, 80))
    ImageDraw.Draw(check).line([(20, 41), (34, 55), (60, 26)], fill="#d5d9df", width=6, joint="curve")
    check.resize((20, 20), Image.Resampling.LANCZOS).save(ASSETS / "check-light.png")
    for name, size, color in [("button", 34, "#2d3239"), ("button-hover", 34, "#414852"),
                               ("plus", 40, "#c6ccd5"), ("plus-hover", 40, "#e1e5eb")]:
        disk = Image.new("RGBA", (size * 4, size * 4))
        ImageDraw.Draw(disk).ellipse((8, 8, size * 4 - 8, size * 4 - 8), fill=color)
        disk.resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"{name}.png")
