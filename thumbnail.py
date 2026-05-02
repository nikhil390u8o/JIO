from PIL import Image, ImageDraw, ImageFont
import io, textwrap

FONT_PATH = "fonts/Impact.ttf"
BG_IMAGE = "BG.jpg"

def sec_to_time(sec):
    sec = int(sec)
    m = sec // 60
    s = sec % 60
    return f"{m}:{s:02d}"

def generate_thumb(song_json):
    # Required fields from JSON
    song = song_json.get("song", "Unknown Song")
    artist = song_json.get("primary_artists", "Unknown Artist")
    duration = sec_to_time(song_json.get("duration", 0))

    img = Image.open(BG_IMAGE).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # Responsive font
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

    # Draw song title
    for line, box, h in dims:
        x = (W - (box[2] - box[0])) / 2
        draw.text((x, y), line, font=title_font, fill="#39ff14")
        y += h + 20

    # Draw artist + duration
    info = f"{artist}  •  {duration}"
    box = draw.textbbox((0, 0), info, font=info_font)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y + 10), info, font=info_font, fill="white")

    bio = io.BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio
