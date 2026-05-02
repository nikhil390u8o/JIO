from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import textwrap
import requests

FONT_PATH = "fonts/Impact.ttf"
BG_IMAGE = "static/BG.jpg"

OWNER = "@ll_PANDA_BBY_ll"
CHANNEL = "t.me/sxyaru"


def sec_to_time(sec):
    try:
        sec = int(sec)
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"
    except:
        return "00:00"


def fetch_image(url):
    try:
        r = requests.get(url, timeout=5)
        return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        return None


def rounded_crop(img, radius=40):
    img = img.resize((300, 300))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, *img.size], radius=radius, fill=255)
    output = Image.new("RGBA", img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    return output


def draw_progress_bar(draw, x, y, width, height,
                      track_color="#444444", fill_color="#00BFFF", thumb_color="white"):
    draw.rounded_rectangle([x, y, x + width, y + height], radius=height // 2, fill=track_color)
    cx = x
    cy = y + height // 2
    r = height + 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=thumb_color)


def generate_thumbnail(song_json):
    song = song_json.get("song", "Unknown Song")
    artist = song_json.get("artist", "Unknown Artist")
    duration = sec_to_time(song_json.get("duration", 0))
    image_url = song_json.get("image", "")

    # ── Canvas — BG.jpg as background ───────────────────
    W, H = 900, 380
    canvas = Image.open(BG_IMAGE).convert("RGB").resize((W, H))

    # Dark overlay for text readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 140))
    canvas = canvas.convert("RGBA")
    canvas = Image.alpha_composite(canvas, overlay)
    canvas = canvas.convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # ── Album Art (left) ────────────────────────────────
    art_x, art_y = 35, 40
    album_art = fetch_image(image_url)
    if album_art:
        art = rounded_crop(album_art, radius=30)
        canvas.paste(art, (art_x, art_y), art)
    else:
        draw.rounded_rectangle([art_x, art_y, art_x + 300, art_y + 300], radius=30, fill="#333355")

    # ── Right panel ─────────────────────────────────────
    rx = 370
    ry = 45

    title_font = ImageFont.truetype(FONT_PATH, 46)
    artist_font = ImageFont.truetype(FONT_PATH, 28)
    small_font = ImageFont.truetype(FONT_PATH, 22)
    tag_font = ImageFont.truetype(FONT_PATH, 18)

    # Song title
    lines = textwrap.wrap(song, width=22)[:2]
    for line in lines:
        draw.text((rx, ry), line, font=title_font, fill="#FFD700")
        ry += 54

    # Artist
    artist_short = artist[:45] + "..." if len(artist) > 45 else artist
    draw.text((rx, ry + 5), artist_short, font=artist_font, fill="#00BFFF")
    ry += 42

    # Divider
    draw.line([(rx, ry + 10), (W - 20, ry + 10)], fill="#ffffff44", width=1)
    ry += 25

    # ── Progress Bar ────────────────────────────────────
    bar_x = rx
    bar_w = W - rx - 25
    bar_y = ry + 10
    bar_h = 7

    draw_progress_bar(draw, bar_x, bar_y, bar_w, bar_h,
                      track_color="#444466",
                      fill_color="#00BFFF",
                      thumb_color="white")

    # Times
    time_y = bar_y + bar_h + 10
    draw.text((bar_x, time_y), "00:00", font=small_font, fill="#aaaacc")
    dur_box = draw.textbbox((0, 0), duration, font=small_font)
    draw.text((bar_x + bar_w - (dur_box[2] - dur_box[0]), time_y),
              duration, font=small_font, fill="#aaaacc")

    # ── Watermark ───────────────────────────────────────
    wm_y = H - 32
    draw.text((20, wm_y), OWNER, font=tag_font, fill="#FF6B6B")
    powered = f"Powered by {CHANNEL}"
    pw_box = draw.textbbox((0, 0), powered, font=tag_font)
    draw.text((W - (pw_box[2] - pw_box[0]) - 15, wm_y),
              powered, font=tag_font, fill="#888899")

    # ── Output ──────────────────────────────────────────
    img_io = BytesIO()
    canvas.save(img_io, "PNG")
    img_io.seek(0)
    return img_io
