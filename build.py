#!/usr/bin/env python3
"""בונה את אתר "בונים עתיד" מקבצי הטקסט שבתיקייה content/.

כל פרק נכתב בקובץ content/<מספר>.txt בפורמט של וואטסאפ:
  *טקסט*  = מודגש. שורה שכולה מודגשת = כותרת ביניים.
  _טקסט_  = נטוי. שורה שכולה נטויה = הערה קטנה.
  שורה שמתחילה ב-👇 = תיבת "השורה התחתונה".
  שורה ריקה = פסקה חדשה.

הרצה:  python3 build.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
GROUP_URL = "https://chat.whatsapp.com/K5WcsUNhc2CIY9REkp1zK6?s=cl&p=a&mlu=4&ilr=4&iam=0"
PHONE_DISPLAY = "054-670-2312"
PHONE_WA = "https://wa.me/972546702312"

# published=True: הפרק מופיע באתר ויש לו דף. False: מופיע ברשימה כ"בקרוב".
SERIES = [
    {
        "num": 1,
        "title": "למה כמעט חובה להשקיע",
        "lead": "כסף שיושב בעו״ש לא שומר על הערך שלו. לאן הוא הולך, ומה הזמן יכול לעשות לו.",
        "chapters": [
            {"slug": "1-1", "title": "הכסף בעו״ש מתכווץ, ומי מרוויח מזה", "published": True},
            {"slug": "1-2", "title": "אפקט הזמן: הנכס החשוב ביותר שלכם הוא השנים", "published": True},
        ],
    },
    {
        "num": 2,
        "title": "אפיקי השקעה",
        "lead": "מה בעצם קונים כשמשקיעים: מזומן, אג״ח, מניות, ומדדים שמחזיקים את כל השוק.",
        "chapters": [
            {"slug": "2-1", "title": "מה בעצם קונים כשמשקיעים?", "published": True},
            {"slug": "2-2", "title": "מדדים: איך קונים את כל השוק בקנייה אחת", "published": True},
        ],
    },
    {
        "num": 3,
        "title": "מכשירי השקעה",
        "lead": "בנק, קופת גמל או חשבון מסחר עצמאי: דרך מי קונים, וכמה זה עולה לכם.",
        "chapters": [
            {"slug": "3-1", "title": "איפה משקיעים את הכסף? קופת גמל מול מסחר עצמאי", "published": True},
        ],
    },
    {
        "num": 4,
        "title": "בניית אסטרטגיה לטווח ארוך",
        "lead": "כמה מניות, כמה אג״ח, ואיך מחלקים בין ארה״ב, ישראל והעולם.",
        "chapters": [
            {"slug": "4-1", "title": "איזה משקיע אתם?", "published": False},
            {"slug": "4-2", "title": "תיקים לדוגמה: אגרסיבי, מאוזן ושמרני", "published": False},
            {"slug": "4-3", "title": "השיטה, ומה עושים כשהשוק נופל", "published": False},
        ],
    },
    {
        "num": 5,
        "title": "איך משקיעים בפועל",
        "lead": "צעד אחר צעד, עם סרטונים: פותחים חשבון, מפקידים וקונים.",
        "chapters": [
            {"slug": "5-1", "title": "פותחים חשבון בבית השקעות", "published": False},
            {"slug": "5-2", "title": "מפקידים ומגדירים הוראת קבע", "published": False},
            {"slug": "5-3", "title": "מוצאים קרן וקונים", "published": False},
        ],
    },
]

LOGO = (
    '<svg class="logo" viewBox="0 0 100 100" aria-hidden="true">'
    '<path d="M28 12 H72 C84 12 92 20 92 32 V54 C92 66 84 74 72 74 H44 C40 74 36.5 75.5 33.5 78.5 L23 89 C21.5 90.5 19 89.2 19.6 87.2 L22.5 76.5 C13.5 73.5 8 65 8 54 V32 C8 20 16 12 28 12 Z" fill="#2E8B66"/>'
    '<path d="M48.5 63 C47 55 48.5 49 52.5 44 C55 41 56.3 38.5 56.5 35.5" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round" fill="none"/>'
    '<path d="M38 64.5 Q50 60.5 62 64.5" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round" fill="none"/>'
    '<path d="M49.6 52.5 C44 52.5 36.5 50 32.6 42.5 C30.8 39 30.4 35.5 31.2 32.6 C38 32.4 44.6 35.6 47.9 42 C49.4 45 49.9 48.6 49.6 52.5 Z" fill="#FFFFFF"/>'
    '<path d="M56.4 36.4 C56 30.2 58.8 24.4 64.6 21.2 C67.8 19.5 71.4 18.9 74.2 19.4 C74.7 24.2 73.2 29.2 69.2 32.6 C65.6 35.6 61 36.8 56.4 36.4 Z" fill="#E3A23B"/>'
    "</svg>"
)

DISCLOSURE = (
    "התוכן באתר הוא מידע כללי ולימודי בלבד. הוא אינו ייעוץ השקעות, שיווק השקעות או ייעוץ פנסיוני, "
    "ואינו תחליף לייעוץ המתחשב בנתונים ובצרכים של כל אדם. אינני בעל רישיון לפי חוק הסדרת העיסוק "
    "בייעוץ השקעות, בשיווק השקעות ובניהול תיקי השקעות, התשנ\"ה-1995. כל החלטת השקעה היא באחריות "
    "המשקיע בלבד. תשואות עבר אינן מבטיחות תשואות עתידיות."
)


# ---------- המרת טקסט וואטסאפ ל-HTML ----------

def inline(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w/])_(.+?)_(?![\w/])", r"<em>\1</em>", t)
    return t


def is_whole(line: str, ch: str) -> bool:
    s = line.strip()
    return len(s) > 2 and s.startswith(ch) and s.endswith(ch) and s.count(ch) == 2


def heading_text(line: str) -> str | None:
    """מחזיר כותרת אם השורה כולה מודגשת (מותר אמוג'י לפני ההדגשה)."""
    s = line.strip()
    m = re.fullmatch(r"([^\w*]{0,4}\s*)?\*([^*]+)\*", s)
    if m:
        return (m.group(1) or "").strip() + (" " if m.group(1) and m.group(1).strip() else "") + m.group(2)
    return None


def render(text: str) -> str:
    blocks, out = [], []
    cur: list[str] = []
    for line in text.strip().splitlines():
        if line.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line.rstrip())
    if cur:
        blocks.append(cur)

    for bi, block in enumerate(blocks):
        para: list[str] = []

        def flush():
            if para:
                out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
                para.clear()

        for line in block:
            s = line.strip()
            if s.startswith("👇"):
                flush()
                out.append('<p class="bottom">' + inline(s.lstrip("👇").strip()) + "</p>")
            elif is_whole(s, "_"):
                flush()
                out.append('<p class="note">' + inline(s.strip("_")) + "</p>")
            elif bi == 0 and block.index(line) == 0 and heading_text(s) is not None:
                flush()
                out.append('<p class="lead">' + html.escape(heading_text(s), quote=False) + "</p>")
            elif heading_text(s) is not None and not s.startswith(("📉", "📈", "🔥", "📌", "🏛️", "📊")):
                flush()
                out.append("<h2>" + html.escape(heading_text(s), quote=False) + "</h2>")
            else:
                para.append(s)
        flush()
    return "\n".join(out)


