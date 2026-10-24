"""Draws the profile header and the "one slip of paper" receipt in the style of beratarpa.com.

Fonts (Inter Tight, Inter, IBM Plex Mono; SIL Open Font License) are subset woff2 files in
./fonts and are embedded into each SVG, so GitHub shows the same type as the site.
Numbers come from ./data (refreshed by fetch_data.py); the date is the day the Action ran.
"""
import base64
import json
import os
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(os.environ.get("PROFILE_ROOT", Path(__file__).parent))
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
FONTS = ROOT / "fonts"

# beratarpa.com tokens
SITE = {
    "dark": dict(bg="#07080b", line="rgba(255,255,255,.07)", tx="#f3f4f6", mu="#a0a6b0", pill="rgba(255,255,255,.04)",
                 pill_line="rgba(255,255,255,.14)", glow_a=0.55, glow_b=0.45),
    "light": dict(bg="#f6f8fb", line="rgba(10,37,64,.07)", tx="#0a2540", mu="#4b5b70", pill="#ffffff",
                  pill_line="#e2e7ee", glow_a=0.22, glow_b=0.18),
}
A1, A2, A3, A4, OK = "#ff5b35", "#ff9a3c", "#b05cff", "#4f7cff", "#3ddc84"

TEXT = {
    "en": dict(
        pill="Open to new projects",
        h1=[[("End-to-end", True), (" software development", False)], [("for businesses.", False)]],
        sub=["Web, mobile and desktop applications; system and device integrations.",
             "I have worked at 5 companies since 2020, and some of the systems I built are still in daily use."],
        receipt_title="Software developer",
        rows_meta=[("Date", None), ("Time", None), ("Location", "Ankara · UTC+3")],
        rows=[("Companies", "companies"), ("Live products", "live_products"), ("Open-source repos", "public_repos"),
              ("GitHub stars", "stars"), ("Published packages", "packages")],
        total="TOTAL", days="days", since="since 2020",
        footer=["I also wrote the software", "that prints this slip."],
    ),
    "tr": dict(
        pill="Yeni projelere açık",
        h1=[[("İşletmeler için ", False), ("uçtan uca", True)], [("yazılım geliştiriyorum.", False)]],
        sub=["Web, mobil ve masaüstü uygulamalar; sistem ve cihaz entegrasyonları.",
             "2020'den bu yana 5 şirkette çalıştım, geliştirdiğim sistemlerin bir kısmı bugün hâlâ her gün kullanılıyor."],
        receipt_title="Yazılım geliştirici",
        rows_meta=[("Tarih", None), ("Saat", None), ("Yer", "Ankara · UTC+3")],
        rows=[("Çalıştığım şirket", "companies"), ("Canlı ürün", "live_products"), ("Açık kaynak proje", "public_repos"),
              ("GitHub yıldızı", "stars"), ("Yayınlanan paket", "packages")],
        total="TOPLAM", days="gün", since="2020'den bugüne",
        footer=["Bu fişi basan yazılımı", "da ben yazdım."],
    ),
}

CAREER_START = date(2020, 9, 1)  # first day as an intern


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2');}}"


HERO_FONTS = "".join([
    font_face("Inter Tight", "intertight-600.woff2", 600),
    font_face("Inter", "inter-400.woff2", 400),
    font_face("Inter", "inter-500.woff2", 500),
])
RECEIPT_FONTS = "".join([
    font_face("Plex Mono", "plexmono-400.woff2", 400),
    font_face("Plex Mono", "plexmono-500.woff2", 500),
])
HEAD = "'Inter Tight', Inter, 'Segoe UI', sans-serif"
BODY = "Inter, 'Segoe UI', sans-serif"
MONO = "'Plex Mono', Consolas, monospace"


def svg(w, h, body, title, fonts):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><style>{fonts}</style>{body}</svg>')


def load(name, default):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def numbers():
    summary, static = load("summary.json", {}), load("static.json", {})
    return {
        "companies": static.get("companies", 5),
        "live_products": static.get("live_products", 6),
        "public_repos": summary.get("public_repos", 44),
        "stars": summary.get("stars", 159),
        "packages": static.get("packages", 4),
    }


