"""
Renders docs/architecture.png for Dossier. Same dark palette as Crucible's
diagram (the sibling submission) so the two read as one author's work.
Regenerate with: python3 docs/render_architecture.py
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1000
BG = (10, 12, 16)
PANEL = (18, 21, 29)
LINE = (42, 49, 66)
TEXT = (241, 244, 249)
MUTED = (125, 138, 163)
BLUE = (147, 197, 253)
GREEN = (74, 222, 128)
GOLD = (251, 191, 36)
PURPLE = (167, 139, 250)
RED = (248, 113, 113)


def font(size, bold=False):
    path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        return ImageFont.truetype(path, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.load_default()


def box(draw, x, y, w, h, fill, outline, kicker=None, title=None, sub=None,
        kicker_color=BLUE, title_size=15, center=False):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=fill, outline=outline, width=2)
    tx, ty = x + 18, y + 16
    if kicker:
        draw.text((tx, ty), kicker.upper(), font=font(10, True), fill=kicker_color)
        ty += 20
    if title:
        f = font(title_size, True)
        if center:
            tw = draw.textbbox((0, 0), title, font=f)[2]
            draw.text((x + w / 2 - tw / 2, ty), title, font=f, fill=TEXT)
        else:
            draw.text((tx, ty), title, font=f, fill=TEXT)
        ty += title_size + 8
    if sub:
        f = font(11)
        if center:
            tw = draw.textbbox((0, 0), sub, font=f)[2]
            draw.text((x + w / 2 - tw / 2, ty), sub, font=f, fill=MUTED)
        else:
            draw.text((tx, ty), sub, font=f, fill=MUTED)


def arrow(draw, x1, y1, x2, y2, color, width=2):
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    ah = 8
    p1 = (x2 - ah * math.cos(ang - 0.4), y2 - ah * math.sin(ang - 0.4))
    p2 = (x2 - ah * math.cos(ang + 0.4), y2 - ah * math.sin(ang + 0.4))
    draw.polygon([p1, (x2, y2), p2], fill=color)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.text((60, 34), "DOSSIER", font=font(30, True), fill=TEXT)
d.text((62, 76), "Case-preparation for the UK Student visa financial requirement",
       font=font(12), fill=MUTED)

cx = W - 60
d.text((cx - 340, 34), "GOOGLE CLOUD USED", font=font(10, True), fill=(91, 101, 121), anchor="ra")
chips = [("Vertex AI", BLUE), ("Cloud Run", GREEN), ("Firestore", GOLD), ("Cloud Scheduler", PURPLE)]
row_y = 60
cxx = cx - 340
for label, color in chips:
    f = font(11, True)
    tw = d.textbbox((0, 0), label, font=f)[2]
    d.ellipse([cxx, row_y + 3, cxx + 8, row_y + 11], fill=color)
    d.text((cxx + 16, row_y), label, font=f, fill=(203, 213, 225))
    cxx += tw + 40

# Rulebook source
box(d, 60, 130, 360, 90, PANEL, LINE, kicker="Source (real, third-party)",
    title="gov.uk Appendix Student", sub="+ Appendix Finance — the actual rules")
arrow(d, 240, 220, 240, 260, MUTED)

# Ingest -> Graph
box(d, 60, 260, 360, 90, PANEL, LINE, kicker="rulebook/",
    title="RequirementGraph", sub="every node cited: ST 12.6, FIN 7.1, ...", kicker_color=GOLD)
arrow(d, 240, 350, 240, 400, MUTED)

# Gap engine — the core claim
box(d, 60, 400, 360, 130, (16, 24, 20), (34, 74, 48),
    kicker="engine/ — PURE PYTHON, NO LLM", title="Gap Engine",
    sub="satisfied / blocked-until-DATE", kicker_color=GREEN)
d.text((80, 480), "28/31-day arithmetic + ST 12.1 exemption pruning",
       font=font(10), fill=MUTED)
d.text((80, 496), "Never imports agents/ — enforced by a test", font=font(10), fill=GREEN)

# Interviewer + Notebook
box(d, 480, 130, 360, 130, PANEL, LINE, kicker="agents/interviewer.py",
    title="Interviewer (Gemini)", sub="engine picks the topic, model picks the words")
box(d, 480, 290, 360, 150, PANEL, LINE, kicker="agents/notebook.py",
    title="Notebook", sub="facts · inferences · preferences", kicker_color=BLUE)
d.text((500, 370), "correcting an inference re-runs the engine", font=font(10), fill=MUTED)
d.text((500, 386), "correcting a preference changes the next question", font=font(10), fill=MUTED)
arrow(d, 420, 460, 480, 355, MUTED)
arrow(d, 480, 195, 420, 460, MUTED)

# Extractor
box(d, 480, 460, 360, 90, PANEL, LINE, kicker="agents/extractor.py (multimodal)",
    title="Evidence Extractor", sub="reads a photo of a bank statement / CAS letter")
arrow(d, 480, 505, 420, 490, MUTED)

# Nightly job
box(d, 900, 130, 320, 110, (24, 20, 32), (74, 48, 96), kicker="jobs/nightly.py",
    title="Nightly Caseworker", sub="Cloud Scheduler — recomputes as dates roll", kicker_color=PURPLE)
arrow(d, 1060, 240, 1060, 280, PURPLE)

# The Dossier artifact
box(d, 900, 280, 320, 220, PANEL, LINE, kicker="THE VISIBLE ARTIFACT",
    title="The Dossier", sub="cited assessment + apply-date window", title_size=17)
d.text((920, 400), "\"Your statement closes 2 Sept.", font=font(12), fill=(203, 213, 225))
d.text((920, 418), "You qualify from 2 Sept — evidence", font=font(12), fill=(203, 213, 225))
d.text((920, 436), "expires 3 Oct. Apply in that window.\"", font=font(12), fill=(203, 213, 225))
d.text((920, 468), "every number links its gov.uk paragraph", font=font(10, True), fill=GOLD)
arrow(d, 780, 340, 900, 340, MUTED)

# Guidance audit — the finding
box(d, 900, 540, 320, 160, (32, 20, 20), (96, 48, 48), kicker="THE FINDING",
    title="Guidance Audit", sub="checked 6 public pages against the graph", kicker_color=RED)
d.text((920, 640), "2 of 6 still quoted pre-Nov-2025", font=font(12), fill=(252, 165, 165))
d.text((920, 658), "maintenance figures (£1,334 vs £1,529)", font=font(12), fill=(252, 165, 165))
d.text((920, 678), "— the internet's summary drifted; the rulebook didn't", font=font(10), fill=MUTED)

# Live footer
d.rounded_rectangle([60, 900, 700, 968], radius=10, fill=PANEL, outline=LINE, width=2)
d.text((80, 916), "LIVE", font=font(10, True), fill=(103, 232, 249))
d.text((80, 934), "Cloud Run + Firestore, deployed and reachable now",
       font=font(11), fill=MUTED)

d.text((60, 985), "An LLM never decides whether a rule is met. That decision is plain code.",
       font=font(12, True), fill=(203, 213, 225))

img.save("docs/architecture.png", optimize=True)
print("Wrote docs/architecture.png", img.size)
