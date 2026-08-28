#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
騰域整合行銷 — 靜態網站建置腳本

用法：
    python3 build.py            產出整站到 dist/
    python3 build.py --serve    產出後開本機預覽 (http://localhost:8000)

新增一篇文章：在 content/posts/ 放一個 .md 檔，執行本腳本即可。
新增一個頁面：在 content/pages/ 放一個 .md 檔。
新增一個案例：在 content/cases/ 放一個 .md 檔。
sitemap.xml、feed.xml、文章列表、分類頁、分頁都會自動產生。
"""

import json, os, re, shutil, sys, datetime, html as htmllib
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PER_PAGE = 12

# ============================================================
# 全站設定 — 改這裡就會套用到每一頁
# ============================================================
SITE = {
    "name": "騰域整合行銷",
    "org": "騰域整合行銷有限公司",

    # ⚠ 這裡是全站 canonical、OG 標籤與 sitemap 的基準網址。
    #    已確認主要網域為「無 www」版本，請勿改回 www.tengyuim.com。
    #    結尾的斜線不要拿掉。
    "url": "https://tengyuim.com/",

    "root": "/",                      # 若放在子目錄，改成 "/子目錄/"
    "email": "wesley@tengyuim.com",
    "line": "https://lin.ee/U1ZY9dh",
    "address": "臺北市松山區八德路4段699號5樓之3",
    "year": datetime.date.today().year,
    "favicon": (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'"
        "%3E%3Crect width='200' height='200' fill='%230F2540'/%3E%3Ctext x='100' y='138' "
        "font-family='sans-serif' font-weight='900' font-size='120' fill='%23C49E54' "
        "text-anchor='middle'%3E%E9%A8%B0%3C/text%3E%3C/svg%3E"
    ),
    "nav": [
        {"label": "服務項目", "href": "services/",   "section": "services"},
        {"label": "產業經驗", "href": "industries/", "section": "industries"},
        {"label": "實績案例", "href": "cases/",      "section": "cases"},
        {"label": "服務方案", "href": "pricing/",    "section": "pricing"},
        {"label": "行銷文章", "href": "blog/",       "section": "blog"},
        {"label": "關於騰域", "href": "about/",      "section": "about"},
    ],
    "socials": [
        {"label": "官方 LINE", "href": "https://lin.ee/U1ZY9dh"},
        {"label": "Facebook",  "href": "https://www.facebook.com/profile.php?id=61563656686152"},
        {"label": "Instagram", "href": "https://www.instagram.com/tengyu_marketing/"},
    ],
    "ticker": [
        {"num": "18.94",  "label": "再行銷 ROAS 最高"},
        {"num": "NT$85",  "label": "房地產潛在客戶/位"},
        {"num": "16.89",  "label": "白色情人節 ROAS"},
        {"num": "4,128",  "label": "單活動開啟對話"},
        {"num": "NT$17",  "label": "度假屋訊息成本/次"},
        {"num": "42.6萬", "label": "單月觸及人數"},
    ],
    "services": [
        {"href": "services/meta-ads/", "tag": "META ADS", "title": "Meta 廣告代操",
         "desc": "Facebook 與 Instagram 廣告投放。受眾規劃、素材輪替、預算配置與成效優化，每月固定費用。"},
        {"href": "services/google-ads/", "tag": "GOOGLE ADS", "title": "Google 廣告代操",
         "desc": "關鍵字廣告、多媒體聯播網與 PMAX。從搜尋意圖出發，把預算花在有需求的人身上。"},
        {"href": "services/creative/", "tag": "CREATIVE", "title": "廣告素材製作",
         "desc": "圖文設計與廣告文案，每月固定產出篇數。素材不是做完就算，而是持續測試與汰換。"},
        {"href": "services/ai-workflow/", "tag": "AI", "title": "AI 導入與流程自動化",
         "desc": "AI Workflow、Notion 知識庫與自動化建置。把重複、耗時、易出錯的環節交給系統。"},
    ],
    "industries": [
        {"href": "industries/ecommerce/", "title": "電商・零售",
         "desc": "檔期操作、再行銷分層、會員成本控管。"},
        {"href": "industries/real-estate/", "title": "房地產・建案",
         "desc": "名單成本與品質並重的在地投放策略。"},
        {"href": "industries/medical/", "title": "醫療・診所",
         "desc": "在法規邊界內做出能過審又有效的素材。"},
        {"href": "industries/direct-sales/", "title": "直銷・保健",
         "desc": "對話導流、名單池累積與帳號風險控管。"},
    ],
    "plans": [
        {"name": "入門方案", "price": "15,000", "quota": "限額 4 組", "featured": False,
         "features": ["Meta 或 Google 擇一平台代操", "每月 5 篇靜態圖素材（含文案）",
                      "受眾設定與廣告策略規劃", "月報一份（成效數據分析）"]},
        {"name": "標準方案", "price": "25,000", "quota": "限額 4 組", "featured": True,
         "features": ["Meta + Google 雙平台代操", "每月 8 篇靜態圖素材（含文案）",
                      "A/B 素材測試與受眾輪替優化", "雙週報告＋優化建議", "受眾策略完整規劃"]},
        {"name": "旗艦方案", "price": "35,000", "quota": "限額 2 組", "featured": False,
         "features": ["Meta + Google 雙平台深度代操", "每月 10 篇靜態圖素材（含文案）",
                      "每週報告＋即時溝通優先處理", "完整受眾策略＋競品分析",
                      "季度行銷策略建議書", "適合房地產、醫療、直銷等高客單"]},
    ],
    "steps": [
        {"no": "01", "title": "填寫諮詢表單", "desc": "告訴我們你的產業、目標與預算，24 小時內回覆。"},
        {"no": "02", "title": "免費策略會議", "desc": "30 分鐘線上討論，分析你的狀況，提出初步廣告方向。"},
        {"no": "03", "title": "確認方案簽約", "desc": "選擇適合的方案，提供帳號權限，正式啟動。"},
        {"no": "04", "title": "素材製作＆上線", "desc": "完成首批素材並開始投放，後續你只需看報表。"},
    ],
    "form_industries": ["請選擇產業別", "電商 / 零售", "房地產 / 建案", "醫療 / 診所",
                        "直銷 / 保健", "餐飲 / 民宿", "已有數位基礎、想導入 AI", "其他"],
    "form_budgets": ["請選擇預算範圍", "每月 3 萬以下", "每月 3–10 萬",
                     "每月 10–30 萬", "每月 30 萬以上", "尚未確定"],
}

CATEGORIES = {
    "industry": {"name": "產業別行銷觀點", "href": "blog/industry/",
                 "desc": "電商、房地產、醫療、直銷——不同產業的廣告難點與實際打法。"},
    "ads":      {"name": "廣告知識教學", "href": "blog/ads/",
                 "desc": "受眾、素材、預算、報表。從實際操作中整理出來的做法與判斷依據。"},
    "ai":       {"name": "AI 導入與工具", "href": "blog/ai/",
                 "desc": "AI Workflow、知識庫與自動化，如何真正用在行銷與營運上。"},
}

# ============================================================
# 工具函式
# ============================================================
MD_EXT = ["tables", "attr_list", "fenced_code", "sane_lists", "md_in_html", "footnotes"]


def md2html(text):
    """轉成 HTML。內容來自本專案的 .md 檔（可信來源），故標記為安全。"""
    return Markup(markdown.markdown(text or "", extensions=MD_EXT, output_format="html5"))


def wrap_tables(html_str):
    """讓表格在手機上可橫向捲動。"""
    return Markup(re.sub(r"(<table>.*?</table>)", r'<div class="table-scroll">\1</div>',
                         str(html_str), flags=re.S))


def read_doc(path):
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    else:
        meta, body = {}, raw
    return meta, body.strip()


def read_minutes(text):
    chars = len(re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", text)))
    return max(1, round(chars / 450))


def fmt_date(d):
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d)
    return d, d.isoformat(), f"{d.year} 年 {d.month} 月 {d.day} 日"


def excerpt(meta, body, n=62):
    if meta.get("excerpt"):
        return meta["excerpt"]
    plain = re.sub(r"[#*`>\-\[\]()!]", "", body)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain[:n] + "…"


def build_crumbs(page):
    """依網址自動產生麵包屑。"""
    url = page["url"]
    if not url:
        return None
    parts = [p for p in url.strip("/").split("/") if p]
    crumbs = [{"label": "首頁", "href": ""}]
    known = {
        "services": ("服務項目", "services/"),
        "industries": ("產業經驗", "industries/"),
        "cases": ("實績案例", "cases/"),
        "blog": ("行銷文章", "blog/"),
        "pricing": ("服務方案", "pricing/"),
        "about": ("關於騰域", "about/"),
        "contact": ("免費諮詢", "contact/"),
        "privacy": ("隱私權政策", "privacy/"),
    }
    acc = ""
    for i, p in enumerate(parts):
        acc += p + "/"
        last = i == len(parts) - 1
        if last:
            crumbs.append({"label": page.get("crumb") or page["h1"], "href": acc})
        elif p in known:
            crumbs.append({"label": known[p][0], "href": known[p][1]})
        else:
            crumbs.append({"label": p, "href": acc})
    return crumbs


# ============================================================
# 結構化資料 (JSON-LD)
# ============================================================
ORG_ID = SITE["url"] + "#org"


def org_schema():
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": SITE["org"],
        "alternateName": ["騰域整合行銷", "TENGYU Marketing", "騰域"],
        "url": SITE["url"],
        "email": SITE["email"],
        "image": SITE["url"] + "og-image.jpg",
        "priceRange": "NT$15,000 - NT$35,000",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "八德路4段699號5樓之3",
            "addressLocality": "松山區",
            "addressRegion": "臺北市",
            "addressCountry": "TW",
        },
        "areaServed": {"@type": "Country", "name": "台灣"},
        "sameAs": [s["href"] for s in SITE["socials"]],
        "knowsAbout": ["Meta 廣告代操", "Google 廣告代操", "數位廣告投放", "廣告素材製作",
                       "受眾策略規劃", "AI Workflow 導入", "行銷自動化"],
    }


def breadcrumb_schema(crumbs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["label"],
             "item": SITE["url"] + c["href"]}
            for i, c in enumerate(crumbs)
        ],
    }


def faq_schema(faq):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faq
        ],
    }


def make_jsonld(page):
    graph = []
    layout = page.get("layout")

    if page["url"] == "":
        graph.append(org_schema())
        graph.append({
            "@type": "WebSite", "@id": SITE["url"] + "#website", "url": SITE["url"],
            "name": SITE["name"], "inLanguage": "zh-TW", "publisher": {"@id": ORG_ID},
        })
    else:
        graph.append({"@type": "Organization", "@id": ORG_ID, "name": SITE["org"], "url": SITE["url"]})

    if page.get("crumbs"):
        graph.append(breadcrumb_schema(page["crumbs"]))

    if layout == "post":
        graph.append({
            "@type": "BlogPosting",
            "@id": SITE["url"] + page["url"] + "#article",
            "headline": page["h1"],
            "description": page["description"],
            "datePublished": page["date"],
            "dateModified": page.get("updated") or page["date"],
            "articleSection": page["category_name"],
            "inLanguage": "zh-TW",
            "wordCount": page.get("word_count", 0),
            "author": {"@id": ORG_ID},
            "publisher": {"@id": ORG_ID},
            "mainEntityOfPage": SITE["url"] + page["url"],
        })

    if page.get("schema_type") == "Service":
        graph.append({
            "@type": "Service",
            "name": page.get("service_name") or page["h1"],
            "serviceType": page.get("service_name") or page["h1"],
            "provider": {"@id": ORG_ID},
            "areaServed": {"@type": "Country", "name": "台灣"},
            "description": page["description"],
        })

    if page.get("offers"):
        graph.append({
            "@type": "OfferCatalog", "name": "廣告代操服務方案",
            "itemListElement": [
                {"@type": "Offer", "name": o["name"], "price": o["price"],
                 "priceCurrency": "TWD", "description": o["desc"]}
                for o in page["offers"]
            ],
        })

    if page.get("faq"):
        graph.append(faq_schema(page["faq"]))

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


# ============================================================
# 建置
# ============================================================
env = Environment(
    loader=FileSystemLoader(ROOT / "templates"),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True, lstrip_blocks=True,
)


def write(url, html_str):
    out = DIST / url / "index.html" if url else DIST / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_str, encoding="utf-8")


def render(page, content_html, template=None):
    page.setdefault("layout", "page")
    if page.get("crumbs") is None and page["url"]:
        page["crumbs"] = build_crumbs(page)
    page["jsonld"] = Markup(make_jsonld(page))
    tpl = env.get_template(template or (page["layout"] + ".html"))
    inner = tpl.render(page=page, site=SITE, content=Markup(content_html))
    base = env.get_template("base.html")
    return base.render(page=page, site=SITE, content=Markup(inner))


def load_all(folder, default_layout):
    docs = []
    d = ROOT / "content" / folder
    if not d.exists():
        return docs
    for f in sorted(d.glob("*.md")):
        meta, body = read_doc(f)
        meta.setdefault("layout", default_layout)
        meta.setdefault("slug", f.stem)
        meta["_body"] = body
        docs.append(meta)
    return docs


def prep_faq(meta):
    for f in meta.get("faq") or []:
        f["a_html"] = md2html(f["a"])


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    all_urls = []

    def record(url, priority="0.7", changefreq="monthly", lastmod=None):
        all_urls.append({"loc": SITE["url"] + url, "priority": priority,
                         "changefreq": changefreq,
                         "lastmod": lastmod or datetime.date.today().isoformat()})

    # ---- 靜態資源 ----
    for f in (ROOT / "static").iterdir():
        if f.is_file():
            shutil.copy(f, DIST / f.name)

    # ---- 文章 ----
    posts = load_all("posts", "post")
    for p in posts:
        d, iso, disp = fmt_date(p["date"])
        p["_d"], p["date"], p["date_display"] = d, iso, disp
        p["url"] = f"blog/{p['slug']}/"
        p["category_name"] = CATEGORIES[p["category"]]["name"]

    # 排程發布：date 在未來的文章不會產出，時間到了重新建置就會自動上線。
    # 想預覽未來文章，執行 python3 build.py --preview
    today = datetime.date.today()
    preview = "--preview" in sys.argv
    scheduled = [p for p in posts if p["_d"] > today]
    all_posts = list(posts)
    if scheduled and not preview:
        posts = [p for p in posts if p["_d"] <= today]
    live_slugs = {p["slug"] for p in posts}

    posts.sort(key=lambda x: x["_d"], reverse=True)

    # ---- 案例 ----
    cases = load_all("cases", "page")
    for c in cases:
        c["url"] = f"cases/{c['slug']}/"

    # ---- 一般頁面 ----
    pages = load_all("pages", "page")
    for pg in pages:
        pg["url"] = pg.get("url", pg["slug"] + "/")
        if pg["url"] == "/":
            pg["url"] = ""

    # 供首頁與列表使用
    SITE["latest_posts"] = [
        {"href": p["url"], "title": p["h1"], "tag": p["category_name"],
         "desc": excerpt(p, p["_body"]), "date": p["date"], "date_display": p["date_display"]}
        for p in posts[:3]
    ]
    SITE["featured_cases"] = [
        {"href": c["url"], "industry": c["industry"], "metric": c["metric"],
         "unit": c["unit"], "metricLabel": c["metric_label"], "story": c["summary"]}
        for c in cases[:3]
    ]

    def link_of(ref):
        """把 slug 或路徑轉成卡片資料，供 related_links 使用。
        可接受：apparel-remarketing / cases/apparel-remarketing / cases/apparel-remarketing/
        """
        key = ref.strip("/")

        def hit(doc):
            return key in (doc["slug"], doc["url"].strip("/"))

        for p in posts:
            if hit(p):
                return {"href": p["url"], "title": p["h1"], "tag": p["category_name"],
                        "desc": excerpt(p, p["_body"], 48)}
        for c in cases:
            if hit(c):
                return {"href": c["url"], "title": c["h1"], "tag": c["industry"],
                        "desc": c["summary"][:46] + "…"}
        for pg in pages:
            if hit(pg):
                return {"href": pg["url"], "title": pg["h1"],
                        "tag": (pg.get("eyebrow", "").split("·")[-1].strip() or "騰域"),
                        "desc": (pg.get("lead") or pg["description"])[:46] + "…"}
        raise SystemExit(f"✗ related 找不到：{ref}\n  請確認 slug 是否正確（不含副檔名）")

    def resolve_related(meta):
        """展開延伸閱讀。指向尚未發布（排程中）的文章會自動略過，不會產生死連結。"""
        if not meta.get("related"):
            return
        links = []
        for ref in meta["related"]:
            key = ref.strip("/")
            pending = next((p for p in all_posts
                            if key in (p["slug"], p["url"].strip("/"))
                            and p["slug"] not in live_slugs), None)
            if pending:
                continue
            links.append(link_of(ref))
        meta["related_links"] = links

    # ---- 產出：一般頁面 ----
    for pg in pages:
        prep_faq(pg)
        resolve_related(pg)
        body = pg["_body"].replace("{{root}}", SITE["root"])
        content = wrap_tables(md2html(body))
        write(pg["url"], render(pg, content, pg.get("template")))
        record(pg["url"], "1.0" if pg["url"] == "" else "0.8",
               "weekly" if pg["url"] == "" else "monthly")

    # ---- 產出：案例 ----
    for c in cases:
        prep_faq(c)
        resolve_related(c)
        body = c["_body"].replace("{{root}}", SITE["root"])
        content = wrap_tables(md2html(body))
        write(c["url"], render(c, content))
        record(c["url"], "0.8")

    # ---- 產出：文章 ----
    for p in posts:
        prep_faq(p)
        resolve_related(p)
        body = p["_body"].replace("{{root}}", SITE["root"])
        content = wrap_tables(md2html(body))
        p["read_min"] = read_minutes(body)
        p["word_count"] = len(re.sub(r"\s+", "", body))
        write(p["url"], render(p, content))
        record(p["url"], "0.7", "yearly", p["date"])

    # ---- 產出：文章列表 + 分頁 ----
    def post_card(p):
        return {"href": p["url"], "title": p["h1"], "tag": p["category_name"],
                "desc": excerpt(p, p["_body"]), "date": p["date"],
                "date_display": p["date_display"]}

    filters = [{"label": "全部文章", "href": "blog/", "active": False}] + [
        {"label": v["name"], "href": v["href"], "active": False} for v in CATEGORIES.values()
    ]

    def build_list(items, base_url, meta, intro=None, active_href=None):
        total = max(1, -(-len(items) // PER_PAGE))
        for n in range(1, total + 1):
            chunk = items[(n - 1) * PER_PAGE: n * PER_PAGE]
            url = base_url if n == 1 else f"{base_url}page/{n}/"
            pg = dict(meta)
            pg["url"] = url
            pg["layout"] = "list"
            pg["entries"] = [post_card(i) for i in chunk]
            pg["page_num"], pg["pages_total"], pg["pager_base"] = n, total, base_url
            pg["intro_html"] = md2html(intro) if intro and n == 1 else None
            pg["filters"] = [dict(f, active=(f["href"] == active_href)) for f in filters]
            if n > 1:
                pg["title"] = f'{meta["title"]}（第 {n} 頁）'
                # 分頁的麵包屑要手動給，否則會產生指向 /blog/page/ 的死連結
                pg["crumbs"] = [{"label": "首頁", "href": ""}]
                if base_url != "blog/":
                    pg["crumbs"].append({"label": "行銷文章", "href": "blog/"})
                pg["crumbs"].append({"label": f'{meta["crumb"]}（第 {n} 頁）', "href": url})
            write(url, render(pg, ""))
            record(url, "0.6", "weekly")

    build_list(posts, "blog/", {
        "title": "行銷文章｜廣告投放、產業觀點與 AI 導入｜騰域整合行銷",
        "description": "騰域整合行銷的實戰文章：Meta 與 Google 廣告投放做法、電商房產醫療等產業別行銷觀點，以及企業 AI 導入的實際應用。",
        "h1": "行銷文章", "eyebrow": "INSIGHTS · 行銷觀點", "section": "blog",
        "crumb": "行銷文章",
        "lead": "我們把實際操盤過程中整理出來的判斷依據寫下來。都是真的做過、有數據支撐的內容，不是通用教科書。",
    }, intro=None, active_href="blog/")

    for key, cat in CATEGORIES.items():
        sub = [p for p in posts if p["category"] == key]
        build_list(sub, cat["href"], {
            "title": f'{cat["name"]}｜騰域整合行銷',
            "description": cat["desc"],
            "h1": cat["name"], "eyebrow": "CATEGORY · 文章分類", "section": "blog",
            "crumb": cat["name"],
            "lead": cat["desc"],
        }, intro=cat.get("intro"), active_href=cat["href"])

    # ---- 產出：案例列表 ----
    case_items = [{"href": c["url"], "title": c["h1"], "tag": c["industry"],
                   "desc": c["summary"]} for c in cases]
    pg = {
        "title": "實績案例｜真實廣告後台數據拆解｜騰域整合行銷",
        "description": "電商 ROAS 18.94、建案名單成本 NT$85、直銷 4,128 則對話——六個真實案例的產業背景、操作邏輯與成效數據完整拆解。",
        "h1": "實績案例", "eyebrow": "SELECTED WORK · 實績案例", "section": "cases",
        "url": "cases/", "layout": "list", "crumb": "實績案例",
        "lead": "每一個案例都附上產業背景、遇到的問題與實際做法。數據皆為真實廣告後台成果。",
        "entries": case_items, "page_num": 1, "pages_total": 1, "pager_base": "cases/",
    }
    write("cases/", render(pg, ""))
    record("cases/", "0.9", "monthly")

    # ---- robots.txt ----
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}sitemap.xml\n", encoding="utf-8")

    # ---- sitemap.xml ----
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in all_urls:
        lines += ["  <url>", f'    <loc>{u["loc"]}</loc>',
                  f'    <lastmod>{u["lastmod"]}</lastmod>',
                  f'    <changefreq>{u["changefreq"]}</changefreq>',
                  f'    <priority>{u["priority"]}</priority>', "  </url>"]
    lines.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")

    # ---- feed.xml (RSS) ----
    def esc(s):
        return htmllib.escape(s, quote=True)

    items = []
    for p in posts[:20]:
        pub = datetime.datetime.combine(p["_d"], datetime.time(9, 0))
        items.append(
            f"    <item>\n      <title>{esc(p['h1'])}</title>\n"
            f"      <link>{SITE['url']}{p['url']}</link>\n"
            f"      <guid isPermaLink=\"true\">{SITE['url']}{p['url']}</guid>\n"
            f"      <description>{esc(p['description'])}</description>\n"
            f"      <category>{esc(p['category_name'])}</category>\n"
            f"      <pubDate>{pub.strftime('%a, %d %b %Y %H:%M:%S +0800')}</pubDate>\n"
            f"    </item>")
    (DIST / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        f'    <title>{esc(SITE["name"])} 行銷文章</title>\n'
        f'    <link>{SITE["url"]}blog/</link>\n'
        '    <description>廣告投放、產業別行銷觀點與 AI 導入的實戰內容。</description>\n'
        '    <language>zh-TW</language>\n' + "\n".join(items) +
        "\n</channel></rss>\n", encoding="utf-8")

    # ---- 404 ----
    pg404 = {"title": "找不到這個頁面｜騰域整合行銷", "description": "您要找的頁面不存在或已移動。",
             "h1": "找不到這個頁面", "url": "404", "noindex": True, "crumbs": False,
             "eyebrow": "404 NOT FOUND",
             "lead": "您要找的頁面不存在，或是網址已經變更。以下是幾個常用的入口。"}
    body404 = md2html(
        "- [回到首頁](%s)\n- [服務項目](%sservices/)\n- [實績案例](%scases/)\n"
        "- [行銷文章](%sblog/)\n- [免費諮詢](%scontact/)"
        % tuple([SITE["root"]] * 5))
    (DIST / "404.html").write_text(render(pg404, body404), encoding="utf-8")

    # ---- 統計 ----
    n_html = len(list(DIST.rglob("index.html"))) + 1
    print(f"✓ 建置完成 → {DIST}")
    print(f"  頁面 {n_html} 個（文章 {len(posts)}、案例 {len(cases)}、一般頁 {len(pages)}）")
    print(f"  sitemap 收錄 {len(all_urls)} 個網址")
    if scheduled:
        if preview:
            print(f"  ⚠ 預覽模式：已包含 {len(scheduled)} 篇未來排程文章，此版本請勿上傳")
        else:
            print(f"  ⏳ 排程中 {len(scheduled)} 篇，尚未產出：")
            for p in sorted(scheduled, key=lambda x: x["_d"]):
                print(f"       {p['date']}  {p['h1'][:34]}")
    print(f"  下一步：把 dist/ 裡的全部內容上傳到主機根目錄")


if __name__ == "__main__":
    main()
    if "--serve" in sys.argv:
        os.chdir(DIST)
        import http.server, socketserver
        print("  預覽：http://localhost:8000  (Ctrl+C 結束)")
        socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler).serve_forever()
