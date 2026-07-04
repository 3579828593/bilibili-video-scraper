<div align="center">

# 🎬 Bilibili Video Scraper

**Batch Video Title Scraper & Analyzer for Bilibili Creators**

Fetch all video metadata from any Bilibili UP creator via WBI-signed API, with automatic intelligent analysis reports.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/3579828593/bilibili-video-scraper?style=social)](https://github.com/3579828593/bilibili-video-scraper/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/3579828593/bilibili-video-scraper)](https://github.com/3579828593/bilibili-video-scraper/issues)

[中文](README.md) | [English](README_EN.md)

</div>

---

> ## ⚠️ Disclaimer
>
> This tool is **for educational and personal use only**, not for any commercial purpose.
>
> - Please comply with the [Bilibili Terms of Service](https://www.bilibili.com/protocal/licence.html) and `robots.txt` rules
> - Do not put excessive pressure on the API; default request interval is 0.5 seconds
> - This tool does not store or transmit user login credentials
> - **Users bear all legal responsibility for improper use**
> - Contact the author to remove any content that infringes third-party rights

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 Full Scraping | Automatically paginate through all videos via WBI-signed API (supports hundreds/thousands) |
| 🔐 No Login Required | Based on WBI signing algorithm, no cookies needed |
| 📊 Smart Analysis | Auto-extract game names, category stats, yearly trends, play count rankings |
| 📝 Markdown Reports | One-click structured analysis report generation |
| 📄 CSV Export | Export to CSV format for Excel/Google Sheets analysis |
| ⚡ Resume Support | Failed pages recorded for later retry |
| 🛠️ CLI Tool | Flexible command-line configuration |
| 📦 Zero Config | `pip install -r requirements.txt && python main.py --mid <UID>` |

---

## 🚀 Quick Start

### Requirements

- Python 3.8+
- pip
- Internet access to Bilibili API

### Installation

```bash
git clone https://github.com/3579828593/bilibili-video-scraper.git
cd bilibili-video-scraper

python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Usage

```bash
# Scrape all videos from a creator
python main.py --mid 177230427

# Scrape + generate analysis report
python main.py --mid 177230427 --analyze

# Export to CSV
python main.py --mid 177230427 --csv

# Analyze existing JSON data (no re-scraping)
python main.py -i up_177230427_videos.json --analyze
```

### Parameters

| Param | Alias | Default | Description |
|-------|-------|---------|-------------|
| `--mid` | — | *(required)* | Target creator UID |
| `--input` | `-i` | — | Existing JSON file path |
| `--output` | `-o` | `up_{mid}.json` | Output JSON path |
| `--analyze` | — | `False` | Generate analysis report |
| `--report` | — | `up_{mid}.md` | Report output path |
| `--csv` | — | `False` | Also export CSV format |
| `--page-size` | — | `50` | Items per page (1-100) |
| `--delay` | — | `0.5` | Request interval (seconds) |
| `--retries` | — | `3` | Max retries per page |
| `--quiet` | `-q` | `False` | Quiet mode |

---

## 📁 Project Structure

```
bilibili-video-scraper/
├── src/
│   ├── wbi_signer.py        # WBI signing module
│   ├── scraper.py           # Video scraping module
│   └── analyzer.py          # Data analysis module
├── tests/
│   └── test_scraper.py      # Unit tests
├── main.py                   # CLI entry point
├── requirements.txt
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

---

## 🔧 Core Modules

### WBI Signer (`src/wbi_signer.py`)
Implements Bilibili's WBI signing algorithm for API authentication.

### Scraper (`src/scraper.py`)
- `BilibiliScraper` class with full scraping logic
- Auto-pagination based on total count
- Smart retry for rate-limit error codes (-352/-412/-799)
- JSON and CSV output support

### Analyzer (`src/analyzer.py`)
- 60+ game alias library with fuzzy matching
- 9 categories: FPS, Horror, RPG, Indie, Sandbox, MOBA, etc.
- Statistics: Top games, category distribution, yearly trends, play rankings

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🔒 Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## 📄 License

[MIT License](LICENSE)
