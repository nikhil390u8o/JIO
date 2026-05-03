from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import textwrap
import requests
import os

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts", "JIB.otf")
BG_IMAGE  = os.path.join(BASE_DIR, "static", "BG.jpg")

OWNER   = "@ll_PANDA_BBY_ll"
CHANNEL = "ARU X API [BOTS]"


def sec_to_time(sec):
    try:
        sec = int(sec)
        m = sec // 60
        s = sec % 60
        return f"{m:02d}.{s:02d}"  # dot instead of colon (JIB.otf has no colon)
    except:
        return "00.00"


def load_font(size):
    """Font load karo — fail hone pe raise karo taaki pata chale"""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception as e:
        print(f"[FONT ERROR] {FONT_PATH} load failed: {e}")
        # Fallback: system font try karo
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            return ImageFont.load_default()


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
    song      = song_json.get("song", "Unknown Song")
    artist    = song_json.get("artist", "Unknown Artist")
    duration  = sec_to_time(song_json.get("duration", 0))
    image_url = song_json.get("image", "")

    # ── Canvas ──────────────────────────────────────────
    W, H   = 900, 380
    canvas = Image.open(BG_IMAGE).convert("RGB").resize((W, H))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 140))
    canvas  = canvas.convert("RGBA")
    canvas  = Image.alpha_composite(canvas, overlay)
    canvas  = canvas.convert("RGB")
    draw    = ImageDraw.Draw(canvas)

    # ── Album Art ───────────────────────────────────────
    art_x, art_y = 35, 40
    album_art = fetch_image(image_url)
    if album_art:
        art = rounded_crop(album_art, radius=30)
        canvas.paste(art, (art_x, art_y), art)
    else:
        draw.rounded_rectangle([art_x, art_y, art_x + 300, art_y + 300], radius=30, fill="#333355")

    # ── Fonts ────────────────────────────────────────────
    title_font  = load_font(46)
    artist_font = load_font(28)
    small_font  = load_font(22)
    tag_font    = load_font(18)

    # ── Right panel ──────────────────────────────────────
    rx = 370
    ry = 45

    lines = textwrap.wrap(song, width=22)[:2]
    for line in lines:
        draw.text((rx, ry), line, font=title_font, fill="#FFD700")
        ry += 54

    artist_short = artist[:45] + "..." if len(artist) > 45 else artist
    draw.text((rx, ry + 5), artist_short, font=artist_font, fill="#00BFFF")
    ry += 42

    draw.line([(rx, ry + 10), (W - 20, ry + 10)], fill="#ffffff44", width=1)
    ry += 25

    # ── Progress Bar ─────────────────────────────────────
    bar_x = rx
    bar_w = W - rx - 25
    bar_y = ry + 10
    bar_h = 7

    draw_progress_bar(draw, bar_x, bar_y, bar_w, bar_h,
                      track_color="#444466",
                      fill_color="#00BFFF",
                      thumb_color="white")

    # ✅ "00.00" — dot use karo, colon nahi (JIB.otf issue)
    time_y     = bar_y + bar_h + 10
    start_time = "00.00"
    draw.text((bar_x, time_y), start_time, font=small_font, fill="#aaaacc")
    dur_box = draw.textbbox((0, 0), duration, font=small_font)
    draw.text((bar_x + bar_w - (dur_box[2] - dur_box[0]), time_y),
              duration, font=small_font, fill="#aaaacc")

    # ── Watermark ────────────────────────────────────────
    wm_y    = H - 32
    powered = f"Powered by {CHANNEL}"
    draw.text((20, wm_y), OWNER, font=tag_font, fill="#FF6B6B")
    pw_box = draw.textbbox((0, 0), powered, font=tag_font)
    draw.text((W - (pw_box[2] - pw_box[0]) - 15, wm_y),
              powered, font=tag_font, fill="#888899")

    # ── Output ───────────────────────────────────────────
    img_io = BytesIO()
    canvas.save(img_io, "PNG")
    img_io.seek(0)
    return img_io
