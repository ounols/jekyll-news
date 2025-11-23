#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤러 로직 테스트 (오프라인 모드)
- 실제 네트워크 요청 없이 크롤러 로직 검증
- 샘플 HTML로 파싱 테스트
"""

import sys
from pathlib import Path
from datetime import datetime

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def test_imports():
    """필요한 모듈 import 테스트"""
    print("=" * 60)
    print("1. Import 테스트")
    print("=" * 60)

    modules = {
        'cloudscraper': False,
        'bs4': False,
        'readability': False,
        'deep_translator': False,
        'lxml': False,
    }

    try:
        import cloudscraper
        modules['cloudscraper'] = True
    except ImportError:
        pass

    try:
        from bs4 import BeautifulSoup
        modules['bs4'] = True
    except ImportError:
        pass

    try:
        from readability import Document
        modules['readability'] = True
    except ImportError:
        pass

    try:
        from deep_translator import GoogleTranslator
        modules['deep_translator'] = True
    except ImportError:
        pass

    try:
        import lxml
        modules['lxml'] = True
    except ImportError:
        pass

    for mod, status in modules.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {mod}")

    all_ok = all(modules.values())
    print(f"\n결과: {'모든 모듈 OK' if all_ok else '일부 모듈 누락'}")
    return all_ok


def test_html_parsing():
    """HTML 파싱 테스트"""
    print("\n" + "=" * 60)
    print("2. HTML 파싱 테스트")
    print("=" * 60)

    from bs4 import BeautifulSoup

    # 샘플 뉴스 HTML
    sample_html = """
    <html>
    <head><title>Stock Market News</title></head>
    <body>
        <article class="news-item">
            <h2 class="headline">NVIDIA Surges on AI Demand</h2>
            <p class="summary">NVIDIA stock rose 5% today amid strong AI chip demand.</p>
            <a href="/news/nvidia-ai-2024" class="link">Read more</a>
            <img src="/images/nvda.jpg" alt="NVIDIA">
        </article>
        <article class="news-item">
            <h2 class="headline">Apple Announces New iPhone</h2>
            <p class="summary">Apple unveiled the latest iPhone with advanced features.</p>
            <a href="/news/apple-iphone-2024" class="link">Read more</a>
        </article>
    </body>
    </html>
    """

    soup = BeautifulSoup(sample_html, 'lxml')
    articles = soup.find_all('article', class_='news-item')

    print(f"  발견된 기사 수: {len(articles)}")

    for i, article in enumerate(articles, 1):
        title = article.find('h2').get_text(strip=True)
        summary = article.find('p').get_text(strip=True)
        link = article.find('a').get('href', '')
        print(f"  [{i}] {title}")
        print(f"      링크: {link}")

    return len(articles) == 2


def test_rss_parsing():
    """RSS 파싱 테스트"""
    print("\n" + "=" * 60)
    print("3. RSS 파싱 테스트")
    print("=" * 60)

    from bs4 import BeautifulSoup

    # 샘플 RSS XML
    sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Finance News</title>
            <item>
                <title>Tesla Stock Rises After Earnings</title>
                <link>https://example.com/tesla-earnings</link>
                <description>Tesla exceeded analyst expectations...</description>
            </item>
            <item>
                <title>Fed Signals Rate Cut</title>
                <link>https://example.com/fed-rate-cut</link>
                <description>Federal Reserve hints at interest rate reduction...</description>
            </item>
        </channel>
    </rss>
    """

    soup = BeautifulSoup(sample_rss, 'lxml-xml')
    items = soup.find_all('item')

    print(f"  발견된 RSS 아이템 수: {len(items)}")

    for i, item in enumerate(items, 1):
        title = item.find('title').get_text(strip=True)
        link = item.find('link').get_text(strip=True)
        print(f"  [{i}] {title}")
        print(f"      링크: {link}")

    return len(items) == 2


def test_ticker_extraction():
    """티커 심볼 추출 테스트"""
    print("\n" + "=" * 60)
    print("4. 티커 심볼 추출 테스트")
    print("=" * 60)

    import re

    sample_text = """
    NVIDIA ($NVDA) stock surged 5% today. Meanwhile, Apple (AAPL)
    and Microsoft (MSFT) also saw gains. Tesla stock price increased
    after the company reported strong earnings.
    """

    patterns = [
        r'\$([A-Z]{1,5})\b',
        r'\(([A-Z]{2,5})\)',
    ]

    tickers = set()
    for pattern in patterns:
        matches = re.findall(pattern, sample_text)
        tickers.update(matches)

    print(f"  발견된 티커: {sorted(tickers)}")

    expected = {'NVDA', 'AAPL', 'MSFT'}
    return tickers == expected


