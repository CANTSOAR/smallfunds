# Hedge Fund Scraper

This repository contains a scraper for SEC Investment Adviser bulk XML records to filter hedge funds with $10M - $1000M in AUM.
[https://adviserinfo.sec.gov/compilation](https://adviserinfo.sec.gov/compilation)

## Folder Outputs
The script generates results in two folders:
- **`full/`**: Statistics for all hedge funds matching AUM and private fund filters.
- **`nyc/`**: Filtered down specifically to New York City.

Inside each folder, you will find:
1. `.csv`: Raw spreadsheet data.
2. `.md`: Markdown table file with clickable links.