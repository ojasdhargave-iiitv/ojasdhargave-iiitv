#!/usr/bin/env python3
"""Generates editorial-style SVG cards for the GitHub profile README.
Usage:  GITHUB_TOKEN=... GITHUB_USER=ojasdhargave-iiitv python scripts/generate.py
        python scripts/generate.py --demo     (fake data, no network, for previewing)
Stdlib only."""
import os, sys, json, base64, random, textwrap, datetime as dt, urllib.request
from html import escape as esc

USER  = os.environ.get("GITHUB_USER", "ojasdhargave-iiitv")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
DEMO  = "--demo" in sys.argv
OUT   = "assets"

# ───────────── EDIT YOUR CONTENT HERE ─────────────
PROFILE = dict(
    first="Ojas", last="Dhargave",
    eyebrow="FULL-STACK DEVELOPER  ·  IIIT VADODARA",
    tagline="I build full-stack products from 0 to 1, from pixel-perfect UI/UX to robust backends.",
    link="github.com/ojasdhargave-iiitv",
)
TILES = [
    dict(label="BUILD",  big="3",   it="projects", bg="#3355ff", fg="#ffffff",
         text="PortionUp, a SaaS Backend Boilerplate IDE, and a from-scratch Self Driving Car."),
    dict(label="DETECT", big="88%", it="mAP",      bg="#ee4035", fg="#ffffff",
         text="YOLO + OpenCV on a custom food dataset, with 35% lower inference latency."),
    dict(label="LEARN",  big="CSE", it="'28",      bg="#ffc82c", fg="#1a1a1a",
         text="Computer Science at IIIT Vadodara, shipping from design to deploy."),
]
# repo=None -> card is not linked and shows no star count
PROJECTS = [
    dict(name="portionup", repo="portionup", color="#3355ff", lang="Python",
         desc="Real-time multi-object food detection and nutrition estimation. YOLO + OpenCV, 88% mAP."),
    dict(name="saas-backend-ide", repo=None, color="#ee4035", lang="TypeScript",
         desc="Code editor, compiler pipeline and backend template engine. Cuts setup time by 65%."),
    dict(name="self-driving-car", repo="Self_driving_Car", color="#ffc82c", lang="JavaScript",
         desc="A neural network written with zero libraries that navigates traffic on its own."),
]
# ───────────────────────────────────────────────

CSS = """
.serif{font-family:Georgia,'Times New Roman',serif}
.sans{font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'SFMono-Regular',Menlo,Consolas,'Courier New',monospace}
.cell{opacity:0;animation:pop .5s ease-out forwards}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
.bar{transform-origin:bottom;animation:grow .8s ease-out both}
@keyframes grow{from{transform:scaleY(0)}to{transform:none}}
.blink{animation:bl 1.4s steps(1) infinite}@keyframes bl{50%{opacity:.2}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.cell{opacity:1!important}}
"""
CARD, EDGE, INK, MUTE, BLUE = "#f4f3ee", "#e2e0d8", "#141414", "#6b6b66", "#3355ff"

def svg(w, h, body, extra_css=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<style>{CSS}{extra_css}</style>{body}</svg>')

def card(w, h, rx=16):
    return f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{CARD}" stroke="{EDGE}"/>'

def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f: f.write(content)
    print("wrote", name)

# ───────────── data ─────────────
def http(url, data=None, accept=None):
    h = {"User-Agent": "profile-cards"}
    if TOKEN: h["Authorization"] = f"bearer {TOKEN}"
    if data: h["Content-Type"] = "application/json"
    if accept: h["Accept"] = accept
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=30)

