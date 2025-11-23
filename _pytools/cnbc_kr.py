#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNBC 크롤러 (한국어)
- CNBC에서 최신 주식 시장 뉴스 수집
- 전체 본문 크롤링
- 한국어 자동 번역
"""

import cloudscraper
from bs4 import BeautifulSoup
from readability import Document
from deep_translator import GoogleTranslator
from datetime import datetime
import re
from pathlib import Path
import sys
import time
import json

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class CNBCKR:
    def __init__(self):
        self.base_url = "https://www.cnbc.com"
        self.posts_dir = Path(__file__).parent.parent / "_posts"
        self.posts_dir.mkdir(exist_ok=True)

        # cloudscraper 세션 생성
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

        # 번역기 초기화
        self.translator = GoogleTranslator(source='en', target='ko')

        # Ticker 캐시 로드
        self.ticker_cache = self.load_ticker_cache()

    def load_ticker_cache(self):
        """Ticker 캐시 파일 로드"""
        cache_file = Path(__file__).parent / "ticker_cache.json"
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('tickers', {})
            return {}
        except Exception as e:
            print(f"[WARNING] 티커 캐시 로드 실패: {e}")
            return {}

    def fetch_news_list(self):
        """CNBC에서 뉴스 목록 가져오기"""
        try:
            print("[INFO] CNBC 뉴스 수집 중...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            # 여러 섹션에서 뉴스 수집
            news_urls = [
                f"{self.base_url}/markets/",
                f"{self.base_url}/investing/",
                f"{self.base_url}/technology/",
            ]

            articles = []
            seen_urls = set()

            for news_url in news_urls:
                try:
                    response = self.scraper.get(news_url, headers=headers, timeout=30)
                    if response.status_code != 200:
                        print(f"  [WARNING] {news_url} 접근 실패 ({response.status_code})")
                        continue

                    soup = BeautifulSoup(response.text, 'lxml')

                    # 뉴스 아이템 찾기 - CNBC 구조에 맞춤
                    # 방법 1: Card 컴포넌트
                    news_items = soup.find_all('div', class_=re.compile(r'Card-|RiverCard'))

                    # 방법 2: article 태그
                    if not news_items:
                        news_items = soup.find_all('article')

                    # 방법 3: 링크가 있는 섹션
                    if not news_items:
                        news_items = soup.find_all('div', class_=re.compile(r'LatestNews|FeaturedCard'))

                    for item in news_items:
                        try:
                            # 링크와 제목 추출
                            link_tag = item.find('a', href=True)
                            if not link_tag:
                                continue

                            href = link_tag.get('href', '')

                            # 제목 추출
                            title_tag = item.find(['h2', 'h3', 'span'], class_=re.compile(r'Card-title|headline'))
                            if title_tag:
                                title = title_tag.get_text(strip=True)
                            else:
                                title = link_tag.get_text(strip=True)

                            if not title or len(title) < 10:
                                continue

                            # URL 정규화
                            if href.startswith('/'):
                                full_url = f"{self.base_url}{href}"
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue

                            # CNBC 기사만 필터링
                            if 'cnbc.com' not in full_url:
                                continue

                            # 비디오/오디오 제외
                            if '/video/' in full_url or '/audio/' in full_url:
                                continue

                            # 중복 제거
                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)

                            # 이미지 추출
                            img_tag = item.find('img')
                            image_url = ''
                            if img_tag:
                                image_url = img_tag.get('src') or img_tag.get('data-src', '')

                            # 요약 추출
                            desc_tag = item.find('div', class_=re.compile(r'Card-description|summary'))
                            summary = desc_tag.get_text(strip=True) if desc_tag else ''

                            articles.append({
                                'title': title,
                                'url': full_url,
                                'image_url': image_url,
                                'summary': summary,
                                'source': 'CNBC'
                            })

                        except Exception:
                            continue

                    time.sleep(1)

                except Exception as e:
                    print(f"[WARNING] {news_url} 수집 실패: {e}")
                    continue

            print(f"[OK] {len(articles)}개 기사 발견")
            return articles

        except Exception as e:
            print(f"[ERROR] 뉴스 목록 수집 실패: {e}")
            return []

    def fetch_full_article_content(self, url):
        """기사 페이지에서 전체 본문 크롤링"""
        try:
            print(f"  - 전체 본문 크롤링 중...")
            time.sleep(1)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }

            response = self.scraper.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # 제목 추출
            title = None
            title_tag = soup.find('h1', class_=re.compile(r'ArticleHeader-headline'))
            if not title_tag:
                title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)

            # 본문 추출 시도
            content_parts = []

            # 방법 1: ArticleBody에서 본문 추출
            article_body = soup.find('div', class_=re.compile(r'ArticleBody-articleBody|group'))
            if not article_body:
                article_body = soup.find('div', {'data-module': 'ArticleBody'})
            if not article_body:
                article_body = soup.find('article')

            if article_body:
                # 관련 기사, 광고 등 제거
                for unwanted in article_body.find_all(['aside', 'figure'], class_=re.compile(r'Related|Ad|Promo')):
                    unwanted.decompose()

                paragraphs = article_body.find_all(['p', 'h2', 'h3'])
                for p in paragraphs:
                    # 부모가 광고/관련기사면 스킵
                    parent_classes = ' '.join(p.parent.get('class', []))
                    if any(skip in parent_classes.lower() for skip in ['related', 'ad', 'promo', 'sidebar']):
                        continue

                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        # 광고/구독 문구 필터링
                        skip_phrases = ['subscribe', 'newsletter', 'sign up', 'click here',
                                       'read more', 'advertisement', 'sponsored',
                                       'cnbc pro', 'watch video', 'related:']
                        if not any(skip.lower() in text.lower() for skip in skip_phrases):
                            content_parts.append(text)

            # 방법 2: Readability 사용
            if not content_parts or len('\n'.join(content_parts)) < 200:
                print(f"  - Readability 방식으로 시도...")
                doc = Document(response.text)
                if not title:
                    title = doc.title()
                content_html = doc.summary()

                soup2 = BeautifulSoup(content_html, 'lxml')
                paragraphs = soup2.find_all(['p', 'h2', 'h3'])

                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        content_parts.append(text)

            content = '\n\n'.join(content_parts)

            if content and len(content) > 200:
                print(f"  - 본문 추출 완료 ({len(content)} 자)")
                return title, content

            return None, None

        except Exception as e:
            print(f"  [WARNING] 본문 크롤링 실패: {e}")
            return None, None

    def extract_tickers_from_text(self, text):
        """텍스트에서 티커 심볼 추출"""
        patterns = [
            r'\$([A-Z]{1,5})\b',
            r'\(([A-Z]{1,5})\)',
            r'\b([A-Z]{2,5})\b(?=\s+(?:stock|shares|price|fell|rose|gained|dropped|surged|plunged))',
        ]

        tickers = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match in self.ticker_cache:
                    tickers.add(match)

        return list(tickers)[:5]

    def is_korean(self, text):
        """텍스트가 한국어인지 확인"""
        if not text:
            return False
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.sub(r'\s', '', text))
        if total_chars == 0:
            return False
        return (korean_chars / total_chars) > 0.3

    def translate_to_korean(self, text, max_length=4500):
        """한국어로 번역"""
        try:
            if not text or len(text.strip()) == 0:
                return text

            if self.is_korean(text):
                return text

            if len(text) > max_length:
                text = text[:max_length]

            translated = self.translator.translate(text)
            time.sleep(0.5)
            return translated

        except Exception as e:
            print(f"  [WARNING] 번역 실패: {e}")
            return text

    def sanitize_filename(self, text):
        """파일명으로 사용 가능한 문자열로 변환"""
        text = re.sub(r'[^\w\sㄱ-ㅎㅏ-ㅣ가-힣-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')[:80]

    def convert_tickers_to_badges(self, text, tickers=None):
        """티커 심볼을 실시간 뱃지로 변환"""
        if not tickers:
            return text

        for ticker in tickers:
            cache_data = self.ticker_cache.get(ticker, {})
            if isinstance(cache_data, dict):
                instrument_id = cache_data.get('instrument_id', '')
            else:
                instrument_id = cache_data

            if instrument_id:
                badge_html = f'<span class="stock-ticker" data-ticker="{ticker}" data-symbol="{ticker}" data-instrument-id="{instrument_id}">${ticker}</span>'
                text = re.sub(rf'\${ticker}\b', badge_html, text)

        return text

    def create_post(self, article, index):
        """Jekyll 포스트 생성"""
        try:
            original_title = article.get('title', '').strip()
            article_url = article.get('url', '')
            image_url = article.get('image_url', '')
            summary = article.get('summary', '')

            if not original_title or not article_url:
                return False

            print(f"\n{'='*70}")
            print(f"[{index}] {original_title[:50]}...")
            print(f"{'='*70}")

            # 1. 본문 가져오기
            full_title, full_content = self.fetch_full_article_content(article_url)

            # 요약만 있는 경우 사용
            if not full_content and summary:
                full_content = summary

            if not full_content or len(full_content) < 100:
                print(f"  [SKIP] 충분한 본문이 없음")
                return False

            # 2. 티커 추출
            tickers = self.extract_tickers_from_text(full_content)

            # 3. 제목 번역
            title_to_use = full_title if full_title else original_title
            print(f"  - 제목 번역 중...")
            title_kr = self.translate_to_korean(title_to_use)

            # 4. 본문 번역
            print(f"  - 본문 번역 중...")
            content_chunks = [full_content[i:i+4500] for i in range(0, len(full_content), 4500)]
            content_kr_parts = []

            for i, chunk in enumerate(content_chunks[:3], 1):
                if i > 1:
                    print(f"  - 번역 진행 중... ({i}/{min(3, len(content_chunks))})")
                translated = self.translate_to_korean(chunk)
                if translated:
                    content_kr_parts.append(translated)

            content_kr = '\n\n'.join(content_kr_parts)

            # 5. 요약 생성
            excerpt_text = content_kr[:200] if len(content_kr) > 200 else content_kr
            excerpt_clean = re.sub(r'\s+', ' ', excerpt_text).strip()
            excerpt = excerpt_clean + "..." if len(content_kr) > 200 else excerpt_clean

            # 6. 티커 뱃지 변환
            content_kr = self.convert_tickers_to_badges(content_kr, tickers)

            # 7. 날짜
            pub_date = datetime.now()
            date_str = pub_date.strftime('%Y-%m-%d')

            # 8. 파일명 생성
            filename_base = self.sanitize_filename(title_kr)
            if not filename_base or len(filename_base) < 5:
                filename_base = self.sanitize_filename(original_title)

            filename = f"{date_str}-cnbc-{index:02d}-{filename_base}.md"
            filepath = self.posts_dir / filename

            if filepath.exists():
                print(f"  [SKIP] 이미 존재: {filename}")
                return False

            # 9. Front Matter 생성
            title_escaped = title_kr.replace("'", "''")
            excerpt_escaped = excerpt.replace("'", "''")
            image_line = f'image: "{image_url}"\n' if image_url else ''

            # 주식 태그 생성
            stock_tags_yaml = ""
            if tickers:
                stock_tags_yaml = "stock_tags:\n"
                for ticker in tickers:
                    cache_data = self.ticker_cache.get(ticker, {})
                    if isinstance(cache_data, dict):
                        instrument_id = cache_data.get('instrument_id', '')
                    else:
                        instrument_id = cache_data
                    if instrument_id:
                        stock_tags_yaml += f"  - symbol: {ticker}\n"
                        stock_tags_yaml += f"    instrument_id: {instrument_id}\n"

            front_matter = f"""---