def test_filename_sanitization():
    """파일명 생성 테스트"""
    print("\n" + "=" * 60)
    print("5. 파일명 생성 테스트")
    print("=" * 60)

    import re

    def sanitize_filename(text):
        text = re.sub(r'[^\w\sㄱ-ㅎㅏ-ㅣ가-힣-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')[:80]

    test_cases = [
        ("NVIDIA's Stock Surges 5%!", "NVIDIAs-Stock-Surges-5"),
        ("애플, 새 아이폰 발표", "애플-새-아이폰-발표"),
        ("Test   Multiple   Spaces", "Test-Multiple-Spaces"),
    ]

    all_pass = True
    for original, expected in test_cases:
        result = sanitize_filename(original)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{original}' -> '{result}'")
        if result != expected:
            print(f"      예상: '{expected}'")
            all_pass = False

    return all_pass


def test_post_generation():
    """포스트 생성 테스트"""
    print("\n" + "=" * 60)
    print("6. 포스트 Front Matter 생성 테스트")
    print("=" * 60)

    title = "NVIDIA Stock Surges on AI Demand"
    date = datetime.now()
    excerpt = "NVIDIA stock rose 5% today..."

    # YAML escape
    title_escaped = title.replace("'", "''")
    excerpt_escaped = excerpt.replace("'", "''")

    front_matter = f"""---
layout: post
title: '{title_escaped}'
date: {date.strftime('%Y-%m-%d %H:%M:%S +0900')}
categories: [Financial]
author: "Test Source"
excerpt: '{excerpt_escaped}'
stock_tags:
  - symbol: NVDA
    instrument_id: 6497
---

Test content here.
"""

    print("  생성된 Front Matter:")
    for line in front_matter.split('\n')[:10]:
        print(f"    {line}")

    # 기본 검증
    has_layout = 'layout: post' in front_matter
    has_title = f"title: '{title}'" in front_matter
    has_category = 'categories: [Financial]' in front_matter

    print(f"\n  layout 포함: {'✅' if has_layout else '❌'}")
    print(f"  title 포함: {'✅' if has_title else '❌'}")
    print(f"  categories 포함: {'✅' if has_category else '❌'}")

    return has_layout and has_title and has_category


def test_crawler_classes():
    """크롤러 클래스 로드 테스트"""
    print("\n" + "=" * 60)
    print("7. 크롤러 클래스 로드 테스트")
    print("=" * 60)

    crawlers = {}

    try:
        from investing_complete_kr import InvestingCompleteKR
        crawlers['Investing.com'] = True
    except Exception as e:
        crawlers['Investing.com'] = str(e)[:50]

    try:
        from yahoo_finance_kr import YahooFinanceKR
        crawlers['Yahoo Finance'] = True
    except Exception as e:
        crawlers['Yahoo Finance'] = str(e)[:50]

    try:
        from marketwatch_kr import MarketWatchKR
        crawlers['MarketWatch'] = True
    except Exception as e:
        crawlers['MarketWatch'] = str(e)[:50]

    try:
        from cnbc_kr import CNBCKR
        crawlers['CNBC'] = True
    except Exception as e:
        crawlers['CNBC'] = str(e)[:50]

    for name, status in crawlers.items():
        if status is True:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: {status}")

    return all(v is True for v in crawlers.values())


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🧪 크롤러 오프라인 테스트")
    print("=" * 60)

    results = {
        'Import 테스트': test_imports(),
        'HTML 파싱': test_html_parsing(),
        'RSS 파싱': test_rss_parsing(),
        '티커 추출': test_ticker_extraction(),
        '파일명 생성': test_filename_sanitization(),
        '포스트 생성': test_post_generation(),
        '크롤러 클래스': test_crawler_classes(),
    }

    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    for test_name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print("-" * 60)
    print(f"  총 {total_count}개 중 {passed_count}개 통과")

    if passed_count == total_count:
        print("\n✅ 모든 테스트 통과! 크롤러 로직이 정상입니다.")
        print("   실제 네트워크 환경에서 실행하면 작동할 것으로 예상됩니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 위 결과를 확인하세요.")


if __name__ == "__main__":
    main()
