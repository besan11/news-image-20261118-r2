#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news front page (1024x1024 PNG).

Written from scratch for the make.fun news-image-20261118 bounty, round 2.
Every fact on the page comes from the verified story list in the round-2
spec; every picture is drawn with plain PIL shapes (no external images).
The render is fully deterministic: fixed fonts, fixed data, no randomness,
no clock, no timestamps in the PNG.
"""

import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 16  # outer margin

# ---- palette: warm newsprint ----
PAPER = (247, 241, 227)
INK = (26, 26, 26)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
SEA = (110, 151, 184)
SEA_DARK = (74, 116, 150)
LAND = (216, 199, 160)
LAND_EDGE = (138, 123, 90)
GOLD = (201, 162, 39)
GREEN = (46, 125, 50)
GREY = (90, 86, 76)
LIGHT_LINE = (196, 186, 164)
PANEL = (252, 248, 238)
TAG_BG = (232, 222, 200)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_TITLE = font("DejaVuSans-Bold.ttf", 38)
F_DATE = font("DejaVuSans-Bold.ttf", 23)
F_COUNT_BIG = font("DejaVuSans-Bold.ttf", 27)
F_COUNT_SMALL = font("DejaVuSans-Bold.ttf", 13)
F_KICKER = font("DejaVuSans-Bold.ttf", 11)
F_LEAD_HEAD = font("DejaVuSans-Bold.ttf", 29)
F_LEAD_BODY = font("DejaVuSans.ttf", 13)
F_PANEL_HEAD = font("DejaVuSans-Bold.ttf", 15)
F_PANEL_BODY = font("DejaVuSans.ttf", 11)
F_MAP_TITLE = font("DejaVuSans-Bold.ttf", 12)
F_MAP_LABEL = font("DejaVuSans-Bold.ttf", 9)
F_MAP_NUM = font("DejaVuSans-Bold.ttf", 10)
F_STRIP = font("DejaVuSans.ttf", 12)
F_TAG = font("DejaVuSans-Bold.ttf", 8)
F_TILE_HEAD = font("DejaVuSans-Bold.ttf", 11)
F_TILE_BODY = font("DejaVuSans.ttf", 9)
F_BRIEF_HEAD = font("DejaVuSans-Bold.ttf", 11)
F_BRIEF = font("DejaVuSans.ttf", 10)
F_FOOT = font("DejaVuSans.ttf", 11)
F_SCENE = font("DejaVuSans-Bold.ttf", 10)
F_SCENE_SMALL = font("DejaVuSans.ttf", 9)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---- content: the 36 verified stories of Wednesday 18 November 2026 ----
LEAD = {
    "kicker": "LEAD  ·  1",
    "head": "GULF STRIKES",
    "body": (
        "US fighter jets struck a Revolutionary Guard missile site on "
        "Qeshm Island. Iran fired drones at Bahrain and Kuwait \u2014 a US "
        "radar site in Bahrain was hit for a third time in under a week "
        "\u2014 and an Iranian unit shot down a US MQ-9 drone near the "
        "Strait of Hormuz."
    ),
}

SECOND_ROW = [
    {
        "num": "2",
        "head": "KERCH BRIDGE HIT AGAIN",
        "body": (
            "Ukraine hit the bridge to Crimea for a second day; part of "
            "its road span fell and one arch collapsed."
        ),
        "icon": "bridge",
    },
    {
        "num": "3",
        "head": "XI AND PUTIN OPEN APEC",
        "body": (
            "Xi and Putin opened the APEC summit in Shenzhen as Trump landed "
            "from Manila; the three meet Thursday."
        ),
        "icon": "summit",
    },
    {
        "num": "4",
        "head": "ALASKA FLIPS BLUE",
        "body": (
            "Mary Peltola beat Dan Sullivan; Democrats reach 56\u201344, their "
            "9th flip \u2014 the largest majority since 2009."
        ),
        "icon": "alaska",
    },
    {
        "num": "5",
        "head": "NVIDIA: $115.8B QUARTER",
        "body": (
            "Q3 revenue $115.8B (+103%); net income $65.3B. First results "
            "since Huang resigned; interim CEO Kress."
        ),
        "icon": "chip",
    },
]

# (number, section, headline, one factual line)
GRID = [
    (9, "SCIENCE", "CYCLONE XAVIER, CAT 5",
     "Hits the Northern Cook Islands with gusts of 315 km/h."),
    (10, "POLITICS", "WORLD COURT TO RULE THURSDAY",
     "ICJ decides the Myanmar genocide case over the Rohingya."),
    (11, "CONFLICT", "RUSSIAN PLANE CRASHES",
     "Military plane down in Siberia, in Kemerovo \u2014 19 dead."),
    (12, "SCIENCE", "TWO EARTHQUAKES",
     "Magnitude 6.0 in Papua New Guinea; 5.3 in Romania."),
    (13, "POLITICS", "146,000 MARCH IN FRANCE",
     "Unions strike nationwide over the cost of living."),
    (14, "POLITICS", "TRUMP IN MANILA",
     "Meets the Philippines and Quad partners; preliminary trade deal with Thailand."),
    (15, "CONFLICT", "GAZA: COLD KILLS IN TENTS",
     "Displaced families freeze as the Board of Peace warns the ceasefire may collapse."),
    (16, "ECONOMY", "US TECH OUTAGES",
     "Outages hit banks, flights and the NSA \u2014 at least 8 major outages in a week."),
    (17, "POLITICS", "NEW KNESSET PRESIDENT",
     "Matan Kahana elected 66\u201352 over Ofir Katz."),
    (18, "POLITICS", "BRITAIN AND AUSTRALIA ACT",
     "UK blacklists builders in Judea and Samaria; Australia lists Weiss, Amana, Nachala."),
    (19, "CONFLICT", "MOSSAD TIP FOILS PLOT",
     "Greece and North Macedonia break up an Iranian-run murder plot in Skopje."),
    (20, "POLITICS", "TURKEY SEIZES SOZCU TV",
     "Government takes control of the opposition broadcaster."),
    (21, "SCIENCE", "WAYMO OFF THE FREEWAYS",
     "Driverless taxi rides halted on all US freeways after a California ban."),
    (22, "ECONOMY", "MARKETS SLIDE",
     "S&P 500 \u22121.03%, Nasdaq \u22120.74%, FTSE \u22121.76%, DAX \u22122.08%, Brent $92.47."),
    (23, "SCIENCE", "M1.1 SOLAR FLARE",
     "An M1.1-class flare recorded on the Sun."),
    (24, "POLITICS", "EU RETURN HUBS",
     "Five EU states plan migrant return hubs in Rwanda."),
    (25, "CONFLICT", "27 YEARS FOR TRUMP PLOT",
     "Pakistani man jailed in New York over an Iran-linked plot against Trump."),
    (26, "CONFLICT", "SPY SUSPECT MOVED",
     "US soldier held in the UK over Russia spy suspicion moved to US custody."),
    (27, "CONFLICT", "HOUTHIS PRESS ON ADEN",
     "Houthi forces advance toward Aden, Yemen."),
    (28, "CONFLICT", "US CRITICISES KYIV STRIKES",
     "Washington faults Ukraine\u2019s deep strikes; Germany pushes back."),
    (29, "POLITICS", "SERBIA\u2019S NEW PARLIAMENT",
     "Parliament opens with a student-list majority."),
    (30, "CONFLICT", "FEARS OF WIDER WAR",
     "Clashes near the Eritrean border raise fears of a wider war in Tigray."),
    (31, "ECONOMY", "SOUTH KOREA LIFTS FORECAST",
     "Seoul raises its 2027 growth forecast to 3.9%."),
    (32, "ECONOMY", "FRANCE\u2013MALAYSIA DEAL",
     "Strategic partnership agreed, with a rare-earths deal."),
    (33, "ECONOMY", "BRAZILIAN REAL FALLS",
     "The real drops as Lula\u2019s fiscal plan disappoints investors."),
    (34, "ECONOMY", "ANTHROPIC TO LIST",
     "Anthropic set to list on Nasdaq on Thursday 19 November."),
    (35, "SCIENCE", "FIJI DECLARES DISASTER",
     "National disaster declared over the El Ni\u00f1o drought."),
    (36, "CULTURE", "FELA KUTI MAKES HISTORY",
     "First African inducted into the Rock and Roll Hall of Fame."),
]

IN_BRIEF = [
    "Zverev into the ATP Finals knockouts in Turin",
    "Northern Ireland up to the Nations League top tier",
    "Tiger Woods to return to competition in December",
    "Cambridge Dictionary: \u201chuman\u201d is word of the year",
    "Robert Pattinson named as the new James Bond",
    "Earthshot Prize winners celebrated in Mumbai",
    "Pope Leo reveals cancer surgery after a South America tour",
    "An isolated Awa group emerges in the Brazilian Amazon",
    "Pakistan rooftop solar lifts its solar share to 28%",
    "The US tightens chip-access rules for China",
]

MARKETS = (
    "MARKETS \u2014 S&P 500 \u22121.03%  \u00b7  Nasdaq \u22120.74%  \u00b7  "
    "FTSE 100 \u22121.76%  \u00b7  DAX \u22122.08%  \u00b7  Brent $92.47  "
    "\u00b7  Gold \u22122.05%  \u00b7  VIX 25.46 (+11%)"
)

FOOTER = (
    "One day\u2019s news: Wednesday 18 November 2026 \u2014 36 stories, six "
    "continents, as reported that day."
)

SECTION_COLORS = {
    "CONFLICT": RED,
    "POLITICS": BLUE,
    "HEALTH": (122, 60, 120),
    "ECONOMY": (120, 90, 20),
    "SCIENCE": GREEN,
    "CULTURE": (160, 82, 45),
}

# ---- world map: simplified continent outlines, encoded by hand ----
# Each polygon is a list of (longitude, latitude) points, coarse on purpose.
CONTINENTS = [
    # North America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
     (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
     (-79, 9), (-80, 13), (-84, 16), (-87, 21), (-90, 21), (-91, 19),
     (-95, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26),
     (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44),
     (-60, 47), (-55, 47), (-60, 52), (-64, 58), (-68, 58), (-72, 62),
     (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70),
     (-140, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-25, 70),
     (-20, 74), (-25, 76), (-35, 76), (-50, 74), (-58, 70)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35), (-52, -32),
     (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
     (-44, -2), (-50, 0), (-54, 2), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-76, 10)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 4), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5),
     (13, -10), (12, -17), (15, -27), (18, -32), (20, -35), (26, -34),
     (32, -29), (35, -24), (36, -18), (40, -15), (40, -10), (42, -4),
     (46, -1), (51, 2), (51, 11), (48, 11), (44, 11), (40, 15), (38, 18),
     (37, 22), (35, 28), (32, 31), (25, 32), (19, 33), (11, 34), (10, 37),
     (4, 37), (-1, 35)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (0, 51),
     (3, 53), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
     (12, 65), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 68),
     (55, 68), (60, 69), (68, 73), (75, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (158, 69),
     (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 60),
     (158, 58), (156, 52), (150, 59), (142, 55), (140, 50), (138, 46),
     (135, 43), (132, 43), (128, 38), (127, 35), (126, 38), (122, 39),
     (120, 35), (122, 31), (120, 28), (118, 25), (112, 22), (108, 18),
     (105, 10), (103, 8), (100, 7), (98, 10), (97, 16), (94, 17), (92, 21),
     (89, 22), (86, 20), (83, 19), (80, 15), (77, 8), (75, 10), (73, 16),
     (70, 20), (66, 25), (62, 25), (58, 25), (56, 27), (54, 26), (52, 25),
     (50, 26), (48, 29), (48, 30), (44, 29), (42, 27), (40, 25), (38, 22),
     (36, 21), (34, 28), (33, 31), (36, 36), (30, 36), (27, 37), (26, 38),
     (23, 36), (22, 37), (19, 40), (16, 38), (12, 44), (10, 44), (8, 44),
     (3, 43), (0, 40), (-2, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (142, 44), (144, 44), (143, 42), (141, 39), (140, 36),
     (137, 34), (135, 33), (132, 31)],
    # Indonesia / South-East Asian islands (coarse)
    [(95, 5), (98, 3), (100, 0), (103, -2), (106, -6), (110, -7), (114, -8),
     (118, -9), (120, -10), (122, -9), (125, -8), (128, -4), (131, -1),
     (134, -3), (137, -2), (140, -4), (141, -6), (138, -8), (135, -8),
     (132, -6), (130, -3), (128, 0), (125, 1), (122, 0), (120, 2), (117, 0),
     (114, 0), (111, 1), (108, 3), (105, 5), (102, 5)],
    # Philippines
    [(120, 18), (122, 18), (122, 14), (121, 13), (124, 11), (126, 8),
     (122, 7), (120, 10)],
    # Australia
    [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (172, -43), (168, -46)],
]

# Numbered markers for the 8 lead stories: (number, lon, lat, short label)
MAP_MARKERS = [
    ("1", 56, 27, "GULF"),
    ("2", 36.5, 45.3, "KERCH"),
    ("3", 114, 22.5, "SHENZHEN"),
    ("4", -152, 64, "ALASKA"),
    ("5", -122, 37, "NVIDIA"),
    ("6", -98, 39, "MEASLES"),
    ("7", 23, -2, "EBOLA"),
]
MAP_REGION_LABELS = [
    ("NORTH AMERICA", -110, 60),
    ("SOUTH AMERICA", -60, -16),
    ("EUROPE", 8, 55),
    ("AFRICA", 10, 14),
    ("ASIA", 88, 52),
    ("OCEANIA", 138, -30),
]


def project(lon, lat, box):
    """Equirectangular projection into box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (78.0 - lat) / 136.0 * (y1 - y0)
    return (x, y)


def draw_burst(draw, cx, cy, r, fill):
    """Simple explosion starburst of triangles."""
    import math
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_jet(draw, cx, cy, s, fill, flip=False):
    """Simple fighter-jet silhouette (triangle body + swept wings)."""
    d = -1 if flip else 1
    body = [(cx + 2.2 * s * d, cy), (cx - 1.2 * s * d, cy - 0.35 * s),
            (cx - 0.9 * s * d, cy), (cx - 1.2 * s * d, cy + 0.35 * s)]
    wing = [(cx + 0.4 * s * d, cy), (cx - 0.7 * s * d, cy - 1.0 * s),
            (cx - 0.4 * s * d, cy), (cx - 0.7 * s * d, cy + 1.0 * s)]
    draw.polygon(body, fill=fill)
    draw.polygon(wing, fill=fill)


def draw_icon(draw, kind, x0, y0, x1, y1):
    """Small drawn illustration at the top of a second-row panel."""
    if kind == "bridge":
        wy = y1 - 14
        draw.rectangle([x0, wy, x1, y1], fill=SEA)
        draw.line([x0, wy, x1, wy], fill=SEA_DARK, width=1)
        # deck: two spans with a gap in the middle (the fallen span)
        mid = (x0 + x1) // 2
        draw.line([x0 + 4, y0 + 16, mid - 16, y0 + 16], fill=INK, width=4)
        draw.line([mid + 16, y0 + 16, x1 - 4, y0 + 16], fill=INK, width=4)
        # arch under the right span
        draw.arc([mid + 20, y0 + 4, x1 - 8, y0 + 30], 180, 360, fill=INK, width=2)
        # fallen span, tilted, dropping into the water
        draw.line([mid - 14, y0 + 18, mid + 2, y0 + 34], fill=RED, width=4)
        draw_burst(draw, mid - 2, y0 + 22, 7, (230, 120, 40))
        draw.line([x0 + 10, y0 + 16, x0 + 10, wy], fill=INK, width=2)
        draw.line([x1 - 10, y0 + 16, x1 - 10, wy], fill=INK, width=2)
    elif kind == "summit":
        base = y1 - 6
        # skyline
        heights = [26, 40, 32, 48, 36]
        bw = (x1 - x0) // 6
        for i, hh in enumerate(heights):
            bx = x0 + 6 + i * bw
            draw.rectangle([bx, base - hh, bx + bw - 6, base], fill=BLUE)
            draw.rectangle([bx + 3, base - hh - 5, bx + bw - 9, base - hh],
                           fill=BLUE)
        # three flags on poles at the right
        flags = [(176, 42, 30), (31, 78, 121), (240, 240, 240)]
        fx = x1 - 58
        for i, col in enumerate(flags):
            px = fx + i * 19
            draw.line([px, y0 + 6, px, base], fill=INK, width=2)
            draw.rectangle([px, y0 + 6, px + 15, y0 + 18], fill=col,
                           outline=INK, width=1)
        draw.text((x0 + 4, y0 + 2), "APEC", font=F_SCENE_SMALL, fill=INK)
    elif kind == "alaska":
        # rough Alaska outline + star
        pts = [(0.10, 0.55), (0.22, 0.30), (0.42, 0.22), (0.62, 0.28),
               (0.80, 0.18), (0.92, 0.30), (0.86, 0.52), (0.70, 0.62),
               (0.55, 0.78), (0.35, 0.85), (0.18, 0.78)]
        wbox, hbox = x1 - x0, y1 - y0
        poly = [(x0 + px * wbox, y0 + py * hbox) for px, py in pts]
        draw.polygon(poly, fill=(196, 214, 232), outline=BLUE)
        sx, sy = x0 + 0.52 * wbox, y0 + 0.48 * hbox
        draw_burst(draw, sx, sy, 9, RED)
        draw.text((x0 + 4, y0 + 2), "56\u201344", font=F_SCENE, fill=RED)
    elif kind == "chip":
        cx, cy = (x0 + x1) // 2 - 26, (y0 + y1) // 2
        s = 30
        draw.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                       fill=(34, 34, 34))
        draw.rectangle([cx - s // 4, cy - s // 4, cx + s // 4, cy + s // 4],
                       outline=GOLD, width=2)
        for k in range(-1, 2):
            draw.line([cx + k * 12, cy - s // 2 - 7, cx + k * 12, cy - s // 2],
                      fill=GOLD, width=2)
            draw.line([cx + k * 12, cy + s // 2, cx + k * 12, cy + s // 2 + 7],
                      fill=GOLD, width=2)
            draw.line([cx - s // 2 - 7, cy + k * 12, cx - s // 2, cy + k * 12],
                      fill=GOLD, width=2)
            draw.line([cx + s // 2, cy + k * 12, cx + s // 2 + 7, cy + k * 12],
                      fill=GOLD, width=2)
        # rising chart arrow
        ax0, ay0 = cx + s // 2 + 12, cy + 16
        draw.line([(ax0, ay0), (ax0 + 16, ay0 - 12), (ax0 + 30, ay0 - 16),
                   (ax0 + 46, ay0 - 30)], fill=GREEN, width=3)
        draw.polygon([(ax0 + 46, ay0 - 30), (ax0 + 38, ay0 - 28),
                      (ax0 + 44, ay0 - 20)], fill=GREEN)
        draw.text((x0 + 4, y0 + 2), "+103%", font=F_SCENE, fill=GREEN)

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ================= masthead =================
    d.text((MX, 6), "THE WORLD TODAY", font=F_TITLE, fill=INK)
    d.text((MX, 52), "WEDNESDAY 18 NOVEMBER 2026", font=F_DATE, fill=RED)
    right = "36 STORIES"
    rw = d.textlength(right, font=F_COUNT_BIG)
    d.text((W - MX - rw, 8), right, font=F_COUNT_BIG, fill=BLUE)
    right2 = "SIX CONTINENTS"
    rw2 = d.textlength(right2, font=F_COUNT_SMALL)
    d.text((W - MX - rw2, 44), right2, font=F_COUNT_SMALL, fill=INK)
    d.line([MX, 82, W - MX, 82], fill=INK, width=2)
    d.line([MX, 86, W - MX, 86], fill=INK, width=1)

    # ================= lead panel: Gulf strikes =================
    ly0, ly1 = 90, 280
    d.rectangle([MX, ly0, W - MX, ly1], outline=INK, width=2, fill=PANEL)
    # drawn scene, left half
    sx0, sy0, sx1, sy1 = MX + 2, ly0 + 2, 560, ly1 - 2
    d.rectangle([sx0, sy0, sx1, sy1], fill=(233, 226, 205))
    sea_y = sy0 + 100
    d.rectangle([sx0, sea_y, sx1, sy1], fill=SEA)
    for wx in range(sx0 + 20, sx1 - 10, 46):
        d.arc([wx, sea_y + 12, wx + 26, sea_y + 20], 180, 360,
              fill=(255, 255, 255), width=2)
    # Qeshm Island
    island = [(sx0 + 150, sea_y + 8), (sx0 + 210, sea_y - 6),
              (sx0 + 300, sea_y + 2), (sx0 + 330, sea_y + 22),
              (sx0 + 280, sea_y + 34), (sx0 + 190, sea_y + 30)]
    d.polygon(island, fill=LAND, outline=LAND_EDGE)
    d.text((sx0 + 196, sea_y - 26), "QESHM ISLAND", font=F_SCENE, fill=INK)
    # missile site + strike burst
    d.ellipse([sx0 + 238, sea_y + 6, sx0 + 250, sea_y + 18], fill=RED)
    draw_burst(d, sx0 + 244, sea_y + 12, 13, (230, 120, 40))
    d.text((sx0 + 258, sea_y + 2), "MISSILE SITE HIT", font=F_SCENE_SMALL,
           fill=RED)
    # jets
    draw_jet(d, sx0 + 90, sy0 + 42, 11, INK)
    draw_jet(d, sx0 + 150, sy0 + 66, 9, INK)
    d.line([sx0 + 62, sy0 + 42, sx0 + 30, sy0 + 42], fill=GREY, width=2)
    d.line([sx0 + 128, sy0 + 66, sx0 + 102, sy0 + 66], fill=GREY, width=2)
    d.text((sx0 + 10, sy0 + 8), "US FIGHTER JETS", font=F_SCENE, fill=INK)
    # drones over the strait
    for dx, dy in [(sx0 + 380, sea_y + 30), (sx0 + 420, sea_y + 46),
                   (sx0 + 350, sea_y + 52)]:
        d.ellipse([dx - 5, dy - 3, dx + 5, dy + 3], fill=INK)
        d.line([dx - 8, dy - 6, dx + 8, dy - 6], fill=INK, width=1)
    d.text((sx0 + 336, sea_y + 64), "DRONES AT BAHRAIN & KUWAIT",
           font=F_SCENE_SMALL, fill=INK)
    # downed MQ-9
    draw_jet(d, sx0 + 470, sea_y + 22, 8, RED, flip=True)
    d.line([sx0 + 452, sea_y + 36, sx0 + 436, sea_y + 54], fill=RED, width=2)
    d.text((sx0 + 448, sea_y + 42), "MQ-9 DOWN", font=F_SCENE_SMALL, fill=RED)
    d.text((sx0 + 10, sy1 - 20), "STRAIT OF HORMUZ", font=F_SCENE, fill=(255, 255, 255))
    d.line([sx0 + 2, sea_y, sx1 - 2, sea_y], fill=SEA_DARK, width=1)

    # lead text, right half
    tx = 576
    d.text((tx, ly0 + 10), LEAD["kicker"], font=F_KICKER, fill=RED)
    d.text((tx, ly0 + 28), LEAD["head"], font=F_LEAD_HEAD, fill=INK)
    d.line([tx, ly0 + 66, W - MX - 12, ly0 + 66], fill=RED, width=2)
    draw_wrapped(d, tx, ly0 + 76, LEAD["body"], F_LEAD_BODY, W - MX - 12 - tx,
                 INK, 18)

    # ================= second row: 4 medium panels =================
    ry0, ry1 = 286, 428
    pw = (W - 2 * MX - 3 * 8) // 4
    for i, item in enumerate(SECOND_ROW):
        x0 = MX + i * (pw + 8)
        x1 = x0 + pw
        d.rectangle([x0, ry0, x1, ry1], outline=INK, width=1, fill=PANEL)
        d.rectangle([x0, ry0, x1, ry0 + 56], fill=(233, 226, 205))
        draw_icon(d, item["icon"], x0 + 6, ry0 + 2, x1 - 6, ry0 + 54)
        d.text((x0 + 8, ry0 + 62), item["num"] + "  \u00b7", font=F_KICKER,
               fill=RED)
        draw_wrapped(d, x0 + 8, ry0 + 78, item["head"], F_PANEL_HEAD,
                     pw - 16, INK, 18, max_lines=1)
        draw_wrapped(d, x0 + 8, ry0 + 98, item["body"], F_PANEL_BODY,
                     pw - 16, INK, 14, max_lines=3)

    # ================= world map =================
    my0, my1 = 434, 580
    d.rectangle([MX, my0, W - MX, my1], outline=INK, width=1, fill=PANEL)
    d.text((MX + 8, my0 + 5), "THE WORLD ON WEDNESDAY \u2014 8 LEAD STORIES",
           font=F_MAP_TITLE, fill=INK)
    d.line([MX + 8, my0 + 22, W - MX - 8, my0 + 22], fill=LIGHT_LINE, width=1)
    map_box = (MX + 8, my0 + 26, W - MX - 8, my1 - 6)
    # faint graticule
    for lon in range(-150, 181, 30):
        x, _ = project(lon, 78, map_box)
        d.line([x, map_box[1], x, map_box[3]], fill=(228, 221, 203), width=1)
    for lat in range(-60, 79, 30):
        _, y = project(-180, lat, map_box)
        d.line([map_box[0], y, map_box[2], y], fill=(228, 221, 203), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [project(lon, lat, map_box) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # region labels
    for label, lon, lat in MAP_REGION_LABELS:
        x, y = project(lon, lat, map_box)
        d.text((x - d.textlength(label, font=F_MAP_LABEL) / 2, y),
               label, font=F_MAP_LABEL, fill=GREY)
    # numbered markers
    for num, lon, lat, label in MAP_MARKERS:
        x, y = project(lon, lat, map_box)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED, outline=(255, 255, 255),
                  width=1)
        tw = d.textlength(num, font=F_MAP_NUM)
        d.text((x - tw / 2, y - 7), num, font=F_MAP_NUM, fill=(255, 255, 255))
        lx = x + 11
        if lx + d.textlength(label, font=F_MAP_LABEL) > map_box[2]:
            lx = x - 11 - d.textlength(label, font=F_MAP_LABEL)
        d.text((lx, y - 6), label, font=F_MAP_LABEL, fill=RED)
    # story 8 lives in space: corner box
    bx0, by0 = W - MX - 218, my0 + 28
    d.rectangle([bx0, by0, W - MX - 10, by0 + 30], fill=INK)
    d.text((bx0 + 8, by0 + 8), "8  \u2605  VOYAGER 1 \u2014 ONE LIGHT-DAY OUT",
           font=F_MAP_LABEL, fill=(255, 255, 255))

    # ================= markets strip =================
    d.rectangle([MX, 586, W - MX, 608], fill=TAG_BG)
    d.text((MX + 8, 591), MARKETS, font=F_STRIP, fill=INK)

    # ================= grid: 28 more stories =================
    gy0 = 614
    d.text((MX, gy0), "THE REST OF THE DAY \u2014 28 MORE STORIES",
           font=F_MAP_TITLE, fill=INK)
    d.line([MX, gy0 + 18, W - MX, gy0 + 18], fill=INK, width=1)
    cols, rows = 4, 7
    gw = (W - 2 * MX - (cols - 1) * 8) // cols
    gh = 44
    gy = gy0 + 24
    for idx, (num, section, head, body) in enumerate(GRID):
        r, c = divmod(idx, cols)
        x0 = MX + c * (gw + 8)
        y0 = gy + r * gh
        x1 = x0 + gw
        if r > 0:
            d.line([MX, y0 - 2, W - MX, y0 - 2], fill=LIGHT_LINE, width=1)
        col = SECTION_COLORS[section]
        d.text((x0, y0), str(num) + "  " + section, font=F_TAG, fill=col)
        d.text((x0, y0 + 11), head, font=F_TILE_HEAD, fill=INK)
        draw_wrapped(d, x0, y0 + 22, body, F_TILE_BODY, gw - 2, INK, 10,
                     max_lines=2)

    # ================= in brief =================
    by0 = 950
    d.line([MX, by0, W - MX, by0], fill=INK, width=1)
    d.text((MX, by0 + 6), "IN BRIEF", font=F_BRIEF_HEAD, fill=RED)
    brief_text = "  \u00b7  ".join(IN_BRIEF)
    lines = wrap(d, brief_text, F_BRIEF, W - 2 * MX - 74)
    yy = by0 + 6
    for ln in lines[:3]:
        d.text((MX + 74, yy), ln, font=F_BRIEF, fill=INK)
        yy += 13

    # ================= footer =================
    fy = 996
    d.line([MX, fy, W - MX, fy], fill=INK, width=1)
    fw = d.textlength(FOOTER, font=F_FOOT)
    d.text(((W - fw) / 2, fy + 8), FOOTER, font=F_FOOT, fill=GREY)

    return img


def main():
    img = render()
    img.save("entry.png", format="PNG", optimize=True)
    data = open("entry.png", "rb").read()
    print("entry.png bytes:", len(data))
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