# ---- header ---------------------------------------------------------------------------
def hero(lang, theme):
    c, t = SITE[theme], TEXT[lang]
    W, H = 900, 340
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{c["line"]}"/>' for x in range(60, W, 60)) + \
           "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{c["line"]}"/>' for y in range(60, H, 60))
    h1 = ""
    for i, line in enumerate(t["h1"]):
        spans = "".join(f'<tspan fill="{"url(#grad)" if g else c["tx"]}">{escape(s)}</tspan>' for s, g in line)
        h1 += f'<text x="48" y="{150 + i * 54}" font-family="{HEAD}" font-weight="600" font-size="48" letter-spacing="-1.4">{spans}</text>'
    sub = "".join(f'<text x="48" y="{270 + i * 24}" font-family="{BODY}" font-size="16" fill="{c["mu"]}">{escape(s)}</text>'
                  for i, s in enumerate(t["sub"]))
    pill_w = 44 + len(t["pill"]) * 7.4
    body = (
        f'<defs>'
        f'<linearGradient id="grad" x1="0" x2="1" y1="0" y2="0" gradientTransform="rotate(10)">'
        f'<stop offset="0" stop-color="{A1}"/><stop offset=".32" stop-color="{A2}"/><stop offset=".68" stop-color="{A3}"/><stop offset="1" stop-color="{A4}"/></linearGradient>'
        f'<radialGradient id="g1"><stop offset="0" stop-color="{A1}" stop-opacity="{c["glow_a"]}"/><stop offset="1" stop-color="{A1}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="g2"><stop offset="0" stop-color="{A3}" stop-opacity="{c["glow_b"]}"/><stop offset="1" stop-color="{A3}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="logo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{A1}"/><stop offset=".5" stop-color="{A3}"/><stop offset="1" stop-color="{A4}"/></linearGradient>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
        f'</defs>'
        f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="{c["bg"]}"/>{grid}'
        f'<ellipse cx="700" cy="40" rx="320" ry="220" fill="url(#g1)">'
        f'<animateTransform attributeName="transform" type="translate" dur="18s" repeatCount="indefinite" values="0 0;-60 30;0 0"/></ellipse>'
        f'<ellipse cx="560" cy="330" rx="300" ry="200" fill="url(#g2)">'
        f'<animateTransform attributeName="transform" type="translate" dur="22s" repeatCount="indefinite" values="0 0;50 -25;0 0"/></ellipse>'
        f'</g>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{c["pill_line"]}"/>'
        # brand mark, as in the site's nav
        f'<rect x="48" y="34" width="26" height="26" rx="7" fill="url(#logo)"/>'
        f'<text x="61" y="52" text-anchor="middle" font-family="{HEAD}" font-weight="600" font-size="11" fill="#fff">BA</text>'
        f'<text x="84" y="52" font-family="{HEAD}" font-weight="600" font-size="15" fill="{c["tx"]}">Berat ARPA</text>'
        # "open to new projects" pill
        f'<g transform="translate({W - 48 - pill_w:.0f},30)"><rect width="{pill_w:.0f}" height="32" rx="16" fill="{c["pill"]}" stroke="{c["pill_line"]}"/>'
        f'<circle cx="18" cy="16" r="4" fill="{OK}"><animate attributeName="opacity" dur="2.4s" repeatCount="indefinite" values="1;.35;1"/></circle>'
        f'<text x="30" y="21" font-family="{BODY}" font-weight="500" font-size="13" fill="{c["mu"]}">{escape(t["pill"])}</text></g>'
        f'{h1}{sub}'
    )
    return svg(W, H, body, f'Berat ARPA. {"".join(s for line in t["h1"] for s, _ in line)}', HERO_FONTS)


# ---- receipt ----------------------------------------------------------------------------
def receipt_parts(lang, now):
    t, n = TEXT[lang], numbers()
    W = 340
    PW, PX = 276, 32  # paper width / x
    ink, faint, paper = "#1c1c1c", "#8a8a8a", "#fbfaf6"
    y = 42
    parts = []

    def center(text, size=12.5, weight=400, spacing=0, color=ink):
        nonlocal y
        parts.append(f'<text x="{PX + PW / 2}" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="{size}" '
                     f'font-weight="{weight}" letter-spacing="{spacing}" fill="{color}">{escape(text)}</text>')

    def rule():
        nonlocal y
        parts.append(f'<line x1="{PX + 18}" y1="{y}" x2="{PX + PW - 18}" y2="{y}" stroke="{ink}" stroke-dasharray="2 3" stroke-width="1"/>')

    def row(left, right, size=11.5, weight=400):
        nonlocal y
        lw = len(left) * size * 0.6
        rw = len(right) * size * 0.6
        parts.append(f'<text x="{PX + 18}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{ink}">{escape(left)}</text>'
                     f'<line x1="{PX + 22 + lw:.0f}" y1="{y - 1}" x2="{PX + PW - 22 - rw:.0f}" y2="{y - 1}" stroke="{faint}" stroke-dasharray="1 2.5"/>'
                     f'<text x="{PX + PW - 18}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{ink}">{escape(right)}</text>')

    center("BERAT ARPA", 14, 500, 2.5); y += 20
    center(t["receipt_title"], 11.5); y += 16
    rule(); y += 22
    meta_vals = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M")]
    for i, (label, val) in enumerate(t["rows_meta"]):
        row(label, val if val else meta_vals[i]); y += 18
    y += 2; rule(); y += 22
    for label, key in t["rows"]:
        row(label, f'{n[key]:,}'); y += 18
    y += 2; rule(); y += 28
    days = (now.date() - CAREER_START).days
    row(t["total"], f'{days:,} {t["days"]}', 14, 500); y += 18
    center(t["since"], 10.5, color="#555"); y += 18
    rule(); y += 22
    center("beratarpa@hotmail.com", 10.5); y += 16
    center("github.com/BeratARPA", 10.5); y += 22
    for line in t["footer"]:
        center(line, 10, color="#555"); y += 14
    center("beratarpa.com", 10.5, 500); y += 22
    paper_h = y
    zig = "".join(f" l{PW / 20 / 2:.1f} 6 l{PW / 20 / 2:.1f} -6" for _ in range(20))
    paper_path = f'M{PX} 6{zig} V{paper_h} H{PX} Z'

    printer_y = paper_h + 6
    H = printer_y + 92
    feed = 2.6  # seconds; prints once and stays
    body = (
        f'<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-opacity=".22"/></filter>'
        f'<linearGradient id="pr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1e25"/><stop offset="1" stop-color="#0b0d11"/></linearGradient>'
        f'<clipPath id="slot"><rect x="0" y="0" width="{W}" height="{printer_y + 12}"/></clipPath></defs>'
        f'<g clip-path="url(#slot)"><g>'
        f'<animateTransform attributeName="transform" type="translate" dur="{feed}s" fill="freeze" calcMode="spline" keySplines=".2 .7 .1 1" values="0 {paper_h};0 0"/>'
        f'<path d="{paper_path}" fill="{paper}" filter="url(#sh)"/>{"".join(parts)}</g></g>'
        f'<g filter="url(#sh)"><rect x="8" y="{printer_y}" width="{W - 16}" height="84" rx="14" fill="url(#pr)"/></g>'
        f'<rect x="24" y="{printer_y + 10}" width="{W - 48}" height="7" rx="3.5" fill="#000"/>'
        f'<text x="26" y="{printer_y + 66}" font-family="{MONO}" font-size="10" letter-spacing="1" fill="#5d6470">80MM</text>'
        f'<circle cx="{W - 28}" cy="{printer_y + 62}" r="3.5" fill="{OK}"><animate attributeName="opacity" dur="1.6s" repeatCount="indefinite" values="1;.35;1"/></circle>'
    )
    return body, W, H


def receipt(lang, now):
    body, W, H = receipt_parts(lang, now)
    return svg(W, H, body, "Berat ARPA on one slip of paper", RECEIPT_FONTS)


# ---- section panels in the site's style ------------------------------------------------
PANEL_FONTS = HERO_FONTS + font_face("Plex Mono", "plexmono-400.woff2", 400)

PANEL = {
    "dark": dict(bg="#0b0d12", card="#0f1117", line="rgba(255,255,255,.08)", line2="rgba(255,255,255,.15)",
                 tx="#f3f4f6", mu="#a0a6b0", mu2="#6c727c"),
    "light": dict(bg="#ffffff", card="#f6f8fb", line="#e2e7ee", line2="#d3dae4",
                  tx="#0a2540", mu="#4b5b70", mu2="#7a8796"),
}

SERVICES = {
    "en": ("Services", "What I do.", [
        ("Web applications and admin panels", "Orders, stock and reporting on one screen."),
        ("Mobile applications", "iOS and Android in one go."),
        ("Desktop software", "Sales and stock that keep working offline."),
        ("System integration", "Data flows from one place, entered once."),
        ("Device integration", "Fiscal registers, scanners, scales, printers."),
        ("Maintenance and modernisation", "I take over your system and move it forward."),
    ]),
    "tr": ("Hizmetler", "Ne yapıyorum.", [
        ("Web uygulamaları ve yönetim panelleri", "Sipariş, stok ve raporlama tek ekranda."),
        ("Mobil uygulamalar", "iOS ve Android tek seferde."),
        ("Masaüstü yazılımlar", "İnternet kesilse de çalışan satış ve stok."),
        ("Sistem entegrasyonları", "Veri tek yerden akar, bir kez girilir."),
        ("Cihaz entegrasyonları", "Yazarkasa, barkod okuyucu, terazi, fiş yazıcısı."),
        ("Bakım ve modernizasyon", "Sisteminizi devralır, ileri taşırım."),
    ]),
}

WORK = {
    "en": ("Work", "Work that runs in real businesses.", "Live · in daily use", [
        ("pos", "TZ Yazılım · desktop + web", "Point-of-sale and order system", "From order entry to the kitchen display", "and the end-of-day report.", "tek-cozum.com"),
        ("fiscal", "TZ Yazılım · device integration", "Fiscal register integration", "The legal receipt is issued the moment", "a sale ends. End-of-day report included.", "inside the POS"),
        ("qr", "TZ Yazılım · web", "QR menu system", "Customers order from the table.", "A new menu never needs reprinting.", "sefimqr.com"),
        ("orders", "LiwaSoft · Innovative Software", "Ordering platform integration", "Three ordering platforms, one central", "flow. No manual entry, no lost orders.", "pentegrasyon.net"),
        ("courier", "LiwaSoft · iOS + Android", "Courier mobile app", "Couriers see the order on the phone;", "head office sees the status instantly.", "Google Play · App Store"),
        ("hr", "EasyHR · enterprise platform · now", "AI-assisted HR platform", "Leave, payroll, recruitment and", "personnel records in one platform.", "easyhr.com.tr"),
    ]),
    "tr": ("İşler", "Gerçek işletmelerde çalışan işler.", "Yayında · her gün kullanılıyor", [
        ("pos", "TZ Yazılım · masaüstü + web", "Adisyon ve kasa sistemi", "Sipariş girişinden mutfak ekranına,", "gün sonu raporuna kadar tek sistem.", "tek-cozum.com"),
        ("fiscal", "TZ Yazılım · cihaz entegrasyonu", "Yazarkasa entegrasyonu", "Satış bittiği anda mali fiş kesilir,", "gün sonu raporu kendiliğinden hazırlanır.", "adisyonun içinde"),
        ("qr", "TZ Yazılım · web", "QR menü sistemi", "Müşteri masadan sipariş verir.", "Menü değişince yeniden baskı gerekmez.", "sefimqr.com"),
        ("orders", "LiwaSoft · Innovative Software", "Sipariş platformu entegrasyonu", "Üç sipariş platformu, tek merkezi akış.", "Elle giriş yok, kayıp sipariş yok.", "pentegrasyon.net"),
        ("courier", "LiwaSoft · iOS + Android", "Kurye mobil uygulaması", "Kurye siparişi telefonda görür,", "durum anında merkeze düşer.", "Google Play · App Store"),
        ("hr", "EasyHR · kurumsal platform · şu an", "Yapay zekâ destekli İK platformu", "İzin, bordro, işe alım ve özlük", "süreçleri tek platformda.", "easyhr.com.tr"),
    ]),
}

OPEN = {
    "en": dict(eyebrow="Open source", title="One engine, three ecosystems.",
               sub=["ARE runs the same business rules in desktop,", "web and mobile apps, from one API."],
               cols=[("Desktop", "C# · .NET", "NuGet"), ("Web", "JavaScript", "npm"), ("Mobile", "Dart", "pub.dev")],
               printer_eyebrow="Open source", printer_title="The tool behind the slip.",
               printer_sub=["HTML-Thermal-Printer prints HTML straight to receipt", "printers, with a preview and receipt-specific tags."],
               stars="stars", downloads="NuGet downloads"),
    "tr": dict(eyebrow="Açık kaynak", title="Aynı motor, üç ekosistem.",
               sub=["ARE aynı iş kurallarını masaüstü, web ve", "mobil uygulamalarda tek bir API ile çalıştırır."],
               cols=[("Masaüstü", "C# · .NET", "NuGet"), ("Web", "JavaScript", "npm"), ("Mobil", "Dart", "pub.dev")],
               printer_eyebrow="Açık kaynak", printer_title="Fişin arkasındaki araç.",
               printer_sub=["HTML-Thermal-Printer HTML içeriğini doğrudan fiş", "yazıcısına basar; önizleme yapar, fiş etiketlerini tanır."],
               stars="yıldız", downloads="NuGet indirme"),
}

