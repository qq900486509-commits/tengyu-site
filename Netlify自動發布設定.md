# Netlify 自動發布設定步驟

你的網站在 Netlify，這比 FTP 好處理很多——Netlify 本來就會**自己建置**，不需要你在電腦上跑指令，也不需要上傳檔案。

設定完成後的日常流程：**寫一個 `.md` 檔推上 GitHub，網站兩分鐘後自動更新。**

預計花費：約 25 分鐘。

---

## 網域設定（已完成，供你確認）

你的 Netlify 主要網域是 **`https://tengyuim.com`（沒有 www）**，我已經把 `build.py` 設定成這個值：

```python
"url": "https://tengyuim.com/",
```

全站 31 頁的 canonical 標籤、Open Graph 標籤與 sitemap 都已重新產生成無 www 版本。**這一項不需要你再動。**

順便建議到 Netlify → **Domain management** 確認一下 `www.tengyuim.com` 有設定成轉址到主網域（Netlify 通常會自動處理）。這樣兩種寫法的網址都能正確導向同一個地方。

---

## 步驟一：建立 GitHub Repository

Netlify 需要從 Git 讀取你的專案。

1. 到 [github.com](https://github.com) 註冊帳號（免費）
2. 右上角 `+` → **New repository**
3. Repository name 填 `tengyu-site`
4. 選 **Private**
5. 按 **Create repository**

---

## 步驟二：把專案上傳到 GitHub

1. 在剛建立的 repo 頁面，點 **uploading an existing file**
2. 把 `tengyu-site.zip` 解壓後**資料夾裡面的所有東西**拖進去
   （是資料夾裡面的內容，不是整個資料夾）
3. 下方填 Commit message，例如 `初始版本`
4. 按 **Commit changes**

上傳完應該要看到：`build.py`、`netlify.toml`、`requirements.txt`、`README.md`、`templates/`、`content/`、`static/`。

> **`.github` 資料夾沒出現？** 網頁上傳會略過以點開頭的資料夾。解法在最下面的疑難排解。這個資料夾只影響「排程文章自動上線」，不影響一般發布，可以之後再補。

**不要上傳 `dist/` 資料夾**，Netlify 會自己產生。

---

## 步驟三：把 Netlify 接上 GitHub

這一步會把你現在的網站，從「手動上傳檔案」改成「從 Git 自動建置」。

1. Netlify 後台 → 你的網站 → **Site configuration** → **Build & deploy**
2. 找到 **Continuous deployment** 區塊 → **Link repository**
   （如果你現在是拖曳部署的，這裡會顯示 manual deploys）
3. 選 **GitHub**，授權後選擇 `tengyu-site`
4. 建置設定的欄位應該會自動從 `netlify.toml` 讀取。確認一下：

| 欄位 | 值 |
| --- | --- |
| Branch to deploy | `main` |
| Build command | `pip install -r requirements.txt && python3 build.py` |
| Publish directory | `dist` |

5. 按 **Deploy**

第一次建置大約一到兩分鐘。到 **Deploys** 分頁可以看即時進度。

**看到 Published** = 成功，打開網站就是新版了。

---

## 步驟四：設定排程建置（讓未來文章自動上線）

前面三步做完，你**推送檔案時網站就會自動更新**。但排程文章需要多一個設定。

### 為什麼需要

Netlify 只在你「推送程式碼」時建置。但排程文章是靠「日期到了」才要出現，那時候沒有推送動作，所以需要一個定時器去戳它。

### 設定方式

**1. 在 Netlify 建立 Build hook**

- Netlify → **Site configuration** → **Build & deploy** → **Build hooks**
- 按 **Add build hook**
- 名稱填「每週排程發布」，Branch 選 `main`
- 建立後會給你一組網址，長得像 `https://api.netlify.com/build_hooks/xxxxx`
- **複製起來**

**2. 在 GitHub 存進 Secret**

- GitHub repo → **Settings** → **Secrets and variables** → **Actions**
- **New repository secret**
- Name 填 `NETLIFY_BUILD_HOOK`
- Secret 貼上剛剛複製的網址
- 按 **Add secret**

完成。之後每週一早上 9 點，GitHub 會自動戳 Netlify 重新建置，該上線的文章就會出現。

---

## 完成之後的日常流程

### 發一篇文章

1. GitHub repo → `content/posts/` → **Add file** → **Create new file**
2. 檔名填 `文章網址.md`（英文小寫、連字號分隔）
3. 貼上文章內容
4. **Commit changes**

**兩分鐘後網站自動更新。** 完全不用碰終端機。

### 排程未來的文章

文章的 `date` 填未來日期就好：

```yaml
date: 2026-11-02
```

推上去之後不會馬上出現，會等到 11/2 之後的那個週一自動上線。

### 改配色、改文案

一樣在 GitHub 上編輯對應的檔案，Commit 之後自動重新建置。

---

## 幾個 Netlify 的額外好處

接上 Git 之後你會多拿到這些，不用額外設定：

**每次部署都有預覽網址。** Deploys 分頁裡每筆記錄都有獨立網址，可以先看過再確認。

**一鍵回滾。** 改壞了的話，到 Deploys 找到之前正常的版本，按 **Publish deploy** 就還原了。

**建置失敗不會影響線上版本。** 如果某次建置出錯，Netlify 會保留原本正常的版本，不會讓網站掛掉。

**自動 HTTPS 與 CDN。** 這個你應該已經有了。

---

## 疑難排解

### `.github` 資料夾沒出現

網頁上傳會略過以點開頭的資料夾。手動補上：

1. repo 頁面 → **Add file** → **Create new file**
2. 檔名欄位輸入：`.github/workflows/publish.yml`
   （直接打斜線，GitHub 會自動建立資料夾）
3. 貼上 `publish.yml` 的內容 → Commit

### 建置失敗，錯誤訊息提到 `python` 或 `pip`

到 Netlify → **Site configuration** → **Environment variables**，確認有一項：

```
PYTHON_VERSION = 3.12
```

`netlify.toml` 裡已經設定了，但如果 Netlify 沒讀到，在後台手動加一次。

### 建置失敗，錯誤訊息提到 `related 找不到`

某篇文章的 `related` 欄位填了不存在的檔名。錯誤訊息會直接告訴你是哪一個，改掉拼字就好。

**這個設計是刻意的**——寧可建置失敗，也不要讓死連結上線。線上版本不會受影響。

### 網站更新了但看到舊的

按 `Ctrl+Shift+R` 強制重整。`netlify.toml` 裡已經把 HTML 設成不快取，正常情況下不會有這個問題。

### 想暫停每週的排程建置

編輯 `.github/workflows/publish.yml`，把 `schedule:` 那兩行前面加 `#` 註解掉。

---

## 如果你不想用 GitHub

Netlify 也支援直接拖曳資料夾部署（你現在可能就是這樣）。那樣的話：

1. 在自己電腦上跑 `python3 build.py`
2. 把 `dist/` 資料夾拖到 Netlify 的部署區

缺點是每次都要手動做，而且排程文章要你記得在對的日期重跑一次。

**如果你確定不想碰 GitHub，跟我說，我可以改成另一種做法**：把所有文章都建置出來但用日期控制顯示。不過那個方案在 SEO 上有缺點（Google 可能提早索引到還沒正式發布的頁面），所以我不建議，除非你真的不想用 Git。
