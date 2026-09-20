<h1 align="center">📱 Flipkart Price Intelligence — Automated ETL & BI Pipeline</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=F5A623&center=true&vCenter=true&width=700&lines=Scrape+%E2%86%92+Clean+%E2%86%92+Engineer+%E2%86%92+Visualize;n8n+%2B+FastAPI+%2B+Selenium+%2B+Pandas+%2B+Power+BI;Async+Orchestration+%7C+Daily+Price+Snapshots" alt="Typing SVG" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-Async%20Orchestration-009688?logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/n8n-Workflow%20Automation-EA4B71?logo=n8n&logoColor=white">
  <img src="https://img.shields.io/badge/Selenium-Web%20Scraping-43B02A?logo=selenium&logoColor=white">
  <img src="https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?logo=pandas&logoColor=white">
  <img src="https://img.shields.io/badge/Power%20BI-Dashboarding-F2C811?logo=powerbi&logoColor=black">
  <img src="https://img.shields.io/badge/Status-Complete-success">
</p>

---

<div align="center">

## 🗺️ Table of Contents

<table>
  <tr>
    <td align="center">🎯<br><a href="#-project-overview"><b>Project Overview</b></a></td>
    <td align="center">❓<br><a href="#-the-business-question"><b>The Business Question</b></a></td>
    <td align="center">🏗️<br><a href="#-architecture"><b>Architecture</b></a></td>
  </tr>
  <tr>
    <td align="center">🔄<br><a href="#-the-process--how-this-came-together"><b>The Process</b></a></td>
    <td align="center">🧭<br><a href="#-methodology--stage-by-stage"><b>Methodology</b></a></td>
    <td align="center">💡<br><a href="#-key-insights"><b>Key Insights</b></a></td>
  </tr>
  <tr>
    <td align="center">🏢<br><a href="#-business-intelligence--future-outlook"><b>Business Outlook</b></a></td>
    <td align="center">⚠️<br><a href="#-honest-limitations"><b>Honest Limitations</b></a></td>
    <td align="center">🧠<br><a href="#-skills-applied"><b>Skills Applied</b></a></td>
  </tr>
  <tr>
    <td align="center">🚀<br><a href="#-about-me"><b>About Me</b></a></td>
    <td align="center">📫<br><a href="#-lets-connect"><b>Let's Connect</b></a></td>
    <td align="center">⭐<br><a href="#-lets-connect"><b>Support</b></a></td>
  </tr>
</table>

</div>

---

## 🎯 Project Overview

Most portfolio "web scraping" projects stop at pulling a table into a CSV. This one is built as an actual **automated intelligence platform** — a scheduled, self-orchestrating pipeline that scrapes live mobile phone listings from Flipkart, cleans and enriches them into a business-ready dataset, and surfaces the result as a multi-page Power BI dashboard, without a human needing to babysit any step of it.

The point wasn't to prove I could call `requests.get()`. It was to build the same *category* of system real retail and e-commerce analytics teams run — competitive price intelligence — using an actual orchestration layer (n8n), an async backend (FastAPI), a resilient scraper that survives anti-bot protection, and a cleaning layer that catches its own mistakes. That last part matters more than it sounds: partway through, I discovered the pipeline was silently misreading phone storage listed in MB as if it were GB — a data-quality bug that would have quietly corrupted every downstream number. Catching and fixing that is a bigger signal of analyst judgment than any chart in the dashboard.

---

## ❓ The Business Question

E-commerce prices aren't static — they move daily, sometimes hourly, driven by flash sales, exchange offers, and inventory pressure. A shopper, or a business tracking competitor pricing, can't answer basic questions from a single glance at Flipkart's website:

- Which phones are genuinely a good deal right now, versus just marked "off" from an inflated MRP?
- Which brands consistently under-price or over-price relative to their ratings?
- How does the market segment mix (budget vs. flagship) shift day to day?
- Is a given listing actually reliable (Flipkart Assured), well-reviewed, and worth the price?

**Business need:** turn a wall of unstructured product listings into a structured, trend-aware dataset that answers these questions on demand — refreshed automatically, not manually re-collected every time someone wants an answer.

---

## 🏗️ Architecture


Schedule Trigger ─┐
                   ├─▶ n8n Workflow ─▶ POST /run-etl (FastAPI) ─▶ 202 Accepted (task_id)
