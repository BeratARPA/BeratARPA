"""Generates the animated SVGs for the visual profile README (dark and light variants).

Everything is drawn from data in ./data and the constants below, so a GitHub Action can
re-run this script daily and commit fresh numbers. No third-party image service is used.
"""
import json
import os
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(os.environ.get("PROFILE_ROOT", Path(__file__).parent))
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(bg="#0d1117", card="#161b22", card2="#1c2330", border="#30363d", text="#e6edf3",
                 muted="#8b949e", accent="#22d3ee", accent2="#a78bfa", paper="#f8fafc", ink="#0f172a",
                 printer="#2b3340", printer2="#3b4554", empty="#161b22",
                 heat=["#0e4429", "#006d32", "#26a641", "#39d353"]),
    "light": dict(bg="#ffffff", card="#f6f8fa", card2="#eef2f6", border="#d0d7de", text="#1f2328",
                  muted="#59636e", accent="#0891b2", accent2="#7c3aed", paper="#ffffff", ink="#0f172a",
                  printer="#cbd5e1", printer2="#94a3b8", empty="#ebedf0",
                  heat=["#9be9a8", "#40c463", "#30a14e", "#216e39"]),
}

SANS = "Segoe UI, Ubuntu, Helvetica Neue, Arial, sans-serif"
MONO = "Consolas, Menlo, DejaVu Sans Mono, monospace"

# ---- data -----------------------------------------------------------------------------
contrib = json.loads((HERE / "data/contrib.json").read_text(encoding="utf-8"))["data"]["user"]["contributionsCollection"]
calendar = contrib["contributionCalendar"]
TOTAL_CONTRIB = calendar["totalContributions"]
summary = json.loads((HERE / "data/summary.json").read_text(encoding="utf-8"))
STARS = summary["stars"]
packages = json.loads((HERE / "data/packages.json").read_text(encoding="utf-8"))
# Hand-kept facts the Actions token cannot see (private repos): see data/static.json.
static = json.loads((HERE / "data/static.json").read_text(encoding="utf-8"))

# The Actions token only sees the private count as 0; fall back to the last measured share.
restricted = contrib.get("restrictedContributionsCount") or 0
PRIVATE_SHARE = round(restricted / TOTAL_CONTRIB * 100) if restricted else static["private_share"]

NUGET_PRINTHTML = packages["nuget_printhtml"]
NUGET_ARE = packages["nuget_are"]
NPM_ARE = packages["npm_are"]
PUB_POINTS = packages.get("pub_points", 160)
PACKAGE_DOWNLOADS = NUGET_PRINTHTML + NUGET_ARE + NPM_ARE
FLUTTER_APPS = static["flutter_apps"]
REPO_STARS = summary.get("repo_stars", {})


def k(n):
    return f"{n / 1000:.1f}K".replace(".0K", "K") if n >= 1000 else str(n)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>')


def write(name, theme, content):
    (ASSETS / f"{name}-{theme}.svg").write_text(content, encoding="utf-8")