layout: post
title: '{title_escaped}'
date: {pub_date.strftime('%Y-%m-%d %H:%M:%S +0900')}
categories: [Financial]
author: "CNBC"
{image_line}excerpt: '{excerpt_escaped}'
{stock_tags_yaml}---

{content_kr}

---

*출처: [CNBC]({article_url})*
"""

            # 10. 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter)

            print(f"  [OK] 포스트 생성 완료: {filename}\n")
            return True

        except Exception as e:
            print(f"  [ERROR] 포스트 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, limit=5):
        """크롤러 실행"""
        print("=" * 70)
        print("CNBC 크롤러 (한국어)")
        print("=" * 70)

        articles = self.fetch_news_list()

        if not articles:
            print("\n[ERROR] 뉴스 수집 실패")
            return

        print(f"총 {len(articles)}개 기사 발견, 최대 {limit}개 처리\n")

        created_count = 0
        for i, article in enumerate(articles[:limit], 1):
            try:
                if self.create_post(article, i):
                    created_count += 1
            except Exception as e:
                print(f"[ERROR] 처리 중 오류: {e}")
                continue

        print("\n" + "=" * 70)
        print(f"완료: {created_count}개의 포스트 생성됨")
        print("=" * 70)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='CNBC 크롤러 (한국어)')
    parser.add_argument('--limit', type=int, default=5, help='가져올 기사 수 (기본: 5)')
    args = parser.parse_args()

    crawler = CNBCKR()
    crawler.run(limit=args.limit)


if __name__ == "__main__":
    main()