Manual Trigger ────┘                         │
                                              ▼
                                   Background Task (async)
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     ▼                        ▼                        ▼
              01_scrape_products      02_clean_data          03_feature_engineering
              (Selenium + Chrome)     (pandas cleaning)       (business logic columns)
                     │                        │                        │
                     └────────────────────────┴────────────────────────┘
                                              │
                                              ▼
                          n8n polls GET /etl-status/{task_id} on a loop
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                                ▼
                     SUCCESS → Email confirmation      FAILED → Email alert
                                              │
                                              ▼
                                   Power BI (5-page dashboard)


n8n never does the heavy lifting itself — it only triggers, waits, and reports. FastAPI accepts the request instantly and runs the real work in the background, so the caller is never blocked waiting on a multi-minute scrape. This is the same async pattern production data platforms use.

---

## 🔄 The Process — How This Came Together

### 🕸️ Scraping

Rather than trust a public API (most retail platforms gate real catalog access behind seller/affiliate programs, which I confirmed before ruling it out), I built a Selenium-based scraper that renders the live page like a real browser — necessary because a plain HTTP request was blocked outright. Every product's HTML container was identified by hand through DevTools, not guessed, and the scraper includes retry-friendly pacing (courtesy delays between pages, an auto-stop after repeated empty pages) so it behaves responsibly rather than hammering the site.

### 🧹 Cleaning

Raw scraped data is messy by nature: duplicate listings, missing ratings on basic phones, storage sometimes reported in MB instead of GB. Each of these was handled explicitly rather than papered over — including a genuine bug I found and fixed, where MB-based storage values were being read as GB, producing physically impossible numbers (a "phone" with tens of thousands of GB of storage). The fix normalizes both units correctly and applies realistic range validation so future extraction errors surface instead of silently corrupting the dataset.

### 🧪 Feature Engineering

Beyond the raw scraped fields, the pipeline derives real business logic: price bands, market segments (blending price *and* device type, not price alone), a rating-per-rupee value score, hot-deal flags, brand tiering, and price-per-GB-storage efficiency. These exist because they answer the business question directly, not to pad the column count.

### 📊 Visualization

A five-page Power BI report — Price Overview, Deal & Value Analytics, Trends Over Time, Brand & Segment Deep-Dive, and a Home landing page — plus a custom **hover tooltip page** that shows a product's photo, price, rating, and discount the moment you hover over it in a scatter chart, powered by the same scraped image URLs.

---

## 🧭 Methodology — Stage by Stage

**1. Orchestration Layer (n8n)**
A schedule trigger (daily) and a manual trigger both feed the same workflow, matching how a real production job would support both automated runs and on-demand testing. A polling loop checks pipeline status every few seconds until it resolves to either outcome — never left running indefinitely.

**2. Async API Layer (FastAPI)**
The `/run-etl` endpoint responds immediately with a task ID instead of blocking on the scrape, using FastAPI's background task system. A `/etl-status/{task_id}` endpoint lets the caller check progress independently. Every run — success or failure — is logged to disk with a timestamp and, on failure, the actual error message, so nothing fails silently.

**3. Data Collection (Selenium)**
Product cards are located by their real DOM structure rather than assumed selectors, confirmed against live HTML each time a selector broke. Title, price, MRP, rating, review count, full spec text, product image, and Flipkart Assured status are captured per listing, with graceful fallbacks (`None`) when a field genuinely isn't present, rather than crashing the run.

**4. Cleaning (pandas)**
Deduplication uses a composite key (title + price + color + date) deliberately chosen to avoid two failure modes: collapsing genuinely different color variants into one row, and collapsing legitimate day-over-day price history into a single stale snapshot. Units are normalized, data types enforced, and implausible values filtered as extraction errors rather than trusted blindly.

**5. Feature Engineering (business logic)**
Market segment, value score, discount metrics, and rating tiers are derived specifically to support comparative, decision-ready analysis — the same layer a real BI analyst would build before handing data to a dashboard.

**6. Reporting (Power BI)**
Each dashboard page has its own distinct KPI focus (market scale, deal value, time trend, brand/trust) rather than repeating the same four numbers with different labels — a deliberate design choice made after noticing an early draft was doing exactly that.

---

## 💡 Key Insights