# ---- 1. header: name, rotating tagline, printer printing a receipt ---------------------
def header(t):
    c = THEMES[t]
    taglines = ["POS systems &amp; receipt printing", "food-delivery platform integrations",
                "Flutter apps for everyday problems", ".NET back end @ EasyHR"]
    cycle = 12
    tag = ""
    for i, line in enumerate(taglines):
        a, b = i / len(taglines), (i + 1) / len(taglines)
        tag += (f'<text x="0" y="0" font-family="{MONO}" font-size="21" fill="{c["accent"]}" opacity="0">&gt; {line}'
                f'<animate attributeName="opacity" dur="{cycle}s" repeatCount="indefinite" '
                f'keyTimes="0;{a:.3f};{a + 0.01:.3f};{b - 0.01:.3f};{b:.3f};1" values="0;0;1;1;0;0"/></text>')
    chips = ""
    x = 0
    for label in ["C# / .NET", "Flutter", "SQL Server", "Ankara, TR"]:
        w = 14 + len(label) * 8.2
        chips += (f'<g transform="translate({x},0)"><rect width="{w:.0f}" height="28" rx="14" fill="{c["card2"]}" stroke="{c["border"]}"/>'
                  f'<text x="{w / 2:.0f}" y="19" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{c["text"]}">{label}</text></g>')
        x += w + 8

    # receipt lines, printed one after another
    rows = [("BERAT ARPA", "", True), ("", "", False), ("PrintHTML.Core", k(NUGET_PRINTHTML), False),
            ("ARE  nuget/npm/pub", k(NUGET_ARE + NPM_ARE), False), ("Flutter apps", str(FLUTTER_APPS), False),
            ("Contributions/yr", k(TOTAL_CONTRIB), False), ("", "", False), ("TOTAL STARS", str(STARS), True)]
    period = 9.0
    receipt = ""
    for i, (left, right, bold) in enumerate(rows):
        y = 30 + i * 17
        start = 0.10 + i * 0.07
        weight = "700" if bold else "400"
        if not left and not right:
            line = f'<line x1="14" y1="{y - 4}" x2="156" y2="{y - 4}" stroke="{c["ink"]}" stroke-dasharray="3 3" opacity="0.5"/>'
        else:
            line = (f'<text x="14" y="{y}" font-family="{MONO}" font-size="11" font-weight="{weight}" fill="{c["ink"]}">{escape(left)}</text>'
                    f'<text x="156" y="{y}" text-anchor="end" font-family="{MONO}" font-size="11" font-weight="{weight}" fill="{c["ink"]}">{escape(right)}</text>')
        receipt += (f'<g opacity="0">{line}<animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" '
                    f'keyTimes="0;{start:.2f};{start + 0.03:.2f};0.9;0.95;1" values="0;0;1;1;0;0"/></g>')
    barcode = "".join(f'<rect x="{18 + i * 4}" y="176" width="{2 if i % 3 else 3}" height="18" fill="{c["ink"]}"/>' for i in range(34))
    paper = (f'<clipPath id="feed"><rect x="0" y="0" width="170" height="0">'
             f'<animate attributeName="height" dur="{period}s" repeatCount="indefinite" keyTimes="0;0.08;0.72;0.9;0.95;1" values="0;0;215;215;0;0"/></rect></clipPath>'
             f'<g clip-path="url(#feed)"><path d="M0 0 H170 V205 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 l-8.5 8 l-8.5 -8 Z" fill="{c["paper"]}" stroke="{c["border"]}"/>'
             f'{receipt}<g opacity="0">{barcode}<animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" keyTimes="0;0.68;0.71;0.9;0.95;1" values="0;0;1;1;0;0"/></g></g>')
    printer = (f'<rect x="-20" y="-44" width="210" height="52" rx="12" fill="{c["printer"]}"/>'
               f'<rect x="-6" y="-8" width="182" height="10" rx="5" fill="{c["printer2"]}"/>'
               f'<circle cx="166" cy="-26" r="5" fill="{c["accent"]}"><animate attributeName="opacity" dur="1.2s" repeatCount="indefinite" values="1;0.25;1"/></circle>'
               f'<rect x="4" y="-32" width="60" height="8" rx="4" fill="{c["printer2"]}"/>')
    body = (f'<rect width="900" height="300" rx="16" fill="{c["card"]}" stroke="{c["border"]}"/>'
            f'<g transform="translate(44,92)"><text font-family="{SANS}" font-size="56" font-weight="800" fill="{c["text"]}">Berat ARPA</text></g>'
            f'<g transform="translate(46,138)">{tag}<rect x="0" y="-18" width="2" height="22" fill="{c["accent"]}" opacity="0"/></g>'
            f'<text x="46" y="184" font-family="{SANS}" font-size="17" fill="{c["muted"]}">I build the software that runs at the counter, and the apps around it.</text>'
            f'<g transform="translate(46,214)">{chips}</g>'
            f'<g transform="translate(650,62)">{printer}<g transform="translate(0,2)">{paper}</g></g>')
    return svg(900, 300, body, "Berat ARPA: .NET and Flutter developer. POS, receipt printing and integrations.")


# ---- 2. stats infographic ------------------------------------------------------------------
def stats(t):
    c = THEMES[t]
    tiles = [(k(PACKAGE_DOWNLOADS) + "+", "package downloads", "NuGet + npm", c["accent"]),
             (str(STARS), "GitHub stars", "on public repos", "#f5b301"),
             ("4", "published packages", "NuGet · npm · pub.dev", c["accent2"]),
             (f"{FLUTTER_APPS}+", "Flutter apps", "shipped since 2025", "#00B4AB"),
             (f"{TOTAL_CONTRIB:,}", "contributions", f"last year · {PRIVATE_SHARE}% private", "#39d353")]
    w, gap = 168, 15
    body = ""
    for i, (num, label, sub, color) in enumerate(tiles):
        x = i * (w + gap)
        d = 0.15 * i
        body += (f'<g transform="translate({x},0)"><g opacity="0">'
                 f'<animate attributeName="opacity" begin="{d:.2f}s" dur="0.6s" fill="freeze" values="0;1"/>'
                 f'<animateTransform attributeName="transform" type="translate" begin="{d:.2f}s" dur="0.6s" fill="freeze" values="0 14;0 0"/>'
                 f'<rect width="{w}" height="150" rx="14" fill="{c["card"]}" stroke="{c["border"]}"/>'
                 f'<rect x="18" y="20" width="28" height="4" rx="2" fill="{color}"/>'
                 f'<text x="18" y="74" font-family="{SANS}" font-size="38" font-weight="800" fill="{c["text"]}">{escape(num)}</text>'
                 f'<text x="18" y="102" font-family="{SANS}" font-size="15" font-weight="600" fill="{c["text"]}">{escape(label)}</text>'
                 f'<text x="18" y="124" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">{escape(sub)}</text>'
                 f'<rect x="18" y="136" width="0" height="3" rx="1.5" fill="{color}">'
                 f'<animate attributeName="width" begin="{d + 0.4:.2f}s" dur="0.9s" fill="freeze" values="0;{w - 36}"/></rect>'
                 f'</g></g>')
    return svg(900, 150, body, f"{k(PACKAGE_DOWNLOADS)}+ package downloads, {STARS} stars, 4 packages, {FLUTTER_APPS}+ Flutter apps, {TOTAL_CONTRIB} contributions last year")


# ---- 3. project cards ----------------------------------------------------------------------
PROJECTS = [
    ("printer", "HTML-Thermal-Printer", "C# · WPF · NuGet", "Design receipts in HTML, print them on thermal printers.",
     [(f"★ {REPO_STARS.get('HTML-Thermal-Printer', 79)}", None), (f"{k(NUGET_PRINTHTML)} downloads", None), ("used in other apps", None)], "#7355dd"),
    ("are", "ARE rule engine", "C# · TypeScript · Dart", "One Action-Rule-Event engine, the same API in three ecosystems.",
     [(f"★ {REPO_STARS.get('ARE', 32)}", None), ("NuGet · npm · pub", None), (f"{PUB_POINTS}/160 pub points", None)], "#22d3ee"),
    ("courier", "Pentegrasyon Kurye", "Flutter · Firebase · Maps", "Courier app for restaurants: QR pickup, live map, push.",
     [("Google Play", None), ("App Store", None), ("built solo", None)], "#00B4AB"),
    ("radar", "Procurement Radar", ".NET 8 · PostgreSQL · Telegram", "Watches ~80 tender sources, sends matches to Telegram.",
     [("~80 sources", None), ("every 15 min", None), ("zero cost", None)], "#a78bfa"),
    ("fuel", "YakıtCep", "Flutter · Riverpod · EPDK", "Official fuel prices for every province, with charts and a widget.",
     [("81 provinces", None), ("TR / EN", None), ("APK release", None)], "#f97316"),
    ("boiler", "KombiKod", "Flutter · offline", "Boiler fault codes in the basement, no signal needed.",
     [("785 codes", None), ("24 brands", None), ("107 models", None)], "#ef4444"),
    ("lang", "Dilbaz", "Flutter · Supabase · Python", "Language learning built on learning science, from open data.",
     [("Android · Windows · web", None), ("300+ Dart files", None)], "#22c55e"),
    ("car", "CarKeep", "Flutter · Kotlin · Bluetooth", "Maintenance reminders the moment you leave the car.",
     [("520+ tests", None), ("no server", None), ("real-car tested", None)], "#eab308"),
]


def glyph(kind, color, c):
    """Small line-art icon per project, 44x44."""
    s = f'stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    shapes = {
        "printer": f'<rect x="6" y="14" width="32" height="14" rx="3" {s}/><path d="M12 14V6h20v8M12 28v10h20V28" {s}/><path d="M16 33h12" {s}/>',
        "are": f'<circle cx="10" cy="22" r="5" {s}/><circle cx="34" cy="10" r="5" {s}/><circle cx="34" cy="34" r="5" {s}/><path d="M15 20l14-8M15 24l14 8" {s}/>',
        "courier": f'<path d="M22 40s12-12 12-21a12 12 0 0 0-24 0c0 9 12 21 12 21z" {s}/><circle cx="22" cy="19" r="4" {s}/>',
        "radar": f'<circle cx="22" cy="22" r="16" {s}/><circle cx="22" cy="22" r="8" {s}/><path d="M22 22l11-11" {s}/>',
        "fuel": f'<rect x="8" y="6" width="18" height="32" rx="3" {s}/><path d="M12 14h10M26 16l7 5v12a3 3 0 0 1-6 0v-6h-1" {s}/>',
        "boiler": f'<rect x="10" y="4" width="24" height="36" rx="4" {s}/><circle cx="22" cy="18" r="6" {s}/><path d="M16 32h12" {s}/>',
        "lang": f'<path d="M6 10h20v16H14l-6 6V10z" {s}/><path d="M24 18h14v16l-5-4H24z" {s}/>',
        "car": f'<path d="M6 28v-6l5-9h22l5 9v6z" {s}/><circle cx="13" cy="30" r="4" {s}/><circle cx="31" cy="30" r="4" {s}/>',
    }
    return f'<rect width="44" height="44" rx="12" fill="{color}" opacity="0.14"/>{shapes[kind]}'


def card(t, p):
    kind, name, tech, desc, chips, color = p
    c = THEMES[t]
    chip_svg = ""
    x = 0
    for label, _ in chips:
        w = 16 + len(label) * 6.9
        chip_svg += (f'<g transform="translate({x:.0f},0)"><rect width="{w:.0f}" height="24" rx="12" fill="{color}" opacity="0.16"/>'
                     f'<text x="{w / 2:.0f}" y="16.5" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="{c["text"]}">{escape(label)}</text></g>')
        x += w + 6
    # Wrap the description at ~54 characters so it never runs past the card edge.
    words, lines, cur = desc.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > 54 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = f"{cur} {wd}".strip()
    lines.append(cur)
    desc_svg = "".join(f'<text x="22" y="{92 + i * 18}" font-family="{SANS}" font-size="14" fill="{c["text"]}">{escape(l)}</text>'
                       for i, l in enumerate(lines[:2]))
    body = (f'<rect x="0.5" y="0.5" width="439" height="163" rx="14" fill="{c["card"]}" stroke="{c["border"]}"/>'
            f'<rect x="0" y="22" width="4" height="44" rx="2" fill="{color}"/>'
            f'<g transform="translate(22,22)">{glyph(kind, color, c)}</g>'
            f'<text x="80" y="42" font-family="{SANS}" font-size="20" font-weight="700" fill="{c["text"]}">{escape(name)}</text>'
            f'<text x="80" y="63" font-family="{MONO}" font-size="12.5" fill="{c["muted"]}">{escape(tech)}</text>'
            f'{desc_svg}'
            f'<g transform="translate(22,124)">{chip_svg}</g>'
            f'<circle cx="414" cy="30" r="4" fill="{color}"><animate attributeName="r" dur="2.4s" repeatCount="indefinite" values="4;6;4"/>'
            f'<animate attributeName="opacity" dur="2.4s" repeatCount="indefinite" values="1;0.4;1"/></circle>')
    return svg(440, 164, body, f"{name}: {desc}")


# ---- 4. contribution heatmap (real data) ----------------------------------------------------
def activity(t):
    c = THEMES[t]
    weeks = calendar["weeks"]
    max_count = max(d["contributionCount"] for w in weeks for d in w["contributionDays"]) or 1
    cell, gap, ox, oy = 13, 3, 40, 56
    cells, months, last_month = "", "", None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dt = date.fromisoformat(d["date"])
            n = d["contributionCount"]
            if n == 0:
                fill = c["empty"]
            else:
                q = n / max_count
                fill = c["heat"][0 if q < 0.15 else 1 if q < 0.4 else 2 if q < 0.7 else 3]
            x = ox + wi * (cell + gap)
            y = oy + dt.isoweekday() % 7 * (cell + gap)
            cells += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="0">'
                      f'<animate attributeName="opacity" begin="{wi * 0.025:.3f}s" dur="0.4s" fill="freeze" values="0;1"/></rect>')
            if dt.day <= 7 and dt.isoweekday() % 7 == 0 and dt.month != last_month:
                months += f'<text x="{x}" y="{oy - 10}" font-family="{SANS}" font-size="11" fill="{c["muted"]}">{dt.strftime("%b")}</text>'
                last_month = dt.month
    days = "".join(f'<text x="{ox - 8}" y="{oy + i * (cell + gap) + 10}" text-anchor="end" font-family="{SANS}" font-size="10" fill="{c["muted"]}">{l}</text>'
                   for i, l in [(1, "Mon"), (3, "Wed"), (5, "Fri")])
    legend = "".join(f'<rect x="{770 + i * 17}" y="186" width="{cell}" height="{cell}" rx="3" fill="{f}"/>' for i, f in enumerate([c["empty"]] + c["heat"]))
    body = (f'<rect x="0.5" y="0.5" width="899" height="215" rx="14" fill="{c["card"]}" stroke="{c["border"]}"/>'
            f'<text x="24" y="32" font-family="{SANS}" font-size="16" font-weight="700" fill="{c["text"]}">{TOTAL_CONTRIB:,} contributions in the last year</text>'
            f'<text x="876" y="32" text-anchor="end" font-family="{SANS}" font-size="13" fill="{c["muted"]}">{PRIVATE_SHARE}% of it in private work repos</text>'
            f'{months}{days}{cells}'
            f'<text x="762" y="197" text-anchor="end" font-family="{SANS}" font-size="11" fill="{c["muted"]}">Less</text>{legend}'
            f'<text x="862" y="197" font-family="{SANS}" font-size="11" fill="{c["muted"]}">More</text>')
    return svg(900, 216, body, f"{TOTAL_CONTRIB} contributions in the last year")