def get_days():
    if DEMO:
        random.seed(7); end = dt.date.today(); out = []
        for i in range(365, -1, -1):
            d = end - dt.timedelta(days=i)
            out.append((d, 0 if random.random() < .25 else int(random.expovariate(1/6))))
        return out
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % USER
    r = json.load(http("https://api.github.com/graphql", json.dumps({"query": q}).encode()))
    weeks = r["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]

def get_repo(name):
    try:
        r = json.load(http(f"https://api.github.com/repos/{USER}/{name}"))
        return r.get("language"), r.get("stargazers_count", 0)
    except Exception: return None, None

def get_avatar():
    if DEMO: return None
    try:
        r = http(f"https://github.com/{USER}.png?size=400")
        return f"data:{r.headers.get_content_type()};base64," + base64.b64encode(r.read()).decode()
    except Exception: return None

# ───────────── cards ─────────────
def hero(avatar):
    P = PROFILE
    if avatar:
        pic = (f'<defs><clipPath id="c"><circle cx="705" cy="165" r="118"/></clipPath>'
               f'<filter id="g"><feColorMatrix type="saturate" values="0"/></filter></defs>'
               f'<image href="{avatar}" x="587" y="47" width="236" height="236" clip-path="url(#c)" filter="url(#g)" preserveAspectRatio="xMidYMid slice"/>'
               f'<circle cx="705" cy="165" r="118" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    else:
        pic = (f'<circle cx="705" cy="165" r="118" fill="none" stroke="{INK}" stroke-width="1.5"/>'
               f'<text x="705" y="195" text-anchor="middle" class="serif" font-style="italic" font-size="96" fill="{INK}">OD</text>')
    body = (card(880, 330) +
        f'<rect class="blink" x="40" y="42" width="8" height="8" fill="{BLUE}"/>'
        f'<text x="58" y="50" class="mono" font-size="11" letter-spacing="1.6" fill="{MUTE}">{esc(P["eyebrow"])}</text>'
        f'<text x="38" y="145" class="serif" font-size="84" fill="{INK}">{esc(P["first"])}</text>'
        f'<text x="38" y="222" class="serif" font-style="italic" font-size="84" fill="{INK}">{esc(P["last"])}</text>'
        f'<text x="40" y="262" class="sans" font-size="15" fill="#444">{esc(textwrap.wrap(P["tagline"], 48)[0])}</text>'
        f'<text x="40" y="283" class="sans" font-size="15" fill="#444">{esc(" ".join(textwrap.wrap(P["tagline"], 48)[1:]))}</text>'
        f'<text x="40" y="312" class="mono" font-size="12" fill="#111">{esc(P["link"])}<tspan fill="{BLUE}"> ↗</tspan></text>' + pic)
    return svg(880, 330, body)

def heatmap(days):
    first = days[0][0]; start = first - dt.timedelta(days=(first.weekday()+1) % 7)  # Sunday
    n = (days[-1][0] - start).days // 7 + 1
    step = 800 / n; size = step - 3; x0, y0 = 40, 88
    nz = sorted(c for _, c in days if c > 0)
    q = [nz[int(len(nz)*p)] for p in (.25, .5, .75)] if nz else [1, 2, 3]
    pal = ["#e3e5f0", "#c3cbf6", "#8c9cf2", "#4d66ee", "#2340f0"]
    lvl = lambda c: 0 if c == 0 else 1 + sum(c > t for t in q)
    cells, months, seen = [], [], set()
    for d, c in days:
        col = (d - start).days // 7; row = (d.weekday()+1) % 7
        cells.append(f'<rect class="cell" style="animation-delay:{col*.025:.2f}s" x="{x0+col*step:.1f}" y="{y0+row*step:.1f}" '
                     f'width="{size:.1f}" height="{size:.1f}" rx="2.5" fill="{pal[lvl(c)]}"><title>{d}: {c}</title></rect>')
        if d.day <= 7 and (d.year, d.month) not in seen and d.weekday() == 6 or (d.day == 1 and (d.year, d.month) not in seen):
            seen.add((d.year, d.month)); months.append((col, d.strftime("%b")))
    ly = y0 + 7*step + 18
    lab = "".join(f'<text x="{x0+c*step:.1f}" y="{ly:.0f}" class="mono" font-size="10" fill="{MUTE}">{m}</text>' for c, m in months)
    ly2 = ly + 26
    leg = f'<text x="{840-5*14-52}" y="{ly2:.0f}" class="mono" font-size="10" fill="{MUTE}">less</text>' + \
          "".join(f'<rect x="{840-5*14-18+i*14}" y="{ly2-9:.0f}" width="10" height="10" rx="2" fill="{p}"/>' for i, p in enumerate(pal)) + \
          f'<text x="{840-5*14+56}" y="{ly2:.0f}" class="mono" font-size="10" fill="{MUTE}">more</text>'
    h = int(ly2 + 30)
    body = (card(880, h) +
        f'<text x="40" y="56" class="serif" font-size="28" fill="{INK}">Every day, <tspan font-style="italic" fill="{BLUE}">in blue</tspan></text>'
        f'<text x="840" y="52" text-anchor="end" class="mono" font-size="10" letter-spacing="1.4" fill="{MUTE}">REFRESHED DAILY</text>'
        + "".join(cells) + lab + leg)
    return svg(880, h, body)

def stats(days):
    total = sum(c for _, c in days); active = sum(c > 0 for _, c in days); best = max(c for _, c in days)
    run = longest = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0; longest = max(longest, run)
    i = len(days) - 1
    if days[i][1] == 0: i -= 1
    cur = 0
    while i >= 0 and days[i][1] > 0: cur += 1; i -= 1
    last = days[-1][0]; keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append((y, m)); m -= 1
        if m == 0: m, y = 12, y-1
    keys.reverse(); sums = {k: 0 for k in keys}
    for d, c in days:
        if (d.year, d.month) in sums: sums[(d.year, d.month)] += c
    vals = [sums[k] for k in keys]; mx = max(vals) or 1
    bars = ""
    for i, (k, v) in enumerate(zip(keys, vals)):
        hgt = max(4, 120 * v / mx); x = 40 + i*44; top = 270 - hgt
        col = BLUE if v == mx else ("#c9c9c3" if i == 11 else "#1a1a1a")
        bars += (f'<rect class="bar" style="animation-delay:{i*.06:.2f}s" x="{x}" y="{top:.0f}" width="36" height="{hgt:.0f}" rx="3" fill="{col}"/>'
                 f'<text x="{x+18}" y="290" text-anchor="middle" class="mono" font-size="9" fill="{MUTE}">{dt.date(k[0], k[1], 1).strftime("%b")}</text>')
        if v == mx: bars += f'<text x="{x+18}" y="{top-7:.0f}" text-anchor="middle" class="mono" font-size="10" fill="{BLUE}">{v:,}</text>'
    def stat(y, num, unit, desc, line=True):
        s = (f'<text x="620" y="{y}" class="serif" font-style="italic" font-size="38" fill="{INK}">{num}'
             f'<tspan font-size="{24 if unit else 0}" fill="{MUTE}">{unit}</tspan></text>'
             f'<text x="620" y="{y+20}" class="sans" font-size="11.5" fill="{MUTE}">{esc(desc)}</text>')
        return s + (f'<line x1="620" x2="840" y1="{y+40}" y2="{y+40}" stroke="{EDGE}"/>' if line else "")
    body = (card(880, 320) +
        f'<text x="40" y="52" class="mono" font-size="10" letter-spacing="1.4" fill="{MUTE}">THE LAST 12 MONTHS ON GITHUB</text>'
        f'<text x="40" y="104" class="serif" font-style="italic" font-size="46" fill="{INK}">{total:,} contributions</text>' + bars +
        stat(108, cur, " day" if cur == 1 else " days", "current streak, and the longest is " + str(longest)) +
        stat(192, active, f" / {len(days)}", "days with a commit") +
        stat(276, best, "", "on the busiest day", line=False))
    return svg(880, 320, body)

def tiles():
    out = card(0, 0).replace('<rect', '<g') and ""  # (no outer card)
    for i, t in enumerate(TILES):
        x = i * 300; mutedfg = t["fg"]
        lines = textwrap.wrap(t["text"], 34)[:3]
        out += (f'<rect x="{x}" y="0" width="280" height="205" rx="14" fill="{t["bg"]}"/>'
                f'<text x="{x+22}" y="36" class="mono" font-size="10" letter-spacing="1.5" fill="{mutedfg}" opacity=".85">{t["label"]}</text>'
                f'<text x="{x+258}" y="37" text-anchor="end" font-size="14" fill="{mutedfg}" opacity=".85">→</text>'
                f'<text x="{x+22}" y="104" class="serif" font-size="46" fill="{mutedfg}">{esc(t["big"])} '
                f'<tspan font-style="italic">{esc(t["it"])}</tspan></text>' +
                "".join(f'<text x="{x+22}" y="{140+j*19}" class="sans" font-size="12.5" fill="{mutedfg}" opacity=".95">{esc(l)}</text>' for j, l in enumerate(lines)))
    return svg(880, 205, out)

def techstack():
    groups = [
        ("LANGUAGES", ["C / C++", "JavaScript", "TypeScript", "Python", "Go", "HTML", "CSS", "SQL"]),
        ("FRONTEND", ["React.js", "Tailwind CSS", "Three.js", "Figma", "Blender"]),
        ("BACKEND", ["Node.js", "Express.js", "FastAPI", "OpenCV"]),
        ("DATABASES & CLOUD", ["MongoDB", "MySQL", "PostgreSQL", "Redis", "Supabase", "Prisma", "Vercel", "AWS"]),
        ("TOOLS & DEVOPS", ["Git", "GitHub", "Docker", "GitHub Actions", "VS Code", "Postman", "Linux"]),
    ]
    y = 104
    body = (f'<text x="40" y="54" class="serif" font-size="30" fill="{INK}">My '
            f'<tspan font-style="italic" fill="{BLUE}">toolkit</tspan></text>'
            f'<text x="840" y="50" text-anchor="end" class="mono" font-size="10" '
            f'letter-spacing="1.4" fill="{MUTE}">TECH STACK</text>')
    for label, items in groups:
        body += f'<text x="40" y="{y+5}" class="mono" font-size="10.5" letter-spacing="1.1" fill="{MUTE}">{esc(label)}</text>'
        x, row, max_row = 250, 0, 0
        for item in items:
            width = max(54, len(item) * 7.1 + 22)
            if x + width > 842:
                row += 1
                max_row = row
                x = 250
            chip_y = y + row * 34
            body += (f'<rect x="{x}" y="{chip_y-15}" width="{width:.1f}" height="27" rx="7" '
                     f'fill="#ffffff" stroke="{EDGE}"/>'
                     f'<text x="{x+width/2:.1f}" y="{chip_y+3}" text-anchor="middle" class="sans" '
                     f'font-size="11.5" fill="{INK}">{esc(item)}</text>')
            x += width + 8
        y += max(66, (max_row + 1) * 34 + 32)
    height = y - 8
    return svg(880, height, card(880, height) + body)

def heading():
    css = ".h{fill:#141414}.i{fill:#3355ff}@media (prefers-color-scheme:dark){.h{fill:#e6edf3}.i{fill:#7b92ff}}"
    return svg(880, 56, f'<text x="2" y="38" class="serif h" font-size="30">What I\'m <tspan class="i" font-style="italic">coding</tspan></text>', css)

def project(p):
    lang, stars = get_repo(p["repo"]) if (p["repo"] and not DEMO) else (None, None)
    foot = " · ".join(filter(None, [lang or p["lang"], f"★ {stars}" if stars is not None else None]))
    lines = textwrap.wrap(p["desc"], 36)[:4]
    body = (card(280, 190, 12) +
        f'<rect x="22" y="26" width="8" height="8" fill="{p["color"]}"/>'
        f'<text x="38" y="35" class="sans" font-size="14" font-weight="600" fill="{INK}">{esc(p["name"])}</text>' +
        "".join(f'<text x="22" y="{70+j*19}" class="sans" font-size="12.5" fill="#55554f">{esc(l)}</text>' for j, l in enumerate(lines)) +
        f'<line x1="22" x2="258" y1="152" y2="152" stroke="{EDGE}"/>'
        f'<text x="22" y="173" class="mono" font-size="10.5" fill="{MUTE}">{esc(foot)}</text>')
    return svg(280, 190, body)

if __name__ == "__main__":
    days = get_days()
    write("hero.svg", hero(get_avatar()))
    write("heatmap.svg", heatmap(days))
    write("stats.svg", stats(days))
    write("tiles.svg", tiles())
    write("techstack.svg", techstack())
    write("heading-coding.svg", heading())
    for i, p in enumerate(PROJECTS, 1): write(f"project-{i}.svg", project(p))
