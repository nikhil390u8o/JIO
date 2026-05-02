from PIL import Image, ImageDraw, ImageFont
import io, textwrap

FONT_PATH = "fonts/BraveThorn-Regular.ttf"
BG_IMAGE = "BG.jpg"

def generate_thumb(song, artist, duration):
    img = Image.open(BG_IMAGE).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # Font size auto-scale based on width
    title_size = int(W * 0.065)   # responsive
    info_size = int(W * 0.035)

    title_font = ImageFont.truetype(FONT_PATH, title_size)
    info_font = ImageFont.truetype(FONT_PATH, info_size)

    # Wrap song title
    wrap_width = int(W / 70)
    lines = textwrap.wrap(song, width=wrap_width)

    total_height = 0
    bboxes = []

    for line in lines:
        box = draw.textbbox((0, 0), line, font=title_font)
        h = box[3] - box[1]
        total_height += h + 20
        bboxes.append((line, box, h))

    # Start vertically centered
    y = (H - total_height) / 2

    # Draw title
    for line, box, h in bboxes:
        text_w = box[2] - box[0]
        x = (W - text_w) / 2
        draw.text((x, y), line, font=title_font, fill="#39ff14")
        y += h + 20

    # Artist + duration
    info = f"{artist}  •  {duration}"
    box = draw.textbbox((0, 0), info, font=info_font)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y + 10), info, font=info_font, fill="white")

    bio = io.BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio
