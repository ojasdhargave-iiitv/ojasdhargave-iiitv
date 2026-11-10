
#!/usr/bin/env python3
"""Generate SVG cards for the GitHub profile README. Stdlib only."""

import os
import sys
import json
import base64
import random
import textwrap
import datetime as dt
import urllib.request
from html import escape as esc

USER = os.environ.get("GITHUB_USER", "ojasdhargave-iiitv")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
DEMO = "--demo" in sys.argv
OUT = "assets"

# ───────────── PROFILE CONTENT ─────────────

PROFILE = dict(
    first="Ojas",
    last="Dhargave",
    eyebrow="FULL-STACK DEVELOPER · IIIT VADODARA",
    tagline="I build full-stack products from 0 to 1, from pixel-perfect UI/UX to robust backends.",
    link="github.com/ojasdhargave-iiitv",
)

# Updated profile highlight cards
TILES = [
    dict(
        label="ENGINEER",
        big="End-to-end",
        it="engineer",
        bg="#3355ff",
        fg="#ffffff",
        text="Building full-stack products, from intuitive interfaces to robust APIs and cloud deployment."
    ),
    dict(
        label="EXPLORE",
        big="Systems",
        it="& security",
        bg="#ee4035",
        fg="#ffffff",
        text="Exploring distributed systems, cybersecurity, artificial intelligence and computer vision."
    ),
    dict(
        label="LEARN",
        big="CSE",
        it="'28",
        bg="#ffc82c",
        fg="#1a1a1a",
        text="Computer Science at IIIT Vadodara, shipping from design to deployment."
    ),
]

PROJECTS = [
    dict(
        name="portionup",
        repo="portionup",
        color="#3355ff",
        lang="Python",
        desc="Real-time multi-object food detection and nutrition estimation. YOLO + OpenCV, 88% mAP."
    ),
    dict(
        name="saas-backend-ide",
        repo=None,
        color="#ee4035",
        lang="TypeScript",
        desc="Code editor, compiler pipeline and backend template engine. Cuts setup time by 65%."
    ),
    dict(
        name="self-driving-car",
        repo="Self_driving_Car",
        color="#ffc82c",
        lang="JavaScript",
        desc="A neural network written with zero libraries that navigates traffic on its own."
    ),
]

# ───────────── TECHNOLOGY ICONS ─────────────
# Each technology has a short logo-style mark and its brand colour.
# These are drawn directly into the SVG: no external image dependencies.

TECH_GROUPS = [
    ("LANGUAGES", [
        ("C++", "C++", "#00599C"),
        ("JavaScript", "JS", "#F7DF1E"),
        ("TypeScript", "TS", "#3178C6"),
        ("Python", "Py", "#3776AB"),
        ("Go", "Go", "#00ADD8"),
        ("HTML", "5", "#E34F26"),
        ("CSS", "3", "#1572B6"),
        ("SQL", "SQL", "#4479A1"),
    ]),
    ("FRONTEND", [
        ("React.js", "R", "#61DAFB"),
        ("Tailwind CSS", "TW", "#06B6D4"),
        ("Three.js", "3D", "#222222"),
        ("Figma", "F", "#F24E1E"),
        ("Blender", "B", "#E87D0D"),
    ]),
    ("BACKEND", [
        ("Node.js", "JS", "#339933"),
        ("Express.js", "Ex", "#303030"),
        ("FastAPI", "API", "#009688"),
        ("OpenCV", "CV", "#5C3EE8"),
    ]),
    ("DATABASES & CLOUD", [
        ("MongoDB", "M", "#47A248"),
        ("MySQL", "SQL", "#4479A1"),
        ("PostgreSQL", "PG", "#4169E1"),
        ("Redis", "R", "#DC382D"),
        ("Supabase", "S", "#3ECF8E"),
        ("Prisma", "P", "#2D3748"),
        ("Vercel", "▲", "#111111"),
        ("AWS", "aws", "#FF9900"),
    ]),
    ("TOOLS & DEVOPS", [
        ("Git", "Git", "#F05032"),
        ("GitHub", "GH", "#24292F"),
        ("Docker", "D", "#2496ED"),
        ("GitHub Actions", "A", "#2088FF"),
        ("VS Code", "VS", "#007ACC"),
        ("Postman", "P", "#FF6C37"),
        ("Linux", "L", "#FCC624"),
    ]),
]

# ───────────── SVG STYLING ─────────────

CSS = """
.serif{font-family:Georgia,'Times New Roman',serif}
.sans{font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'SFMono-Regular',Menlo,Consolas,'Courier New',monospace}
.cell{opacity:0;animation:pop .5s ease-out forwards}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
.bar{transform-origin:bottom;animation:grow .8s ease-out both}
@keyframes grow{from{transform:scaleY(0)}to{transform:none}}
.blink{animation:bl 1.4s steps(1) infinite}
@keyframes bl{50%{opacity:.2}}
@media (prefers-reduced-motion:reduce){
    *{animation:none!important}
    .cell{opacity:1!important}
}
"""

CARD = "#f4f3ee"
EDGE = "#e2e0d8"
INK = "#141414"
MUTE = "#6b6b66"
BLUE = "#3355ff"


def svg(w, h, body, extra_css=""):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<style>{CSS}{extra_css}</style>{body}</svg>'
    )


def card(w, h, rx=16):
    return (
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" '
        f'rx="{rx}" fill="{CARD}" stroke="{EDGE}"/>'
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name)


# ───────────── GITHUB DATA ─────────────

def http(url, data=None, accept=None):
    headers = {"User-Agent": "profile-cards"}
    if TOKEN:
        headers["Authorization"] = f"bearer {TOKEN}"
    if data:
        headers["Content-Type"] = "application/json"
    if accept:
        headers["Accept"] = accept

    request = urllib.request.Request(
        url, data=data, headers=headers
    )
    return urllib.request.urlopen(request, timeout=30)


def get_days():
    if DEMO:
        random.seed(7)
        end = dt.date.today()
        out = []

        for i in range(365, -1, -1):
            d = end - dt.timedelta(days=i)
            count = (
                0 if random.random() < .25
                else int(random.expovariate(1 / 6))
            )
            out.append((d, count))

        return out

    query = (
        '{user(login:"%s"){contributionsCollection'
        '{contributionCalendar{weeks{contributionDays'
        '{date contributionCount}}}}}}' % USER
    )

    response = json.load(
        http(
            "https://api.github.com/graphql",
            json.dumps({"query": query}).encode()
        )
    )

    weeks = response["data"]["user"][
        "contributionsCollection"
    ]["contributionCalendar"]["weeks"]

    return [
        (dt.date.fromisoformat(d["date"]), d["contributionCount"])
        for week in weeks
        for d in week["contributionDays"]
    ]


def get_repo(name):
    try:
        response = json.load(
            http(f"https://api.github.com/repos/{USER}/{name}")
        )
        return (
            response.get("language"),
            response.get("stargazers_count", 0)
        )
    except Exception:
        return None, None


def get_avatar():
    if DEMO:
        return None

    try:
        response = http(f"https://github.com/{USER}.png?size=400")
        return (
            f"data:{response.headers.get_content_type()};base64,"
            + base64.b64encode(response.read()).decode()
        )
    except Exception:
        return None


# ───────────── HERO CARD ─────────────

def hero(avatar):
    p = PROFILE

    if avatar:
        pic = (
            '<defs>'
            '<clipPath id="c"><circle cx="705" cy="165" r="118"/>'
            '</clipPath>'
            '<filter id="g"><feColorMatrix type="saturate" '
            'values="0"/></filter></defs>'
            f'<image href="{avatar}" x="587" y="47" '
            'width="236" height="236" clip-path="url(#c)" '
            'filter="url(#g)" preserveAspectRatio="xMidYMid slice"/>'
            f'<circle cx="705" cy="165" r="118" fill="none" '
            f'stroke="{INK}" stroke-width="1.5"/>'
        )
    else:
        pic = (
            f'<circle cx="705" cy="165" r="118" fill="none" '
            f'stroke="{INK}" stroke-width="1.5"/>'
            f'<text x="705" y="195" text-anchor="middle" '
            f'class="serif" font-style="italic" font-size="96" '
            f'fill="{INK}">OD</text>'
        )

    lines = textwrap.wrap(p["tagline"], 48)

    body = (
        card(880, 330)
        + f'<rect class="blink" x="40" y="42" width="8" '
          f'height="8" fill="{BLUE}"/>'
        + f'<text x="58" y="50" class="mono" font-size="11" '
          f'letter-spacing="1.6" fill="{MUTE}">'
          f'{esc(p["eyebrow"])}</text>'
        + f'<text x="38" y="145" class="serif" font-size="84" '
          f'fill="{INK}">{esc(p["first"])}</text>'
        + f'<text x="38" y="222" class="serif" font-style="italic" '
          f'font-size="84" fill="{INK}">{esc(p["last"])}</text>'
        + f'<text x="40" y="262" class="sans" font-size="15" '
          f'fill="#444">{esc(lines[0] if lines else "")}</text>'
        + f'<text x="40" y="283" class="sans" font-size="15" '
          f'fill="#444">{esc(" ".join(lines[1:]))}</text>'
        + f'<text x="40" y="312" class="mono" font-size="12" '
          f'fill="#111">{esc(p["link"])}'
          f'<tspan fill="{BLUE}"> ↗</tspan></text>'
        + pic
    )

    return svg(880, 330, body)