# ---- 5. languages + stack ----------------------------------------------------------------
def toolbox(t):
    c = THEMES[t]
    langs = [tuple(x) for x in static["languages"]]
    total = sum(n for _, n, _ in langs)
    bar_w, x = 852, 24
    bars, legend = "", ""
    lx = 24
    for i, (name, n, color) in enumerate(langs):
        w = bar_w * n / total
        bars += (f'<rect x="{x:.1f}" y="50" width="0" height="14" fill="{color}">'
                 f'<animate attributeName="width" begin="{i * 0.12:.2f}s" dur="0.7s" fill="freeze" values="0;{max(w - 2, 1):.1f}"/></rect>')
        x += w
        label = f"{name} {n}"
        legend += (f'<circle cx="{lx + 5}" cy="88" r="5" fill="{color}"/>'
                   f'<text x="{lx + 15}" y="92" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{escape(name)} <tspan fill="{c["muted"]}">{n}</tspan></text>')
        lx += 30 + len(label) * 7.2
    groups = [("Back end", ["C#", "ASP.NET Core", "Web API", "EF Core", "Dapper", "SignalR", "RabbitMQ"]),
              ("Clients", ["Flutter", "WPF", "WinForms", "Kotlin"]),
              ("Data", ["SQL Server", "PostgreSQL", "SQLite", "Firebase", "Supabase"]),
              ("Devices", ["ESC/POS printers", "fiscal printers (ÖKC)", "barcode scanners", "scales"])]
    rows = ""
    for gi, (gname, items) in enumerate(groups):
        y = 130 + gi * 40
        rows += f'<text x="24" y="{y + 17}" font-family="{SANS}" font-size="13" font-weight="700" fill="{c["muted"]}">{gname}</text>'
        px = 118
        for item in items:
            w = 18 + len(item) * 7.1
            rows += (f'<rect x="{px:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{c["card2"]}" stroke="{c["border"]}"/>'
                     f'<text x="{px + w / 2:.0f}" y="{y + 17.5}" text-anchor="middle" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{escape(item)}</text>')
            px += w + 7
    body = (f'<rect x="0.5" y="0.5" width="899" height="295" rx="14" fill="{c["card"]}" stroke="{c["border"]}"/>'
            f'<text x="24" y="34" font-family="{SANS}" font-size="16" font-weight="700" fill="{c["text"]}">Repositories by main language</text>'
            f'<rect x="24" y="50" width="{bar_w}" height="14" rx="7" fill="{c["empty"]}"/>'
            f'<clipPath id="barclip"><rect x="24" y="50" width="{bar_w}" height="14" rx="7"/></clipPath>'
            f'<g clip-path="url(#barclip)">{bars}</g>{legend}{rows}')
    return svg(900, 296, body, "Repositories by main language and toolbox")


for theme in THEMES:
    write("header", theme, header(theme))
    write("stats", theme, stats(theme))
    write("activity", theme, activity(theme))
    write("toolbox", theme, toolbox(theme))
    for p in PROJECTS:
        write(f"card-{p[0]}", theme, card(theme, p))
print("assets:", len(list(ASSETS.glob("*.svg"))))
