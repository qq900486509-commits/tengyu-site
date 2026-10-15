# 騰域整合行銷 — 網站建置系統

一套從 Markdown 產生整站靜態 HTML 的工具。改一次共用版型，全站一起更新；新增文章只要寫一個 `.md` 檔。

---

## 快速開始

### 第一次使用（安裝環境）

需要 Python 3.9 以上。開啟終端機，切換到本資料夾後執行：

```bash
pip install markdown pyyaml jinja2
```

只需要做一次。

### 每次要更新網站時

```bash
python3 build.py
```

產出的完整網站會在 `dist/` 資料夾。

**如果已經接上 Netlify + GitHub**（見 `Netlify自動發布設定.md`），你不需要在本機執行這個指令——推送 `.md` 檔上 GitHub，Netlify 會自己建置。本機建置只是拿來預覽用。

### 上傳前先在本機預覽

```bash
python3 build.py --serve
```

然後開瀏覽器到 `http://localhost:8000`。確認沒問題再上傳。按 Ctrl+C 結束。

---

## 資料夾說明

```
tengyu-site/
├─ build.py              建置腳本（全站設定也在這裡面）
├─ templates/            共用版型 ← 改這裡會影響全站
│   ├─ base.html             head、導覽列、頁尾、麵包屑
│   ├─ home.html             首頁專用版型
│   ├─ page.html             一般頁面版型
│   ├─ post.html             文章版型
│   ├─ list.html             列表頁版型（文章列表、分類、案例）
│   ├─ contact.html          聯絡頁版型（含表單）
│   └─ cta.html              共用的行動呼籲區塊
├─ static/
│   └─ style.css             全站樣式 ← 改配色、字級都在這裡
├─ content/               內容 ← 平常只會動這裡
│   ├─ pages/                一般頁面（首頁、服務、產業、方案…）
│   ├─ posts/                文章
│   └─ cases/                實績案例
└─ dist/                  ← 產出，整包上傳到主機
```

---

## 新增一篇文章

在 `content/posts/` 建立一個新的 `.md` 檔，檔名就是網址。例如 `content/posts/meta-creative-testing.md` 會產生 `https://tengyuim.com/blog/meta-creative-testing/`。

檔案格式：

```markdown
---
date: 2026-09-01
category: ads
title: "廣告素材該測幾組才夠？A/B 測試的實際做法｜騰域"
description: "這段會出現在 Google 搜尋結果的標題底下，控制在 80 字內，要包含關鍵字並說清楚這篇解決什麼問題。"
keywords: "A/B 測試,廣告素材,素材測試"
h1: "廣告素材該測幾組才夠？A/B 測試的實際做法"
lead: "文章開頭那段導言，兩三句話講清楚這篇要解決什麼問題。"
excerpt: "顯示在文章列表卡片上的簡短摘要，不寫的話會自動從內文擷取。"
related:
  - cases/villa-booking
  - services/creative
  - report-metrics-that-matter
---

## 第一個小標

正文從這裡開始。用一般的 Markdown 語法就好。

表格、清單、粗體、連結都支援：

| 欄位 | 說明 |
| --- | --- |
| 內容 | 會自動加上手機橫向捲動 |

站內連結要用 `{{root}}` 開頭，例如 [免費諮詢]({{root}}contact/)。
```

### 欄位說明

| 欄位 | 必填 | 說明 |
| --- | :---: | --- |
| `date` | ✓ | 發布日期，格式 `YYYY-MM-DD`。列表會依此排序 |
| `category` | ✓ | 只能是 `industry`、`ads`、`ai` 三者之一 |
| `title` | ✓ | 瀏覽器分頁與搜尋結果的標題，**控制在 30 字內** |
| `description` | ✓ | 搜尋結果的描述，**控制在 80 字內** |
| `h1` | ✓ | 頁面上顯示的大標，可與 title 不同 |
| `keywords` | | 關鍵字，逗號分隔 |
| `lead` | | 標題下方的導言 |
| `excerpt` | | 列表卡片的摘要，省略則自動擷取 |
| `related` | | 延伸閱讀，填其他文章的檔名或路徑 |

寫好之後執行 `python3 build.py`，**文章列表、分類頁、分頁、sitemap、RSS 全部會自動更新**，不用手動改任何地方。

---

## 新增一個實績案例

在 `content/cases/` 建立 `.md` 檔，格式類似，但多幾個欄位：

```markdown
---
title: "案例標題｜騰域整合行銷"
description: "搜尋結果描述"
h1: "頁面大標"
eyebrow: "CASE 07 · 產業名"
crumb: "麵包屑顯示的短名稱"
industry: "產業別"        # 卡片上的標籤
metric: "12.5"            # 卡片上的大數字
unit: "ROAS"              # 數字後面的單位
metric_label: "這個數字代表什麼"
summary: "卡片上的一句話說明"
lead: "標題下方導言"
related:
  - services/meta-ads
---
```

**注意**：首頁「精選案例」區塊會自動顯示最前面三個案例（依檔名排序）。想換首頁展示哪三個，改檔名的字母順序即可。

