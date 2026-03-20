# Hedge Fund Scraper

This repository contains a scraper for SEC Investment Adviser bulk XML records to filter hedge funds with $10M - $1000M in AUM.

## Folder Outputs
The script generates results in two folders:
- **`full/`**: Statistics for all hedge funds matching AUM and private fund filters.
- **`nyc/`**: Filtered down specifically to New York City.

Inside each folder, you will find:
1. `.csv`: Raw spreadsheet data.
2. `.md`: Markdown table file with clickable links.
3. `.html`: Fully interactive sortable dashboard.

---

## How to View Sortable Dashboards on GitHub

GitHub renders `.html` files as **source code** inside the repository view, meaning the sortable feature won't work there directly. To use the interactive sorting:

### Option A: Open Locally (Fastest)
1. Download or clone this repository to your computer.
2. Double-click `hedge_funds.html` located in `full/` or `nyc/` to open it in your web browser.

### Option B: Enable GitHub Pages (Best for sharing)
You can set up GitHub Pages for your repo to host the HTML files as fully interactable web pages:
1. In your GitHub repository, go to **Settings** -> **Pages** (left sidebar).
2. Under **Build and deployment**, set Source to `Deploy from a branch`.
3. Select `main` branch and folder `/(root)`, then click **Save**.
4. Wait 1-2 minutes. Your page will be live at:  
   `https://[username].github.io/[repo_name]/nyc/hedge_funds.html`  
   *(Replace with your GitHub username and repository name)*
