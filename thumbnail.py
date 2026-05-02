from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

FONT_PATH = "fonts/Impact.ttf"
BG_IMAGE = "static/BG.jpg"


def sec_to_time(sec):
    try:
        sec = int(sec)
        m = sec // 60
        s = sec % 60
        return f"{m}:{s:02d}"
    except:
        return "0:00"


def generate_thumbnail(song_json):
    # ✅ Correct JioSaavn keys
    song = song_json.get("title", "Unknown Song")
    artist = song_json.get("subtitle", "Unknown Artist")
    duration = sec_to_time(
        song_json.get("more_info", {}).get("duration", 0)
    )

    img = Image.open(BG_IMAGE).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype(FONT_PATH, int(W * 0.065))
    info_font = ImageFont.truetype(FONT_PATH, int(W * 0.035))

    # Wrap title
    wrap_width = int(W / 70)
    lines = textwrap.wrap(song, width=wrap_width)

    total_h = 0
    dims = []
    for line in lines:
        box = draw.textbbox((0, 0), line, font=title_font)
        h = box[3] - box[1]
        total_h += h + 20
        dims.append((line, box, h))

    y = (H - total_h) / 2

    for line, box, h in dims:
        x = (W - (box[2] - box[0])) / 2
        draw.text((x, y), line, font=title_font, fill="#39ff14")
        y += h + 20

    info = f"{artist}  •  {duration}"
    box = draw.textbbox((0, 0), info, font=info_font)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y + 10), info, font=info_font, fill="white")

    # ✅ SAVE IN MEMORY (not disk)
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return img_io