# ───────────── CONTRIBUTION HEATMAP ─────────────

def heatmap(days):
    first = days[0][0]
    start = first - dt.timedelta(
        days=(first.weekday() + 1) % 7
    )

    n = (days[-1][0] - start).days // 7 + 1
    step = 800 / n
    size = step - 3
    x0, y0 = 40, 88

    nz = sorted(c for _, c in days if c > 0)
    q = (
        [nz[int(len(nz) * p)] for p in (.25, .5, .75)]
        if nz else [1, 2, 3]
    )

    pal = [
        "#e3e5f0", "#c3cbf6", "#8c9cf2",
        "#4d66ee", "#2340f0"
    ]

    def level(count):
        return 0 if count == 0 else 1 + sum(count > t for t in q)

    cells, months, seen = [], [], set()

    for d, count in days:
        col = (d - start).days // 7
        row = (d.weekday() + 1) % 7

        cells.append(
            f'<rect class="cell" '
            f'style="animation-delay:{col*.025:.2f}s" '
            f'x="{x0+col*step:.1f}" y="{y0+row*step:.1f}" '
            f'width="{size:.1f}" height="{size:.1f}" '
            f'rx="2.5" fill="{pal[level(count)]}">'
            f'<title>{d}: {count}</title></rect>'
        )

        key = (d.year, d.month)
        if key not in seen and (d.day == 1 or d.weekday() == 6):
            seen.add(key)
            months.append((col, d.strftime("%b")))

    ly = y0 + 7 * step + 18

    labels = "".join(
        f'<text x="{x0+c*step:.1f}" y="{ly:.0f}" '
        f'class="mono" font-size="10" fill="{MUTE}">{m}</text>'
        for c, m in months
    )

    ly2 = ly + 26

    legend = (
        f'<text x="718" y="{ly2:.0f}" class="mono" '
        f'font-size="10" fill="{MUTE}">less</text>'
        + "".join(
            f'<rect x="{770+i*14}" y="{ly2-9:.0f}" '
            f'width="10" height="10" rx="2" fill="{p}"/>'
            for i, p in enumerate(pal)
        )
        + f'<text x="846" y="{ly2:.0f}" class="mono" '
          f'font-size="10" fill="{MUTE}">more</text>'
    )

    h = int(ly2 + 30)

    body = (
        card(880, h)
        + f'<text x="40" y="56" class="serif" font-size="28" '
          f'fill="{INK}">Every day, '
          f'<tspan font-style="italic" fill="{BLUE}">'
          f'in blue</tspan></text>'
        + f'<text x="840" y="52" text-anchor="end" class="mono" '
          f'font-size="10" letter-spacing="1.4" fill="{MUTE}">'
          f'REFRESHED DAILY</text>'
        + "".join(cells) + labels + legend
    )

    return svg(880, h, body)


# ───────────── CONTRIBUTION STATS ─────────────

def stats(days):
    total = sum(c for _, c in days)
    active = sum(c > 0 for _, c in days)
    best = max(c for _, c in days)

    run = longest = 0
    for _, count in days:
        run = run + 1 if count > 0 else 0
        longest = max(longest, run)

    i = len(days) - 1
    if days[i][1] == 0:
        i -= 1

    current = 0
    while i >= 0 and days[i][1] > 0:
        current += 1
        i -= 1

    last = days[-1][0]
    keys = []
    y, m = last.year, last.month

    for _ in range(12):
        keys.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1

    keys.reverse()
    sums = {k: 0 for k in keys}

    for d, count in days:
        if (d.year, d.month) in sums:
            sums[(d.year, d.month)] += count

    vals = [sums[k] for k in keys]
    maximum = max(vals) or 1
    bars = ""

    for i, (k, value) in enumerate(zip(keys, vals)):
        height = max(4, 120 * value / maximum)
        x = 40 + i * 44
        top = 270 - height

        color = (
            BLUE if value == maximum
            else ("#c9c9c3" if i == 11 else "#1a1a1a")
        )

        bars += (
            f'<rect class="bar" style="animation-delay:{i*.06:.2f}s" '
            f'x="{x}" y="{top:.0f}" width="36" '
            f'height="{height:.0f}" rx="3" fill="{color}"/>'
            f'<text x="{x+18}" y="290" text-anchor="middle" '
            f'class="mono" font-size="9" fill="{MUTE}">'
            f'{dt.date(k[0], k[1], 1).strftime("%b")}</text>'
        )

        if value == maximum:
            bars += (
                f'<text x="{x+18}" y="{top-7:.0f}" '
                f'text-anchor="middle" class="mono" '
                f'font-size="10" fill="{BLUE}">{value:,}</text>'
            )

    def stat(y, number, unit, desc, line=True):
        result = (
            f'<text x="620" y="{y}" class="serif" '
            f'font-style="italic" font-size="38" fill="{INK}">'
            f'{number}'
            f'<tspan font-size="{24 if unit else 0}" '
            f'fill="{MUTE}">{unit}</tspan></text>'
            f'<text x="620" y="{y+20}" class="sans" '
            f'font-size="11.5" fill="{MUTE}">{esc(desc)}</text>'
        )

        if line:
            result += (
                f'<line x1="620" x2="840" y1="{y+40}" '
                f'y2="{y+40}" stroke="{EDGE}"/>'
            )

        return result

    body = (
        card(880, 320)
        + f'<text x="40" y="52" class="mono" font-size="10" '
          f'letter-spacing="1.4" fill="{MUTE}">'
          f'THE LAST 12 MONTHS ON GITHUB</text>'
        + f'<text x="40" y="104" class="serif" '
          f'font-style="italic" font-size="46" fill="{INK}">'
          f'{total:,} contributions</text>'
        + bars
        + stat(
            108, current,
            " day" if current == 1 else " days",
            "current streak, and the longest is " + str(longest)
        )
        + stat(192, active, f" / {len(days)}", "days with a commit")
        + stat(276, best, "", "on the busiest day", False)
    )

    return svg(880, 320, body)


# ───────────── PROFILE HIGHLIGHT TILES ─────────────

def tiles():
    out = ""

    for i, t in enumerate(TILES):
        x = i * 300
        color = t["fg"]
        lines = textwrap.wrap(t["text"], 34)[:3]

        headline_size = (
            34 if len(t["big"]) > 8
            else (36 if t["label"] == "EXPLORE" else 46)
        )

        out += (
            f'<rect x="{x}" y="0" width="280" height="205" '
            f'rx="14" fill="{t["bg"]}"/>'
            f'<text x="{x+22}" y="36" class="mono" '
            f'font-size="10" letter-spacing="1.5" '
            f'fill="{color}" opacity=".85">'
            f'{esc(t["label"])}</text>'
            f'<text x="{x+258}" y="37" text-anchor="end" '
            f'font-size="14" fill="{color}" opacity=".85">→</text>'
            f'<text x="{x+22}" y="104" class="serif" '
            f'font-size="{headline_size}" fill="{color}">'
            f'{esc(t["big"])} '
            f'<tspan font-style="italic">{esc(t["it"])}</tspan>'
            f'</text>'
            + "".join(
                f'<text x="{x+22}" y="{140+j*19}" '
                f'class="sans" font-size="12.5" fill="{color}" '
                f'opacity=".95">{esc(line)}</text>'
                for j, line in enumerate(lines)
            )
        )

    return svg(880, 205, out)


# ───────────── TECH STACK CARD WITH ICON TILES ─────────────