---

## 新增一個一般頁面

在 `content/pages/` 建立 `.md` 檔：

```markdown
---
url: "services/new-service/"   # 網址，結尾一定要有斜線
section: services              # 導覽列高亮用
title: "頁面標題"
description: "搜尋結果描述"
h1: "頁面大標"
eyebrow: "SECTION · 分類"
crumb: "麵包屑短名"
lead: "導言"
schema_type: Service           # 選填，服務頁用
service_name: "服務名稱"
faq:                           # 選填，會自動產生 FAQ 結構化資料
  - q: "問題"
    a: "答案，可以用 **Markdown**。"
related:
  - pricing
---
```

---

## 排程發布（先寫好，時間到自動上線）

文章的 `date` 如果填**未來的日期**，建置時不會產出，等到那天之後重新建置才會出現。

所以你可以一次寫好四篇，日期排成每週一：

```
date: 2026-09-07   ← 下週一
date: 2026-09-14
date: 2026-09-21
date: 2026-09-28
```

執行 `python3 build.py` 會告訴你哪些還在排程中：

```
✓ 建置完成 → dist
  頁面 30 個（文章 3、案例 6、一般頁 15）
  ⏳ 排程中 3 篇，尚未產出：
       2026-09-14  廣告素材該測幾組才夠
       2026-09-21  Google PMAX 到底該怎麼餵資料
       2026-09-28  用 Notion 建立行銷知識庫
```

想預覽還沒到期的文章長什麼樣：

```bash
python3 build.py --preview
```

**注意：預覽模式產出的版本不要上傳**，它會把未來文章一起放上去。

排程中的文章如果被其他文章的 `related` 引用，會自動跳過，不會產生死連結。

### 完全自動化（Netlify）

網站託管在 Netlify 的話，可以做到完全不用碰終端機：

1. 專案放上 GitHub，Netlify 連結該 repo
2. 之後你在 GitHub 新增或修改 `.md` 檔，**Netlify 會自動建置並上線**
3. 再設一個 Build hook + GitHub Actions 排程，讓未來日期的文章時間到了自動出現

完整步驟見 **`Netlify自動發布設定.md`**。

### 但先說清楚：定時發布對 SEO 沒有加分

Google 不會因為你「規律地每週發一篇」而給你加分。它在意的是內容品質與相關性。

每週一篇這個節奏的意義是**對人的**——它是一個能長期維持的工作量。如果你一個週末寫得出四篇，一次全部發出去，SEO 上不會比較差。

所以排程功能是給你「寫作與發布可以分開」的彈性，不是為了討好演算法。不要為了維持節奏而發品質不好的文章，那反而有害。

---

## 常見修改

### 改導覽列 / 頁尾連結

編輯 `build.py` 最上方的 `SITE` 設定，找到 `"nav"` 那一段。頁尾的分類連結在 `templates/base.html`。

### 改配色

編輯 `static/style.css` 最上方的 `:root` 區塊。所有顏色都定義在那裡，改一個值全站一起變。

```css
:root{
  --navy:#1B3A5C;      /* 主色 */
  --gold:#C49E54;      /* 強調色 */
  --cream:#F7F4EE;     /* 背景 */
}
```

### 改首頁的數據跑馬燈

`build.py` 裡的 `SITE["ticker"]`。

### 改方案內容與價格

`build.py` 裡的 `SITE["plans"]`。同時記得改 `content/pages/pricing.md` 裡的比較表格與 `offers` 欄位（後者是給 Google 看的結構化資料）。

### 改網域

`build.py` 裡的 `SITE["url"]`。sitemap、canonical、OG 標籤會一起更新。

⚠ **目前已設為 `https://tengyuim.com/`（無 www），這是你 Netlify 的 Primary domain，請勿改回 www 版本。** 填錯會讓 canonical 指向一個會被轉址的網址，是 SEO 上不必要的訊號混亂。

---

## 每次上傳後要做的事

1. 開網站，按 `Ctrl+U` 檢視原始碼，確認中文內容看得到
2. 只有新增文章時：到 Search Console 用「網址審查」→「要求建立索引」

**Sitemap 只需要在第一次提交一次**，之後 Google 會自己定期回來抓。

---

## 疑難排解

**執行時出現 `ModuleNotFoundError`**
沒安裝套件，執行 `pip install markdown pyyaml jinja2`。

**出現「✗ related 找不到：xxx」**
某個檔案的 `related` 填了不存在的 slug。檢查拼字，或確認那個檔案真的存在。

**網頁樣式跑掉**
確認 `style.css` 有一起上傳到根目錄。這個檔案在 `dist/style.css`。

**改了東西但網站沒變**
先確認有重新執行 `python3 build.py`，再確認上傳的是 `dist/` 裡的檔案。瀏覽器快取的話按 `Ctrl+Shift+R` 強制重整。

**文章沒出現在列表上**
檢查 `date` 格式是不是 `YYYY-MM-DD`，以及 `category` 是不是 `industry`／`ads`／`ai` 三者之一。

