# 🌐 GeneralPedia.com

> **The Complete All-in-One Encyclopedia & Everyday Knowledge Hub**

GeneralPedia is an automated web platform and autonomous publishing engine designed to build and rank a high-authority encyclopedia website. It analyzes high-volume, low-difficulty keywords, groups them into semantic/LSI clusters, publishes comprehensive articles across 8 silo categories, and logs publishing data to Google Sheets in real-time.

---

## 🏛️ 8 Core Silo Categories

1. **How-To & Guides** (`/how-to/`): Step-by-step solutions, everyday answers, and how-to tutorials.
2. **Finance & Money** (`/finance/`): Tax brackets (2025–2026), retirement plans (Roth IRA, 401k), insurance, and loans.
3. **Health & Wellness** (`/health/`): Verified medical symptoms, home remedies, wellness tips, and dietary health.
4. **Calculators & Tools** (`/tools/`): Financial calculators, metric/volume converters, and printable calendars.
5. **Automotive** (`/automotive/`): Used car purchasing advice, repairs, maintenance, and vehicle comparisons.
6. **Tech & Digital** (`/tech/`): Software guides, cybersecurity concepts (malware, algorithms), and tech tips.
7. **Home & Lifestyle** (`/lifestyle/`): Pet care, home maintenance (dryer vent cleaning), recipes, and food guides.
8. **Entertainment & Culture** (`/culture/`): Major global tournaments (Olympics, World Cup), cinema, and pop culture.

---

## 🚀 Key Features

- **Autonomous Content Engine (`auto_publisher.py`)**: Selects keyword clusters, generates long-form SEO articles with FAQ schema, tags, and meta descriptions.
- **Semantic / LSI Keywords Weaving**: Prevents keyword cannibalization by grouping related searches into single comprehensive pillar posts.
- **Real-Time Google Sheets Sync (`sheet_sync.py`)**: Automatically logs `Keywords`, `Category`, `Tags`, `Status`, `Post Url`, and `Post Date / Time` to your Google Sheet.
- **Modern Responsive Web Application (`site/`)**: Tailwind CSS powered UI with instant live search, category filtering, and an automated publishing control panel.

---

## 🛠️ Quick Start

### 1. Run the Web Server
```bash
python server.py
```
Open `http://localhost:8080` in your web browser.

### 2. Trigger Auto-Publishing
Run a single auto-publish job from terminal:
```bash
python auto_publisher.py
```
Or click **"Auto-Publish Next"** directly from the website header!

---

## 📊 Google Sheets Integration
To link directly with your live Google Sheet:
1. Open your Google Sheet.
2. Navigate to **Extensions > Apps Script**.
3. Paste the contents of `google_apps_script.js` and click **Deploy as Web App**.
4. Set the Webhook URL in `config.py` or as the `GENERALPEDIA_SHEET_WEBHOOK` environment variable.

---

© 2026 GeneralPedia. Autonomous Content System.