def techstack():
    W = 880
    label_x = 40
    start_x = 250

    tile_w = 70
    tile_h = 72
    gap_x = 8
    gap_y = 8
    max_cols = 7

    body = (
        f'<text x="40" y="54" class="serif" font-size="30" '
        f'fill="{INK}">My '
        f'<tspan font-style="italic" fill="{BLUE}">'
        f'toolkit</tspan></text>'
        f'<text x="840" y="50" text-anchor="end" '
        f'class="mono" font-size="10" letter-spacing="1.4" '
        f'fill="{MUTE}">TECH STACK</text>'
    )

    current_y = 84

    for label, items in TECH_GROUPS:
        rows = (len(items) + max_cols - 1) // max_cols

        body += (
            f'<text x="{label_x}" y="{current_y+30}" '
            f'class="mono" font-size="10" letter-spacing="1.1" '
            f'fill="{MUTE}">{esc(label)}</text>'
        )

        for index, (name, mark, color) in enumerate(items):
            col = index % max_cols
            row = index // max_cols

            x = start_x + col * (tile_w + gap_x)
            y = current_y + row * (tile_h + gap_y)

            # White rounded tile
            body += (
                f'<rect x="{x}" y="{y}" width="{tile_w}" '
                f'height="{tile_h}" rx="9" fill="#ffffff" '
                f'stroke="{EDGE}"/>'
            )

            # Coloured logo-style icon background
            body += (
                f'<rect x="{x+17}" y="{y+6}" width="36" '
                f'height="36" rx="9" fill="{color}"/>'
            )

            # Light text on dark logo backgrounds, dark text on yellow
            dark_marks = {"#F7DF1E", "#FCC624"}
            mark_color = "#202020" if color in dark_marks else "#ffffff"

            font_size = 11 if len(mark) > 3 else 14

            body += (
                f'<text x="{x+35}" y="{y+29}" '
                f'text-anchor="middle" class="sans" '
                f'font-size="{font_size}" font-weight="700" '
                f'fill="{mark_color}">{esc(mark)}</text>'
            )

            # Technology name
            name_size = 9 if len(name) > 11 else 10

            body += (
                f'<text x="{x+35}" y="{y+59}" '
                f'text-anchor="middle" class="sans" '
                f'font-size="{name_size}" fill="{INK}">'
                f'{esc(name)}</text>'
            )

        current_y += rows * (tile_h + gap_y) + 17

    H = current_y + 5

    return svg(W, H, card(W, H) + body)


# ───────────── PROJECT SECTION ─────────────

def heading():
    css = (
        ".h{fill:#141414}.i{fill:#3355ff}"
        "@media (prefers-color-scheme:dark){"
        ".h{fill:#e6edf3}.i{fill:#7b92ff}}"
    )

    return svg(
        880,
        56,
        '<text x="2" y="38" class="serif h" font-size="30">'
        'What I\'m <tspan class="i" font-style="italic">'
        'coding</tspan></text>',
        css
    )


def project(p):
    lang, stars = (
        get_repo(p["repo"])
        if p["repo"] and not DEMO
        else (None, None)
    )

    foot = " · ".join(
        filter(
            None,
            [
                lang or p["lang"],
                f"★ {stars}" if stars is not None else None
            ]
        )
    )

    lines = textwrap.wrap(p["desc"], 36)[:4]

    body = (
        card(280, 190, 12)
        + f'<rect x="22" y="26" width="8" height="8" '
          f'fill="{p["color"]}"/>'
        + f'<text x="38" y="35" class="sans" font-size="14" '
          f'font-weight="600" fill="{INK}">'
          f'{esc(p["name"])}</text>'
        + "".join(
            f'<text x="22" y="{70+j*19}" class="sans" '
            f'font-size="12.5" fill="#55554f">'
            f'{esc(line)}</text>'
            for j, line in enumerate(lines)
        )
        + f'<line x1="22" x2="258" y1="152" y2="152" '
          f'stroke="{EDGE}"/>'
        + f'<text x="22" y="173" class="mono" '
          f'font-size="10.5" fill="{MUTE}">'
          f'{esc(foot)}</text>'
    )

    return svg(280, 190, body)


# ───────────── GENERATE ALL CARDS ─────────────

if __name__ == "__main__":
    days = get_days()

    write("hero.svg", hero(get_avatar()))
    write("heatmap.svg", heatmap(days))
    write("stats.svg", stats(days))

    # Updated highlight cards
    write("tiles.svg", tiles())

    # Tech stack with colourful icon-style tiles
    write("techstack.svg", techstack())

    write("heading-coding.svg", heading())

    for i, p in enumerate(PROJECTS, 1):
        write(f"project-{i}.svg", project(p))

    print("\nAll profile cards generated successfully!")