---

## 廣告追蹤（GA4 / Meta 像素 / Google Ads）

### 怎麼啟用

打開 `build.py`，找到 `SITE` 設定裡的 `analytics` 區塊，把四個值填上：

```python
"analytics": {
    "ga4_id": "G-XXXXXXXXXX",
    "meta_pixel_id": "1234567890123456",
    "google_ads_id": "AW-XXXXXXXXX",
    "google_ads_lead_label": "AbC-D_efGhIjKlMnO",
},
```

**留空是安全的**——該平台的追蹤碼完全不會輸出，不會有半套的程式碼跑在線上。
可以只填其中一兩個，先上線 GA4 再補廣告平台。

`google_ads_id` 和 `google_ads_lead_label` 要**一起填**，少一個就不會送出轉換。

### 各個 ID 在哪裡拿

| 項目 | 位置 |
| --- | --- |
| GA4 評估 ID | GA4 → 管理 → 資料串流 → 你的網站串流 → 右上角 |
| Meta 像素 ID | 事件管理工具 → 資料來源 → 你的像素 → 名稱下方 |
| Google Ads 轉換 ID 與標籤 | Google Ads → 目標 → 轉換 → 點進轉換動作 → 標記設定 |

### 會追蹤哪些事件

| 觸發時機 | GA4 事件 | Meta 事件 | 計入 Google Ads 轉換 |
| --- | --- | --- | --- |
| 每個頁面載入 | `page_view`（自動） | `PageView` | — |
| 表單送出成功（到達 `/thanks/`） | `generate_lead` | `Lead` | ✅ |
| 開始填寫表單 | `form_start` | — | — |
| 點擊 LINE 連結 | `contact_line_click` | `Contact` | ✅ |
| 點擊 Email 連結 | `contact_email_click` | `Contact` | ✅ |

`form_start` 用來診斷漏斗：如果開始填的人很多但 `generate_lead` 很少，
代表表單本身有問題（欄位太多、某個欄位卡住），不是流量品質的問題。

### 轉換為什麼綁在感謝頁

表單送出成功後，Netlify 會把訪客導到 `/thanks/`。
那一頁的 `<body>` 帶有 `data-conversion="lead"`，載入時才送出轉換事件。

這表示**只有真正送出成功的才算轉換**，不是「按了送出按鈕」。
廣告平台的演算法會拿這個訊號去優化，訊號準確與否直接決定投放品質。

`/thanks/` 設為 `noindex` 且不列入 sitemap，不會被 Google 收錄。

### 怎麼驗證有沒有生效

填好 ID 並部署之後：

1. **GA4** —— 報表 → 即時。自己開一次網站，看有沒有出現在即時人數裡
2. **Meta 像素** —— 裝 Chrome 擴充功能 Meta Pixel Helper，開網站看有沒有亮起來
3. **Google Ads** —— 目標 → 轉換，狀態會從「未驗證」變成「正在記錄轉換」（需要等幾小時到一天）
4. **完整流程** —— 自己填一次表單送出，確認：
   - 有跳到 `/thanks/`
   - Netlify 後台 → Forms 看得到那筆資料
   - 信箱有收到通知（要先在 Netlify 設定通知，見下方）
   - GA4 即時報表的事件裡出現 `generate_lead`

### Netlify Forms 的設定

表單會自動被 Netlify 偵測，但**通知信要自己開**：

Netlify → Project configuration → **Forms** → Form notifications →
**Add notification** → Email notification → 填 wesley@tengyuim.com

免費方案每月 100 筆。超過會停止接收，所以如果量變大要注意。

收到的名單在 Netlify → **Forms** 可以看到，也能匯出 CSV。

---

## ⚠ 這個 repo 必須維持 public

**不要把 repo 改成 private。**

Netlify 免費方案的 private repo 只允許一位 Git 貢獻者，而且檢查的是
**commit 的作者**，不是誰觸發建置。作者對不上就直接封鎖：

```
Build blocked: Unrecognized Git contributor.
This plan allows only verified account members to push to private repos
```

2026-10-15 曾經改成 private，結果連續四次建置失敗，包含手動
Trigger deploy 也一樣被擋，最後改回 public 才恢復。

### 為什麼 public 沒關係

這個 repo 裡沒有任何機密：

| 內容 | 說明 |
| --- | --- |
| 文章 Markdown | 本來就公開在網站上 |
| `build.py`、`templates/` | 建置邏輯，無祕密 |
| 追蹤 ID（GA4／Pixel／Ads） | 看網頁原始碼就有 |
| `netlify.toml` | 無祕密 |
| `.github/workflows/publish.yml` | Build hook 存在 GitHub Secrets，不在 repo 裡 |

唯一真正的祕密是 Netlify Build Hook 網址，它存在 GitHub Secrets，
不會進版控。

### 真的需要 private 的話

要嘛升級 Netlify Pro，要嘛確保所有 commit 的作者都是已綁定的
Netlify 帳號成員（在 Netlify 的 manage Git contributors 設定）。
