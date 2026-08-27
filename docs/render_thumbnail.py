"""
Renders docs/thumbnail.png — the Devpost project thumbnail for Dossier.
3:2 ratio per Devpost's spec. Same dark palette as Crucible's (the sibling
submission) so the two read as one author's work.
Regenerate with: python3 docs/render_thumbnail.py
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1500, 1000  # 3:2
BG = (10, 12, 16)
PANEL = (18, 21, 29)
LINE = (42, 49, 66)
TEXT = (241, 244, 249)
MUTED = (125, 138, 163)
GOLD = (251, 191, 36)
GREEN = (74, 222, 128)
CYAN = (103, 232, 249)
PURPLE = (167, 139, 250)
RED = (248, 113, 113)


def font(size, bold=False):
    path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        return ImageFont.truetype(path, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

for x in range(0, W, 60):
    d.line([x, 0, x, H], fill=(15, 18, 24), width=1)
for y in range(0, H, 60):
    d.line([0, y, W, y], fill=(15, 18, 24), width=1)

d.text((90, 110), "DOSSIER", font=font(72, True), fill=TEXT)
d.text((92, 200), "UK STUDENT VISA CASE PARTNER",
       font=font(15, True), fill=MUTED)

d.text((92, 260), "It reads the actual rulebook —",
       font=font(26), fill=(203, 213, 225))
d.text((92, 296), "not the internet's summary of it.",
       font=font(26), fill=(203, 213, 225))

chips = [("Vertex AI", CYAN), ("Cloud Run", GREEN), ("Firestore", GOLD), ("Cloud Scheduler", PURPLE)]
cx, cy = 92, 370
for label, color in chips:
    f = font(13, True)
    tw = d.textbbox((0, 0), label, font=f)[2]
    d.ellipse([cx, cy + 3, cx + 8, cy + 11], fill=color)
    d.text((cx + 16, cy), label, font=f, fill=(203, 213, 225))
    cx += tw + 46

panel_x, panel_y, panel_w, panel_h = 92, 460, 1316, 440
d.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
                     radius=14, fill=PANEL, outline=LINE, width=2)
d.text((panel_x + 32, panel_y + 26), "CITED, DETERMINISTIC ASSESSMENT",
       font=font(13, True), fill=(147, 197, 253))

# citation -> computed window, the core idea, drawn simply
ty = panel_y + 150
d.text((panel_x + 60, ty), "ST 12.6", font=font(22, True), fill=GOLD)
d.text((panel_x + 60, ty + 34), "28-day holding period", font=font(13), fill=MUTED)
d.text((panel_x + 300, ty), "FIN 7.1", font=font(22, True), fill=GOLD)
d.text((panel_x + 300, ty + 34), "31-day recency limit", font=font(13), fill=MUTED)

arrow_y = ty + 90
d.line([panel_x + 60, arrow_y, panel_x + panel_w - 420, arrow_y], fill=LINE, width=3)
ax = panel_x + panel_w - 420
d.polygon([(ax, arrow_y - 8), (ax + 14, arrow_y), (ax, arrow_y + 8)], fill=LINE)

d.text((panel_x + panel_w - 400, ty - 6), "APPLY WINDOW",
       font=font(13, True), fill=(147, 197, 253))
d.text((panel_x + panel_w - 400, ty + 24), "2 Sept — 3 Oct",
       font=font(30, True), fill=TEXT)
d.text((panel_x + panel_w - 400, ty + 64), "computed, not guessed",
       font=font(12), fill=MUTED)

# The finding
fy = panel_y + panel_h - 120
d.rounded_rectangle([panel_x + 32, fy, panel_x + panel_w - 32, panel_y + panel_h - 24],
                     radius=8, fill=(32, 20, 20), outline=(96, 48, 48), width=1)
d.text((panel_x + 52, fy + 14), "THE FINDING", font=font(11, True), fill=RED)
d.text((panel_x + 52, fy + 36),
       "2 of 6 public guidance pages we checked still quote pre-Nov-2025 figures",
       font=font(15, True), fill=(252, 165, 165))
d.text((panel_x + 52, fy + 60),
       "(£1,334 vs the current £1,529) — the internet's summary drifted; the rulebook didn't.",
       font=font(13), fill=MUTED)

img.save("docs/thumbnail.png", optimize=True)
print("Wrote docs/thumbnail.png", img.size)