# ---------- תבניות ----------

def page(title: str, desc: str, body: str, depth: int) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<link rel="icon" href="{up}assets/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rubik:wght@500;700;800&family=Assistant:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="{up}index.html">{LOGO}<span><b>בונים עתיד</b><small>השקעות וצמיחה עם אבישי חניא</small></span></a>
    <nav><a href="{up}index.html#series">כל הפרקים</a><a class="join" href="{html.escape(GROUP_URL)}">הצטרפות לקבוצה</a></nav>
  </div>
</header>
{body}
<footer class="site">
  <div class="wrap">
    <p><b>גילוי נאות:</b> {DISCLOSURE}</p>
    <p>שאלות? אפשר לכתוב לי בוואטסאפ: <a href="{PHONE_WA}">{PHONE_DISPLAY}</a></p>
    <p>בונים עתיד | השקעות וצמיחה עם אבישי חניא</p>
  </div>
</footer>
</body>
</html>
"""


def cta() -> str:
    return f"""<section class="cta">
  <h3>רוצים לקבל את הפרקים הבאים?</h3>
  <p>בקבוצה יש סיכום שווקים בכל מוצאי שבת, ופרקים חדשים במהלך השבוע.</p>
  <div class="btns">
    <a class="btn p" href="{html.escape(GROUP_URL)}">להצטרפות לקבוצה</a>
    <a class="btn s" href="{PHONE_WA}">לשאלות בפרטי</a>
  </div>
</section>"""


def build():
    published = [(s, c) for s in SERIES for c in s["chapters"] if c["published"]]
    (ROOT / "posts").mkdir(exist_ok=True)

    for i, (s, c) in enumerate(published):
        src = ROOT / "content" / f"{c['slug']}.txt"
        content = render(src.read_text(encoding="utf-8"))
        idx = [x["slug"] for x in s["chapters"]].index(c["slug"]) + 1
        total = len(s["chapters"])
        prev = published[i - 1] if i > 0 else None
        nxt = published[i + 1] if i + 1 < len(published) else None
        nav = '<nav class="chap">'
        if prev:
            nav += f'<a class="prev" href="{prev[1]["slug"]}.html"><span>הפרק הקודם</span><b>{html.escape(prev[1]["title"])}</b></a>'
        if nxt:
            nav += f'<a class="next" href="{nxt[1]["slug"]}.html"><span>הפרק הבא</span><b>{html.escape(nxt[1]["title"])}</b></a>'
        nav += "</nav>"
        body = f"""<section class="hero">
  <div class="wrap">
    <div class="series">סדרה {s['num']}: {html.escape(s['title'])} · פרק {idx} מתוך {total}</div>
    <h1>{html.escape(c['title'])}</h1>
  </div>
</section>
<main class="wrap article">
{content}
{nav}
{cta()}
</main>"""
        (ROOT / "posts" / f"{c['slug']}.html").write_text(
            page(f"{c['title']} | בונים עתיד", s["lead"], body, 1), encoding="utf-8")

    # דף הבית
    cards = []
    for s in SERIES:
        items = []
        for k, c in enumerate(s["chapters"], 1):
            label = f"{s['num']}.{k}"
            if c["published"]:
                items.append(f'<li><a href="posts/{c["slug"]}.html"><span class="n">{label}</span>{html.escape(c["title"])}<span class="tag pub">לקריאה</span></a></li>')
            else:
                items.append(f'<li class="soon"><span class="n">{label}</span>{html.escape(c["title"])}<span class="tag">בקרוב</span></li>')
        cards.append(f"""<article class="series-card" id="s{s['num']}">
  <div class="sh"><div class="num">{s['num']}</div><div><h2>{html.escape(s['title'])}</h2><p>{html.escape(s['lead'])}</p></div></div>
  <ul>{''.join(items)}</ul>
</article>""")

    first = published[0][1]["slug"] if published else "1-1"
    home = f"""<section class="hero home">
  <div class="wrap">
    <h1>שוק ההון, בגובה העיניים</h1>
    <p class="dek">מדריך למתחילים, מ"למה בכלל להשקיע" ועד "איך עושים את זה בפועל". בלי ז׳רגון, בלי הבטחות, עם הרבה מספרים אמיתיים.</p>
    <div class="btns">
      <a class="btn p" href="posts/{first}.html">להתחיל מהפרק הראשון</a>
      <a class="btn s" href="{html.escape(GROUP_URL)}">להצטרפות לקבוצה</a>
    </div>
  </div>
</section>
<main class="wrap">
  <section class="about">
    <h2>מי אני</h2>
    <p>אני אבישי חניא, משקיע כעשר שנים בשוק ההון, בעיקר במדדים ולטווח ארוך. הקמתי את "בונים עתיד" כדי להנגיש לזוגות צעירים ולמתחילים את מה שלמדתי: איך לגרום לכסף לעבוד, בלי לחפש קיצורי דרך.</p>
  </section>
  <section id="series" class="series-list">
    <h2>הסדרות</h2>
    {''.join(cards)}
  </section>
  {cta()}
</main>"""
    (ROOT / "index.html").write_text(
        page("בונים עתיד | השקעות וצמיחה עם אבישי חניא",
             "מדריך השקעות למתחילים בגובה העיניים: למה להשקיע, במה, דרך מי, ואיך בפועל.", home, 0),
        encoding="utf-8")
    print(f"נבנו {len(published)} פרקים ודף בית.")


if __name__ == "__main__":
    build()
