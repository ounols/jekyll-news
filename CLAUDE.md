# CLAUDE.md - AI Assistant Guide for jekyll-news

## Project Overview

**jekyll-news** is a Korean-language news aggregator site called "@News" built with Jekyll 4.3. It aggregates financial news from Investing.com, translates content to Korean, and displays real-time stock tickers. The site is hosted at `https://news.ounols.kr`.

### Key Features
- Multi-category news platform (World, Business, Financial, Tech, Gaming, For Dev)
- Automated financial news scraping with Korean translation via Python tools
- Real-time stock ticker integration using Investing.com API
- Dark mode support and responsive design
- Client-side search functionality

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Site Generator | Jekyll 4.3 |
| Templates | Liquid, HTML5 |
| Styling | SCSS with Pretendard Variable font (Korean support) |
| Scripts | JavaScript (ES6) |
| Automation | Python 3 (news scraping, translation) |
| External APIs | Investing.com (News, Instruments), Google Translate |
| Plugins | jekyll-feed, jekyll-sitemap, jekyll-seo-tag, jekyll-paginate-v2 |

## Directory Structure

```
jekyll-news/
├── _config.yml              # Main Jekyll configuration
├── Gemfile                  # Ruby dependencies
├── _layouts/                # Template layouts
│   ├── default.html         # Base template
│   ├── home.html            # Homepage with category tabs
│   ├── post.html            # Single post view
│   ├── category.html        # Category listing
│   └── page.html            # Generic page
├── _includes/               # Reusable components
│   ├── header.html          # Navigation, dark mode, search
│   ├── footer.html          # Footer widgets, subscribe
│   ├── sidebar.html         # Newsletter, recent posts
│   ├── post-card.html       # Post preview card
│   ├── post-list-item.html  # List item variant
│   └── video-card.html      # Video preview
├── _posts/                  # Blog posts (YYYY-MM-DD-slug.md)
├── _authors/                # Author profiles
├── _pytools/                # Python news scraping tools
│   ├── run_all_crawlers.py       # Unified crawler runner
│   ├── investing_complete_kr.py  # Investing.com crawler
│   ├── yahoo_finance_kr.py       # Yahoo Finance crawler
│   ├── marketwatch_kr.py         # MarketWatch crawler
│   ├── cnbc_kr.py                # CNBC crawler
│   ├── requirements.txt          # Python dependencies
│   └── ticker_cache.json         # Stock symbol mapping
├── assets/
│   ├── css/
│   │   ├── main.scss        # Main styles
│   │   └── stock-ticker.css # Stock badge styles
│   ├── js/
│   │   ├── main.js          # Core functionality
│   │   └── stock-ticker.js  # Real-time stock updates
│   └── images/              # Static images
├── media/                   # Post media files
└── [category].html          # Category pages (world, business, etc.)
```

## Development Workflows

### Local Development

```bash
# Install Ruby dependencies
bundle install

# Start development server
jekyll serve

# Build for production
jekyll build
```

### Creating New Posts

Posts use the filename format: `YYYY-MM-DD-slug.md` in `_posts/`

Required front matter:
```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
categories: [Category]  # One of: World, Business, Financial, Tech, Gaming, For Dev
author: "Author Name"
excerpt: "Summary text"
image: "/path/to/image.jpg"
tags: [tag1, tag2]
---
```

For auto-generated financial posts with stock tags:
```yaml
stock_tags:
  - symbol: NVDA
    instrument_id: 6497
```

### Running the News Crawlers

```bash
cd _pytools
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate.ps1  # Windows

pip install -r requirements.txt

# Run all crawlers (5 articles each)
python run_all_crawlers.py

# Run all crawlers with custom limit
python run_all_crawlers.py --limit 10

# Run specific source only
python run_all_crawlers.py --source investing  # Investing.com
python run_all_crawlers.py --source yahoo      # Yahoo Finance
python run_all_crawlers.py --source mw         # MarketWatch
python run_all_crawlers.py --source cnbc       # CNBC

# Or run individual crawlers directly
python investing_complete_kr.py --limit 5
python yahoo_finance_kr.py --limit 5
python marketwatch_kr.py --limit 5
python cnbc_kr.py --limit 5
```

All crawlers:
1. Fetch news from their respective sources
2. Extract full article content
3. Translate to Korean via Google Translate
4. Generate Jekyll posts with stock ticker badges
5. Save to `../_posts/`

## Key Conventions

### Naming
- **Posts**: `YYYY-MM-DD-descriptive-slug.md`
- **Categories**: Capitalized (World, Business, Financial, Tech, Gaming, For Dev)
- **CSS Classes**: BEM-style (`.article__title`, `.post__meta`)
- **SCSS Variables**: kebab-case (`$base-font-size`)

### CSS/Styling
- SCSS with organized sections in `assets/css/main.scss`
- CSS variables in `:root` for theming
- Dark mode via `[dark]` attribute on `<html>`
- Responsive grid: `col`, `col-d-6`, `col-t-12` pattern
- Color scheme:
  - Brand: `--brand-color: #0056fe`
  - Up/positive: green
  - Down/negative: red