- **Scraped e-commerce data is never clean by default** — unit inconsistencies (MB vs. GB), missing specs on basic phones, and duplicate sponsored listings all had to be handled explicitly, not assumed away.
- **A high discount percentage alone is a weak signal** — pairing discount with rating and market segment tells a very different story than discount in isolation; a steep markdown on a poorly-rated phone is not the same insight as one on a well-reviewed flagship.
- **Async orchestration is what makes daily automation realistic** — a synchronous scrape-and-wait design would make the trigger layer (n8n) block for minutes per run; separating "start the job" from "check on the job" is what allows scheduling to work at all.
- **Data validation earns its keep on the very first real bug it catches** — the MB/GB issue would have been invisible in a quick visual scan of the dashboard; it only surfaced because storage values were sanity-checked against realistic physical bounds.
- **Failure handling has to be designed as deliberately as success handling** — an early version of this pipeline could loop indefinitely if a run failed, since only the success condition was checked. Explicit failure detection and a dedicated failure-notification path were required, not optional.

---

## 🏢 Business Intelligence & Future Outlook

For a retail or e-commerce analytics team, this kind of pipeline exists to remove humans from a repetitive, time-sensitive loop: nobody should have to manually re-check competitor prices every morning to answer "did anything change." The dashboard is built to answer three practical questions on sight — where are the genuine deals, which brands play in which price tiers, and how has the market shifted since the last check.

The natural next steps are documented here honestly rather than left implicit: moving from a laptop-dependent schedule to a cloud-hosted deployment (Azure/AWS) so the pipeline runs independent of any one machine staying powered on; extending the scraper to visit individual product pages for deeper fields (seller, stock, delivery type) at the cost of a longer run time; and, once enough daily history accumulates, building genuine day-over-day price-movement detection rather than single-snapshot comparisons.

---

## ⚠️ Honest Limitations

- **Local scheduling requires the host machine to stay on** — both n8n and FastAPI must be running for the daily trigger to fire; a missed window does not retroactively catch up.
- **Flipkart's CSS class names are not guaranteed stable** — they can change on redeploy, which has already required selector fixes mid-project; this is a known maintenance cost of scraping over an official API.
- **Deeper product-page fields (description, seller, stock) are intentionally out of scope for now** — capturing them would require visiting each listing individually, substantially increasing run time and anti-bot risk.
- **Listing volume reflects Flipkart's own search ranking for the tracked query**, not true market share — it's a proxy for assortment visibility, not a sales figure.

---

## 🧠 Skills Applied

- **Async System Design** — building a non-blocking trigger → background-task → polling pattern from scratch, the same architectural shape used in production data platforms.
- **Resilient Web Scraping** — handling anti-bot blocking, DOM structure changes, and lazy-loaded content through live HTML inspection rather than guesswork.
- **Data Quality Auditing** — catching a real unit-conversion bug through domain-sense range checking, not an automated tool.
- **Business-Oriented Feature Engineering** — deriving value scores, market segments, and deal flags that map directly to a decision a stakeholder would actually make.
- **End-to-End Pipeline Ownership** — orchestration, backend, scraping, cleaning, and dashboarding all built and debugged as one connected system, not isolated exercises.

---

## 🚀 About Me

I'm **Bernad Meckenzi** — transitioning from medical billing into data analytics and business intelligence, one hands-on project at a time. I hold a **B.Sc. in Mathematics** and am completing an AI-Driven Data Analysis certification, but projects like this one — built, broken, and fixed in real time — are where the actual learning has happened.

| 🔧 Skill Area | 🌟 Tools |
|---|---|
| ⚙️ Automation & Orchestration | n8n, FastAPI, Python |
| 🕸️ Data Collection | Selenium, BeautifulSoup, Requests |
| 🐍 Data Wrangling | Pandas, NumPy |
| 📈 Business Intelligence | Power BI, DAX, Power Query |
| 🗄️ Data Querying | SQL |
| 🧠 Core Strength | End-to-End Pipeline Design & Data Quality Auditing |

My approach: **build the whole pipeline, not just the analysis — and when something breaks, fix the root cause, not the symptom.**

---

## 📫 Let's Connect

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Bernad2304-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Bernad2304)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Bernad%20Meckenzi%20S-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/bernad-meckenzi-s)

⭐ **If this project helped you understand what a real async ETL + BI pipeline looks like end to end, a star would mean a lot.**

</div>
