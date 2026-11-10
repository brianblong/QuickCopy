"""Regenerate the neutral copy artwork. Developer-only dependency: Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def draw_mark(size, color, tile=None):
    scale = 4
    image = Image.new("RGBA", (size * scale, size * scale))
    draw = ImageDraw.Draw(image)
    unit = size * scale / 64
    box = lambda values: tuple(round(value * unit) for value in values)
    if tile:
        draw.rounded_rectangle(box((0, 0, 64, 64)), radius=round(15 * unit), fill=tile)
    for rectangle in [(27, 14, 48, 39), (16, 25, 37, 50)]:
        draw.rounded_rectangle(box(rectangle), radius=round(4 * unit),
                               fill=tile, outline=color, width=round(3 * unit))
    return image.resize((size, size), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    logo = draw_mark(256, "#25292f", "#c6cbd2")
    logo.save(ASSETS / "quickcopy.png")
    logo.save(ASSETS / "quickcopy.ico", sizes=[(16, 16), (24, 24), (32, 32),
                                              (48, 48), (64, 64), (128, 128), (256, 256)])
    draw_mark(24, "#d5d9df").save(ASSETS / "copy-light.png")