### JavaScript
- Event delegation for dynamic elements
- `localStorage` for theme persistence
- Fetch API for data loading
- Debouncing (300ms) for search input

### Liquid Templates
- Collections: `site.posts`, `site.authors`
- Common filters: `relative_url`, `jsonify`, `truncatewords`
- Section markers: `<!-- begin section --> ... <!-- end section -->`

### Content
- Each post has ONE primary category
- Default author: "Alena Curtis" (configurable in `_config.yml`)
- Images optional (graceful fallback)
- Excerpt auto-generated from content if not provided

## Important Files

| File | Purpose |
|------|---------|
| `_config.yml` | Site settings, navigation, collections, defaults |
| `_layouts/home.html` | Homepage with featured posts and category tabs |
| `_layouts/post.html` | Post template with author, share buttons, related posts |
| `assets/js/main.js` | Search, dark mode, mobile menu, category tabs |
| `assets/js/stock-ticker.js` | Real-time stock price updates |
| `_pytools/run_all_crawlers.py` | Unified crawler runner for all sources |
| `_pytools/investing_complete_kr.py` | Investing.com news crawler |
| `_pytools/yahoo_finance_kr.py` | Yahoo Finance news crawler |
| `_pytools/marketwatch_kr.py` | MarketWatch news crawler |
| `_pytools/cnbc_kr.py` | CNBC news crawler |
| `_pytools/ticker_cache.json` | Stock symbol to Investing.com ID mapping |
| `search.json` | Liquid template generating search index |

## News Crawler Sources

| Source | File | Description |
|--------|------|-------------|
| Investing.com | `investing_complete_kr.py` | Breaking News API, full content, stock data |
| Yahoo Finance | `yahoo_finance_kr.py` | Stock Market News, Latest News sections |
| MarketWatch | `marketwatch_kr.py` | Latest News, Markets, Investing sections |
| CNBC | `cnbc_kr.py` | Markets, Investing, Technology sections |

## Stock Ticker System

### How It Works
1. Posts can include `stock_tags` in front matter
2. Stock badges rendered with `data-instrument-id` attribute
3. `stock-ticker.js` fetches real-time data from Investing.com API
4. Updates every 5 minutes

### Adding New Stocks
Edit `_pytools/ticker_cache.json`:
```json
{
  "SYMBOL": {
    "instrument_id": 12345,
    "exchange_id": 67890
  }
}
```

### Supported Markets
- US (NASDAQ, NYSE): NVDA, AAPL, MSFT, GOOGL, TSLA, META, AMZN, etc.
- Korea (KRX): Samsung (005930), SK Hynix (000660)
- Taiwan: TSMC (2330), Foxconn (2317)
- Japan: SoftBank (9984), Advantest (6857)
- Hong Kong/China: Baidu, Alibaba, Tencent

## Common Tasks

### Add a New Category
1. Create `categoryname.html` in root with category layout
2. Add to navigation in `_config.yml`
3. Update category tabs in `_layouts/home.html` if needed

### Add a New Author
Create `_authors/author-slug.md`:
```yaml
---
name: Author Name
image: /assets/images/authors/author.jpg
bio: Biography text
social:
  twitter: https://twitter.com/...
---
```

### Modify Theme Colors
Edit CSS variables in `assets/css/main.scss`:
```scss
:root {
  --brand-color: #0056fe;
  // Other color variables...
}
```

### Enable Dark Mode by Default
In `_layouts/default.html`, modify the dark mode detection script.

## Build Exclusions

The following are excluded from Jekyll build (defined in `_config.yml`):
- `_pytools/` - Python automation scripts
- Standard ignores: `vendor`, `node_modules`, etc.

## Language

- Site language: Korean (`lang: "ko"`)
- Primary font: Pretendard Variable (supports Korean)
- Content can be in Korean or English (crawler auto-translates)

## External Dependencies

### Ruby Gems (Gemfile)
- jekyll ~> 4.3
- jekyll-feed ~> 0.15
- jekyll-sitemap ~> 1.4
- jekyll-seo-tag ~> 2.8
- jekyll-paginate-v2 ~> 3.0

### Python (requirements.txt)
- requests, cloudscraper (HTTP)
- beautifulsoup4, lxml (parsing)
- readability-lxml (content extraction)
- deep-translator (Google Translate)

## Troubleshooting

### News Crawler Issues
- **403 Errors**: Cloudflare blocks; try again later or update cloudscraper
- **Translation Failures**: Google Translate rate limits; reduce batch size
- **Missing Tickers**: Add to `ticker_cache.json`

### Build Issues
- Run `bundle install` for missing gems
- Check `_config.yml` syntax
- Verify front matter in problematic posts

### Stock Ticker Not Updating
- Check browser console for API errors
- Verify `instrument_id` in ticker_cache.json
- API may have rate limits
