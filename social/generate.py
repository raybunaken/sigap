"""Skillsy social media kit generator. Run: python social/generate.py"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
LIME = (212, 255, 50)
BG_TOP = (26, 42, 34)
BG_BOT = (13, 18, 16)
F_BLACK = r"C:\Windows\Fonts\seguibl.ttf"
F_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def bg(w, h, rounded=None, grid=True):
    """Dark gradient + faint grid + soft lime glows."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    if grid:
        gd = ImageDraw.Draw(img, "RGBA")
        step = max(48, w // 24)
        for x in range(0, w, step):
            gd.line([(x, 0), (x, h)], fill=(255, 255, 255, 6))
        for y in range(0, h, step):
            gd.line([(0, y), (w, y)], fill=(255, 255, 255, 6))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-w * 0.2, -h * 0.25, w * 0.45, h * 0.45], fill=(212, 255, 50, 16))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(60)))
    if rounded:
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=rounded, fill=255)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask)
        return out
    return img

def draw_mark(layer, cx, cy, size, glow=True):
    """The 'S.' mark centered at (cx, cy) with cap height ~size."""
    d = ImageDraw.Draw(layer)
    f = font(F_BLACK, size)
    bb = d.textbbox((0, 0), "S", font=f)
    sw, sh = bb[2] - bb[0], bb[3] - bb[1]
    x = cx - sw // 2 - size // 14
    y = cy - sh // 2 - bb[1]
    if glow:
        glow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow_layer).text((x, y), "S", font=f, fill=LIME + (200,))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(size // 5))
        layer.alpha_composite(glow_layer)
        layer.alpha_composite(glow_layer)
    d.text((x, y), "S", font=f, fill=LIME + (255,))
    dot_r = int(size * 0.14)
    dx = x + bb[0] + sw + int(size * 0.16)
    dy = y + bb[1] + sh - dot_r
    d.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=LIME + (255,))
    return sw + int(size * 0.3)

def text_center(layer, cx, y, text, f, fill=(250, 250, 250, 255), spacing=0):
    d = ImageDraw.Draw(layer)
    bb = d.textbbox((0, 0), text, font=f)
    x = cx - (bb[2] - bb[0]) // 2 - bb[0]
    d.text((x, y), text, font=f, fill=fill)
    return bb[3] - bb[1]

def pill(layer, cx, cy, text, f, pad_x=22, pad_y=10):
    d = ImageDraw.Draw(layer)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0, y0 = cx - tw // 2 - pad_x, cy - th // 2 - pad_y
    d.rounded_rectangle([x0, y0, x0 + tw + pad_x * 2, y0 + th + pad_y * 2],
                        radius=(th + pad_y * 2) // 2,
                        fill=(212, 255, 50, 26), outline=(212, 255, 50, 90), width=2)
    d.text((x0 + pad_x - bb[0], y0 + pad_y - bb[1]), text, font=f, fill=LIME + (255,))

# ── 1. PROFILE (avatar, circular-safe) ──────────────────────────────────
def make_profile(px=1024):
    img = bg(px, px, rounded=int(px * 0.22), grid=False)
    draw_mark(img, px // 2, px // 2, int(px * 0.58))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3, 3, px - 4, px - 4], radius=int(px * 0.22) - 3,
                        outline=(255, 255, 255, 26), width=max(2, px // 340))
    if px != 1024:
        img = img.resize((px, px), Image.LANCZOS)
    return img

make_profile(1024).save(os.path.join(OUT, "profile-1024.png"))
make_profile(400).save(os.path.join(OUT, "profile-400.png"))

# ── 2. LINKEDIN BANNER 1584x396 ─────────────────────────────────────────
def make_banner():
    w, h = 1584, 396
    img = bg(w, h)
    d = ImageDraw.Draw(img)
    # mark on the left
    mf = font(F_BLACK, 200)
    bb = d.textbbox((0, 0), "S", font=mf)
    sw = bb[2] - bb[0]
    mx, my = 110, h // 2 - 20
    mark = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    md.text((mx, my - (bb[3] - bb[1]) // 2 - bb[1]), "S", font=mf, fill=LIME + (255,))
    dot_r = 26
    dx = mx + sw + 30
    md.ellipse([dx - dot_r, my + 60 - dot_r, dx + dot_r, my + 60 + dot_r], fill=LIME + (255,))
    glow = mark.filter(ImageFilter.GaussianBlur(28))
    img.alpha_composite(glow)
    img.alpha_composite(mark)
    # wordmark + tagline
    d.text((mx + sw + 90, h // 2 - 118), "Skillsy", font=font(F_BLACK, 78), fill=(255, 255, 255))
    d.text((mx + sw + 92, h // 2 - 16), "AI that shows its work.", font=font(F_BOLD, 40), fill=(212, 255, 50))
    d.text((mx + sw + 92, h // 2 + 52), "Match score. Skill gap. ATS keywords. Cover letters.", font=font(F_BOLD, 24), fill=(161, 161, 170))
    d.text((w - 260, h - 56), "skillsy.my.id", font=font(F_BOLD, 26), fill=(120, 120, 128))
    return img

make_banner().save(os.path.join(OUT, "banner-linkedin-1584x396.png"))

# ── 3. OG IMAGE 1200x630 (web share) ────────────────────────────────────
def make_og():
    w, h = 1200, 630
    img = bg(w, h)
    cx = w // 2
    draw_mark(img, cx, 200, 190)
    text_center(img, cx, 340, "Know your odds, before you apply.", font(F_BLACK, 58))
    text_center(img, cx, 430, "Same CV. Same job. Same score.", font(F_BOLD, 30), fill=(212, 255, 50, 255))
    text_center(img, cx, h - 90, "skillsy.my.id", font(F_BOLD, 24), fill=(120, 120, 128, 255))
    return img

make_og().save(os.path.join(OUT, "og-1200x630.png"))

# ── 4. INSTAGRAM POST 1080x1080 ─────────────────────────────────────────
def make_ig_post():
    w, h = 1080, 1080
    img = bg(w, h)
    cx = w // 2
    draw_mark(img, cx, 330, 330)
    text_center(img, cx, 560, "AI that shows", font(F_BLACK, 92))
    text_center(img, cx, 672, "its work.", font(F_BLACK, 92), fill=LIME + (255,))
    text_center(img, cx, 830, "Same CV. Same job. Same score.", font(F_BOLD, 34), fill=(161, 161, 170, 255))
    pill(img, cx, 950, "skillsy.my.id", font(F_BOLD, 28))
    return img

make_ig_post().save(os.path.join(OUT, "post-instagram-1080x1080.png"))

# ── 5. INSTAGRAM STORY 1080x1920 ────────────────────────────────────────
def make_ig_story():
    w, h = 1080, 1920
    img = bg(w, h)
    cx = w // 2
    draw_mark(img, cx, 560, 420)
    text_center(img, cx, 950, "AI that shows", font(F_BLACK, 100))
    text_center(img, cx, 1072, "its work.", font(F_BLACK, 100), fill=LIME + (255,))
    text_center(img, cx, 1290, "Know your odds,", font(F_BOLD, 44), fill=(161, 161, 170, 255))
    text_center(img, cx, 1352, "before you apply.", font(F_BOLD, 44), fill=(161, 161, 170, 255))
    pill(img, cx, 1560, "skillsy.my.id", font(F_BOLD, 34))
    return img

make_ig_story().save(os.path.join(OUT, "story-instagram-1080x1920.png"))

print("Done:", sorted(os.listdir(OUT)))