CTA = {
    "en": ("Contact", "Let's talk about your project.", "One message is enough. I usually reply the same day.",
           ["beratarpa.com", "LinkedIn", "beratarpa@hotmail.com"]),
    "tr": ("İletişim", "Projenizi konuşalım.", "Bir mesaj yeterli. Genellikle aynı gün dönüyorum.",
           ["beratarpa.com", "LinkedIn", "beratarpa@hotmail.com"]),
}


def grad_defs():
    return (f'<linearGradient id="grad" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{A1}"/><stop offset=".32" stop-color="{A2}"/><stop offset=".68" stop-color="{A3}"/><stop offset="1" stop-color="{A4}"/></linearGradient>')


def frame(c, W, H):
    return (f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{c["bg"]}" stroke="{c["line2"]}"/>')


def heading(c, eyebrow, title, x=40, y=52):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="13" fill="{A1}">{escape(eyebrow)}</text>'
            f'<text x="{x}" y="{y + 40}" font-family="{HEAD}" font-weight="600" font-size="32" letter-spacing="-.8" fill="{c["tx"]}">{escape(title)}</text>')


def services(lang, theme):
    c = PANEL[theme]
    eyebrow, title, items = SERVICES[lang]
    W, H = 900, 500
    cw, ch, gx, gy, ox, oy = 402, 100, 16, 16, 40, 128
    cells = ""
    for i, (name, line) in enumerate(items):
        x = ox + (i % 2) * (cw + gx)
        y = oy + (i // 2) * (ch + gy)
        d = 0.08 * i
        cells += (f'<g opacity="0"><animate attributeName="opacity" begin="{d:.2f}s" dur=".5s" fill="freeze" values="0;1"/>'
                  f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="14" fill="{c["card"]}" stroke="{c["line"]}"/>'
                  f'<text x="{x + 20}" y="{y + 32}" font-family="{MONO}" font-size="13" fill="url(#grad)">{i + 1:02d}</text>'
                  f'<text x="{x + 20}" y="{y + 60}" font-family="{HEAD}" font-weight="600" font-size="17" fill="{c["tx"]}">{escape(name)}</text>'
                  f'<text x="{x + 20}" y="{y + 82}" font-family="{BODY}" font-size="13.5" fill="{c["mu"]}">{escape(line)}</text></g>')
    body = f'<defs>{grad_defs()}</defs>{frame(c, W, H)}{heading(c, eyebrow, title)}{cells}'
    return svg(W, H, body, f"{title} " + "; ".join(n for n, _ in items), PANEL_FONTS)


def work_header(lang, theme):
    c = PANEL[theme]
    eyebrow, title, live, _ = WORK[lang]
    W, H = 900, 120
    body = (f'<defs>{grad_defs()}</defs>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{c["bg"]}" stroke="{c["line2"]}"/>'
            f'{heading(c, eyebrow, title, 40, 46)}'
            f'<g transform="translate({W - 40 - (34 + len(live) * 7.2):.0f},62)"><rect width="{34 + len(live) * 7.2:.0f}" height="30" rx="15" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<circle cx="17" cy="15" r="4" fill="{OK}"><animate attributeName="opacity" dur="2.4s" repeatCount="indefinite" values="1;.35;1"/></circle>'
            f'<text x="29" y="20" font-family="{BODY}" font-weight="500" font-size="12.5" fill="{c["mu"]}">{escape(live)}</text></g>')
    return svg(W, H, body, title, PANEL_FONTS)


def work_card(lang, theme, item):
    c = PANEL[theme]
    key, meta, title, l1, l2, link = item
    W, H = 440, 200
    lw = 30 + len(link) * 7.2
    body = (f'<defs>{grad_defs()}</defs>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<rect x="24" y="0" width="56" height="3" rx="1.5" fill="url(#grad)"/>'
            f'<text x="24" y="38" font-family="{MONO}" font-size="11.5" fill="{c["mu2"]}">{escape(meta)}</text>'
            f'<text x="24" y="72" font-family="{HEAD}" font-weight="600" font-size="21" letter-spacing="-.4" fill="{c["tx"]}">{escape(title)}</text>'
            f'<text x="24" y="104" font-family="{BODY}" font-size="14" fill="{c["mu"]}">{escape(l1)}</text>'
            f'<text x="24" y="124" font-family="{BODY}" font-size="14" fill="{c["mu"]}">{escape(l2)}</text>'
            f'<g transform="translate(24,148)"><rect width="{lw:.0f}" height="30" rx="15" fill="none" stroke="{c["line2"]}"/>'
            f'<text x="14" y="20" font-family="{MONO}" font-size="12" fill="{c["tx"]}">{escape(link)} ↗</text></g>'
            f'<circle cx="{W - 28}" cy="34" r="4" fill="{OK}"><animate attributeName="opacity" dur="2.4s" repeatCount="indefinite" values="1;.35;1"/></circle>')
    return svg(W, H, body, f"{title}: {l1} {l2}", PANEL_FONTS)


def engine(lang, theme):
    c, t = PANEL[theme], OPEN[lang]
    W, H = 900, 300
    sub = "".join(f'<text x="40" y="{142 + i * 22}" font-family="{BODY}" font-size="15" fill="{c["mu"]}">{escape(s)}</text>' for i, s in enumerate(t["sub"]))
    hub_x, hub_y = 500, 150
    cols = ""
    for i, (name, lang_name, reg) in enumerate(t["cols"]):
        y = 46 + i * 76
        cols += (f'<path d="M{hub_x + 46} {hub_y} C {hub_x + 110} {hub_y}, {hub_x + 110} {y + 30}, 668 {y + 30}" fill="none" stroke="url(#grad)" stroke-width="1.6" stroke-dasharray="4 5">'
                 f'<animate attributeName="stroke-dashoffset" dur="1.6s" repeatCount="indefinite" values="18;0"/></path>'
                 f'<rect x="668" y="{y}" width="192" height="60" rx="12" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<text x="686" y="{y + 25}" font-family="{HEAD}" font-weight="600" font-size="15" fill="{c["tx"]}">{escape(name)}</text>'
                 f'<text x="686" y="{y + 45}" font-family="{MONO}" font-size="11.5" fill="{c["mu"]}">{escape(lang_name)}</text>'
                 f'<text x="844" y="{y + 25}" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="{A2}">{escape(reg)}</text>')
    hub = (f'<circle cx="{hub_x}" cy="{hub_y}" r="46" fill="{c["card"]}" stroke="url(#grad)" stroke-width="2"/>'
           f'<circle cx="{hub_x}" cy="{hub_y}" r="56" fill="none" stroke="{A3}" stroke-opacity=".25">'
           f'<animate attributeName="r" dur="3s" repeatCount="indefinite" values="48;62;48"/><animate attributeName="stroke-opacity" dur="3s" repeatCount="indefinite" values=".35;0;.35"/></circle>'
           f'<text x="{hub_x}" y="{hub_y + 8}" text-anchor="middle" font-family="{HEAD}" font-weight="600" font-size="24" fill="{c["tx"]}">ARE</text>')
    body = f'<defs>{grad_defs()}</defs>{frame(c, W, H)}{heading(c, t["eyebrow"], t["title"])}{sub}{cols}{hub}'
    return svg(W, H, body, f'{t["title"]} ARE: NuGet, npm, pub.dev', PANEL_FONTS)


def printer_card(lang, theme):
    c, t = PANEL[theme], OPEN[lang]
    s, p = load("summary.json", {}), load("packages.json", {})
    stars = s.get("repo_stars", {}).get("HTML-Thermal-Printer", 79)
    dl = p.get("nuget_printhtml", 1594)
    W, H = 900, 210
    sub = "".join(f'<text x="40" y="{132 + i * 22}" font-family="{BODY}" font-size="15" fill="{c["mu"]}">{escape(x)}</text>' for i, x in enumerate(t["printer_sub"]))
    stat = ""
    for i, (num, label) in enumerate([(f"★ {stars}", t["stars"]), (f"{dl:,}", t["downloads"])]):
        x = 610 + i * 140
        stat += (f'<text x="{x}" y="112" font-family="{HEAD}" font-weight="600" font-size="34" fill="url(#grad)">{escape(num)}</text>'
                 f'<text x="{x}" y="138" font-family="{MONO}" font-size="12" fill="{c["mu"]}">{escape(label)}</text>')
    body = (f'<defs>{grad_defs()}</defs>{frame(c, W, H)}{heading(c, t["printer_eyebrow"], t["printer_title"])}{sub}{stat}'
            f'<text x="610" y="176" font-family="{MONO}" font-size="12" fill="{c["mu2"]}">C# · WPF · PrintHTML.Core</text>')
    return svg(W, H, body, f'HTML-Thermal-Printer: {stars} stars, {dl} NuGet downloads', PANEL_FONTS)


def cta(lang, theme):
    c = SITE[theme]
    eyebrow, title, sub, chips = CTA[lang]
    W, H = 900, 230
    chip_svg, x = "", 48
    for i, label in enumerate(chips):
        w = 30 + len(label) * 7.6
        primary = i == 0
        chip_svg += (f'<g transform="translate({x:.0f},150)"><rect width="{w:.0f}" height="40" rx="20" '
                     f'fill="{"#ffffff" if primary else "none"}" stroke="{"#ffffff" if primary else c["pill_line"]}"/>'
                     f'<text x="{w / 2:.0f}" y="25" text-anchor="middle" font-family="{BODY}" font-weight="500" font-size="14" '
                     f'fill="{"#07080b" if primary else c["tx"]}">{escape(label)}{" →" if primary else ""}</text></g>')
        x += w + 10
    body = (f'<defs>{grad_defs()}'
            f'<radialGradient id="g1"><stop offset="0" stop-color="{A1}" stop-opacity="{c["glow_a"]}"/><stop offset="1" stop-color="{A1}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="g2"><stop offset="0" stop-color="{A4}" stop-opacity="{c["glow_b"]}"/><stop offset="1" stop-color="{A4}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="fr"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>'
            f'<g clip-path="url(#fr)"><rect width="{W}" height="{H}" fill="{c["bg"]}"/>'
            f'<ellipse cx="820" cy="40" rx="260" ry="170" fill="url(#g1)"><animateTransform attributeName="transform" type="translate" dur="16s" repeatCount="indefinite" values="0 0;-40 20;0 0"/></ellipse>'
            f'<ellipse cx="640" cy="240" rx="260" ry="150" fill="url(#g2)"/></g>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{c["pill_line"]}"/>'
            f'<text x="48" y="54" font-family="{MONO}" font-size="13" fill="{A1}">{escape(eyebrow)}</text>'
            f'<text x="48" y="96" font-family="{HEAD}" font-weight="600" font-size="34" letter-spacing="-.8" fill="{c["tx"]}">{escape(title)}</text>'
            f'<text x="48" y="126" font-family="{BODY}" font-size="15" fill="{c["mu"]}">{escape(sub)}</text>{chip_svg}')
    return svg(W, H, body, f"{title} {sub}", PANEL_FONTS)


SUMMARY = {
    "en": dict(role="Software developer · Ankara", eyebrow="Summary", title=["Everything about me on", "one slip of paper."],
               paras=["I started in software as an intern in 2020. Since then I have built systems of very different scales, from desktop software to enterprise platforms, from mobile apps to device integrations; some of them still run every day in real businesses.",
                      "Thinking about the technical side is my job. All you need to describe is what you want to achieve; we work out the rest together.",
                      "I own the work I take on. You have one point of contact from start to finish, I never hand it off, and I stand behind it after delivery."],
               companies="Companies I have worked at",
               note=["The slip is redrawn from my numbers every morning.", "I also wrote the tool that prints it on paper:"]),
    "tr": dict(role="Yazılım geliştirici · Ankara", eyebrow="Özet", title=["Kendimi tek bir", "fişe sığdırdım."],
               paras=["Yazılıma 2020'de stajyer olarak başladım. O günden beri masaüstü programlardan kurumsal platformlara, mobil uygulamalardan cihaz entegrasyonlarına kadar çok farklı ölçekte sistem geliştirdim; bir kısmı hâlâ her gün, gerçek işletmelerde çalışıyor.",
                      "Teknik tarafı düşünmek benim işim. Sizin anlatmanız gereken tek şey ne yapmak istediğiniz; gerisini birlikte netleştiririz.",
                      "Aldığım işin sahibi benim. Baştan sona tek muhatabınız olurum, işi kimseye devretmem; teslimden sonra da arkasındayım."],
               companies="Çalıştığım şirketler",
               note=["Fiş her sabah kendi rakamlarımdan yeniden çiziliyor.", "Onu kâğıda basan aracı da ben yazdım:"]),
}
COMPANIES = ["EasyHR", "LiwaSoft", "Innovative Software", "TZ Yazılım", "Aniventi"]


def wrap(text, limit):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def summary(lang, theme, now):
    """Left: photo, name, the site's summary text and companies. Right: the receipt."""
    c, t = PANEL[theme], SUMMARY[lang]
    rbody, rw, rh = receipt_parts(lang, now)
    W = 900
    H = max(rh + 56, 600)
    avatar = base64.b64encode((FONTS / "avatar.jpg").read_bytes()).decode()
    x0, y = 40, 54
    left = (f'<clipPath id="av"><circle cx="{x0 + 26}" cy="{y + 2}" r="26"/></clipPath>'
            f'<circle cx="{x0 + 26}" cy="{y + 2}" r="28" fill="none" stroke="url(#grad)" stroke-width="1.5"/>'
            f'<image href="data:image/jpeg;base64,{avatar}" x="{x0}" y="{y - 24}" width="52" height="52" clip-path="url(#av)"/>'
            f'<text x="{x0 + 68}" y="{y - 2}" font-family="{HEAD}" font-weight="600" font-size="16" fill="{c["tx"]}">Berat ARPA</text>'
            f'<text x="{x0 + 68}" y="{y + 18}" font-family="{BODY}" font-size="13" fill="{c["mu"]}">{escape(t["role"])}</text>')
    y += 66
    left += f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="13" fill="{A1}">{escape(t["eyebrow"])}</text>'
    y += 40
    for line in t["title"]:
        left += f'<text x="{x0}" y="{y}" font-family="{HEAD}" font-weight="600" font-size="31" letter-spacing="-.8" fill="{c["tx"]}">{escape(line)}</text>'
        y += 36
    y += 12
    for para in t["paras"]:
        for line in wrap(para, 56):
            left += f'<text x="{x0}" y="{y}" font-family="{BODY}" font-size="14.5" fill="{c["mu"]}">{escape(line)}</text>'
            y += 22
        y += 12
    y += 4
    left += f'<line x1="{x0}" y1="{y}" x2="{x0 + 440}" y2="{y}" stroke="{c["line2"]}"/>'
    y += 30
    left += f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="11.5" fill="{c["mu2"]}">{escape(t["companies"])}</text>'
    y += 26
    # Names joined with dots read evenly whatever the font measures; two lines keep them inside the column.
    for i, row_names in enumerate([COMPANIES[:3], COMPANIES[3:]]):
        spans = f'<tspan fill="{c["mu2"]}">  ·  </tspan>'.join(escape(n) for n in row_names)
        left += f'<text x="{x0}" y="{y + i * 24}" font-family="{HEAD}" font-weight="600" font-size="15" fill="{c["tx"]}" xml:space="preserve">{spans}</text>'
    y += 24
    y += 34
    for i, line in enumerate(t["note"]):
        left += f'<text x="{x0}" y="{y + i * 19}" font-family="{BODY}" font-size="12.5" fill="{c["mu2"]}">{escape(line)}</text>'
    y += 19 * len(t["note"])
    left += (f'<text x="{x0}" y="{y + 2}" font-family="{HEAD}" font-weight="600" font-size="14" fill="{c["tx"]}">HTML-Thermal-Printer '
             f'<tspan fill="url(#grad)">↗</tspan></text>')
    H = max(H, y + 40)
    body = (f'<defs>{grad_defs()}</defs>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{c["bg"]}" stroke="{c["line2"]}"/>'
            f'{left}<g transform="translate({W - rw - 34},{(H - rh) / 2:.0f})">{rbody}</g>')
    return svg(W, H, body, " ".join(t["title"]) + " " + " ".join(t["paras"]), PANEL_FONTS + RECEIPT_FONTS)


def main():
    now = datetime.now(timezone(timedelta(hours=3)))
    for lang in TEXT:
        (ASSETS / f"receipt-{lang}.svg").write_text(receipt(lang, now), encoding="utf-8")
        for theme in SITE:
            out = {
                f"hero-{lang}-{theme}": hero(lang, theme),
                f"summary-{lang}-{theme}": summary(lang, theme, now),
                f"services-{lang}-{theme}": services(lang, theme),
                f"work-{lang}-{theme}": work_header(lang, theme),
                f"engine-{lang}-{theme}": engine(lang, theme),
                f"printer-{lang}-{theme}": printer_card(lang, theme),
                f"cta-{lang}-{theme}": cta(lang, theme),
            }
            for item in WORK[lang][3]:
                out[f"work-{item[0]}-{lang}-{theme}"] = work_card(lang, theme, item)
            for name, content in out.items():
                (ASSETS / f"{name}.svg").write_text(content, encoding="utf-8")
    print("drawn", len(list(ASSETS.glob("*.svg"))), "svg files")


if __name__ == "__main__":
    main()
