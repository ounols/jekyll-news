#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investing.com 완전판 크롤러 (한국어)
- API로 Breaking News 목록 + 이미지 가져오기
- 실제 페이지에서 전체 본문 크롤링
- 관련 주식 정보 추가
- 한국어 자동 번역 (필요시)
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

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class InvestingCompleteKR:
    def __init__(self):
        self.base_url = "https://www.investing.com"
        self.api_url = "https://endpoints.investing.com/news-delivery/api/v2/articles/delivery/domains/18/news/lists/breaking-news"
        self.instrument_api_url = "https://endpoints.investing.com/pd-instruments/v1/instruments"
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
        self.bearer_token = None
    
    def search_instrument(self, search_text):
        """
        Investing.com 검색 API로 종목 정보 조회

        Args:
            search_text: 검색어 (예: "nvda", "005930", "samsung")

        Returns:
            dict: {'id': int, 'symbol': str, 'name': str, 'aql_link': str, 'exchange': str}
            또는 None (검색 실패)
        """
        if not search_text:
            return None

        try:
            url = "https://kr.investing.com/search/service/search"

            data = {
                'search_text': search_text,
                'term': search_text,
                'country_id': '0',
                'tab_id': 'All'
            }

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://kr.investing.com',
                'Referer': 'https://kr.investing.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0'
            }

            response = self.scraper.post(url, data=data, headers=headers, timeout=30)

            if response.status_code == 200:
                result_data = response.json()
                all_results = result_data.get('All', [])

                if all_results and len(all_results) > 0:
                    first_result = all_results[0]

                    inst_info = {
                        'id': first_result.get('pair_ID'),
                        'symbol': first_result.get('symbol'),
                        'name': first_result.get('name'),
                        'aql_link': first_result.get('aql_link'),
                        'exchange': first_result.get('exchange_popular_symbol')
                    }

                    return inst_info

            return None

        except Exception as e:
            print(f"[WARNING] 종목 검색 실패 ({search_text}): {e}")
            return None

    def extract_bearer_token(self):
        """Bearer 토큰 추출 (개선된 버전)"""
        try:
            print("[INFO] Bearer 토큰 추출 중...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            response = self.scraper.get(f"{self.base_url}/news/latest-news", headers=headers, timeout=30)

            if response.status_code != 200:
                print(f"[WARNING] 페이지 로드 실패 (HTTP {response.status_code})")

            # 방법 1: __NEXT_DATA__에서 accessToken 추출 (가장 확실한 방법)
            soup = BeautifulSoup(response.text, 'lxml')
            next_data = soup.find('script', {'id': '__NEXT_DATA__'})

            if next_data:
                try:
                    import json
                    data = json.loads(next_data.string)

                    # props.pageProps.accessToken 경로로 접근
                    access_token = data.get('props', {}).get('pageProps', {}).get('accessToken')

                    if access_token and len(access_token) > 100 and '.' in access_token:
                        print(f"[OK] __NEXT_DATA__에서 JWT 토큰 발견 (길이: {len(access_token)})")
                        return access_token
                except Exception as e:
                    print(f"[WARNING] __NEXT_DATA__ 파싱 실패: {e}")

            # 방법 2: Regex 패턴 사용 (Fallback)
            print("[INFO] Regex 패턴으로 시도 중...")

            patterns = [
                r'"accessToken"\s*:\s*"([^"]+)"',
                r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
                r'"token"\s*:\s*"(eyJ[^"]+)"',
                r'Bearer\s+([A-Za-z0-9\-_\.]+)',
                r'token["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_\.]+)',
            ]

            all_tokens = []
            for pattern in patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                all_tokens.extend(matches)

            # JWT 토큰 찾기 (보통 100자 이상, '.'이 포함됨)
            jwt_tokens = [t for t in all_tokens if len(t) > 100 and '.' in t]

            if jwt_tokens:
                token = jwt_tokens[0]
                print(f"[OK] Regex로 JWT 토큰 발견 (길이: {len(token)})")
                return token

            # JWT를 못 찾으면 가장 긴 토큰 (100자 이상)
            long_tokens = [t for t in all_tokens if len(t) > 100]
            if long_tokens:
                token = long_tokens[0]
                print(f"[OK] 토큰 발견 (길이: {len(token)})")
                return token

            print("[WARNING] 토큰 없이 진행")
            return None

        except Exception as e:
            print(f"[WARNING] 토큰 추출 실패: {e}")
            return None
    
    def fetch_breaking_news_api(self):
        """API로 Breaking News 목록 가져오기"""
        try:
            if not self.bearer_token:
                self.bearer_token = self.extract_bearer_token()
            
            print(f"\n[INFO] API 호출 중...")

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
                'Origin': 'https://www.investing.com',
                'Referer': 'https://www.investing.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }

            # Bearer 토큰이 있을 때만 Authorization 헤더 추가
            if self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'

            response = self.scraper.get(self.api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                print(f"[OK] API로부터 {len(articles)}개 기사 수신\n")
                
                # 기사 정보 파싱
                parsed_articles = []
                for article in articles:
                    # 메인 이미지 추출
                    main_image = None
                    media = article.get('media', [])
                    for m in media:
                        if m.get('purpose') == 'main_image':
                            main_image = m.get('url')
                            break
                    
                    # URL 생성
                    link = article.get('link', '')
                    full_url = f"{self.base_url}{link}" if link.startswith('/') else link
                    
                    # 관련 주식 ID 추출
                    instruments = article.get('instruments') or []
                    instrument_ids = [inst['id'] for inst in instruments if inst and inst.get('primary_tag')]
                    
                    parsed_articles.append({
                        'id': article.get('id'),
                        'title': article.get('title', ''),
                        'url': full_url,
                        'summary': article.get('body', ''),  # API 요약
                        'image_url': main_image,
                        'instrument_ids': instrument_ids[:5],  # 최대 5개만
                        'published': article.get('published_at', ''),
                    })
                
                return parsed_articles
            else:
                print(f"[ERROR] API 호출 실패 (코드: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"[ERROR] API 호출 실패: {e}")
            return None
    
    def fetch_full_article_content(self, url):
        """실제 기사 페이지에서 전체 본문 크롤링"""
        try:
            print(f"  - 전체 본문 크롤링 중...")
            time.sleep(1)

            # 한국어 사이트와 영어 사이트 모두 시도
            urls_to_try = [
                url.replace('www.investing.com', 'kr.investing.com'),  # 한국어 우선
                url  # 영어 원본
            ]

            for try_url in urls_to_try:
                try:
                    response = self.scraper.get(try_url, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'lxml')

                    # __NEXT_DATA__에서 전체 기사 데이터 추출
                    next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})

                    if next_data_script:
                        try:
                            import json
                            data = json.loads(next_data_script.string)

                            # 현재 기사의 본문을 찾기 위해 articleStore를 우선 탐색
                            def find_article_body(obj, depth=0):
                                if depth > 10:
                                    return None

                                if isinstance(obj, dict):
                                    # articleStore나 article 키를 찾아서 그 안의 body를 우선
                                    if 'articleStore' in obj or 'article' in obj:
                                        article_obj = obj.get('articleStore') or obj.get('article')
                                        if isinstance(article_obj, dict):
                                            body = article_obj.get('body', '')
                                            if isinstance(body, str) and len(body) > 500:
                                                return {'title': article_obj.get('title', ''), 'body': body}

                                    # 일반 body 검색 (길이가 충분히 긴 것만)
                                    if 'body' in obj and 'title' in obj:
                                        body = obj.get('body', '')
                                        if isinstance(body, str) and len(body) > 500:
                                            return {'title': obj.get('title', ''), 'body': body}

                                    # 재귀 탐색
                                    for v in obj.values():
                                        result = find_article_body(v, depth+1)
                                        if result:
                                            return result

                                elif isinstance(obj, list):
                                    for item in obj:
                                        result = find_article_body(item, depth+1)
                                        if result:
                                            return result

                                return None

                            article_data = find_article_body(data)

                            if article_data and article_data.get('body'):
                                title = article_data.get('title', '')
                                body_html = article_data['body']

                                # HTML을 텍스트로 변환
                                body_soup = BeautifulSoup(body_html, 'lxml')

                                # 본문 텍스트 추출
                                paragraphs = body_soup.find_all(['p', 'h2', 'h3', 'li'])
                                content_parts = []

                                for p in paragraphs:
                                    text = p.get_text().strip()
                                    # 의미있는 문단만
                                    if text and len(text) > 15:
                                        # 광고성 문구 필터링
                                        skip_phrases = ['subscribe', 'newsletter', 'sign up', 'click here',
                                                       '구독', '뉴스레터', '가입']
                                        if not any(skip.lower() in text.lower() for skip in skip_phrases):
                                            content_parts.append(text)

                                content = '\n\n'.join(content_parts)

                                # 본문 검증
                                if content and self.is_valid_article_content(content):
                                    print(f"  - __NEXT_DATA__에서 본문 추출 완료 ({len(content)} 자)")
                                    return title, content
                                elif content:
                                    print(f"  - __NEXT_DATA__ 결과가 유효하지 않음 (법적 고지 등)")
                                    # 다음 URL 시도
                                    continue

                        except Exception as e:
                            print(f"  [WARNING] __NEXT_DATA__ 파싱 실패: {e}")

                    # 이 URL에서 성공했다면 Readability 시도하지 않고 다음 URL로
                    # (한국어에서 실패하면 영어 시도)

                except Exception as e:
                    # 404나 다른 에러면 다음 URL 시도
                    if '404' in str(e):
                        print(f"  - 한국어 페이지 없음, 영어 페이지 시도...")
                        continue
                    print(f"  [WARNING] 크롤링 실패 ({try_url}): {e}")
                    continue
            
            # Fallback: Readability 사용
            print(f"  - Readability 방식으로 시도...")
            doc = Document(response.text)
            title = doc.title()
            content_html = doc.summary()

            soup2 = BeautifulSoup(content_html, 'lxml')
            paragraphs = soup2.find_all(['p', 'h2', 'h3'])
            content_parts = []

            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    content_parts.append(text)

            content = '\n\n'.join(content_parts)

            # Readability 결과 검증
            if content and self.is_valid_article_content(content):
                print(f"  - Readability로 본문 추출 ({len(content)} 자)")
                return title, content
            elif content:
                print(f"  - Readability 결과가 유효하지 않음 (법적 고지 등)")

            return None, None
            
        except Exception as e:
            print(f"  [WARNING] 본문 크롤링 실패: {e}")
            return None, None
    
    def fetch_instrument_info(self, instrument_ids):
        """관련 주식 정보 가져오기"""
        if not instrument_ids:
            return []
        
        try:
            print(f"  - 관련 주식 정보 조회 중 ({len(instrument_ids)}개)...")
            
            instruments_info = []
            # 각 주식 ID를 개별적으로 조회
            for inst_id in instrument_ids[:3]:  # 최대 3개만
                try:
                    url = f"{self.instrument_api_url}?instrument_ids={inst_id}"
                    response = self.scraper.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            inst = data[0]
                            instruments_info.append({
                                'id': inst.get('id'),
                                'name': inst.get('long_name', inst.get('short_name', '')),
                                'symbol': inst.get('symbol', ''),
                                'exchange_id': inst.get('exchange_id'),
                                'price': inst.get('price', {}),
                                'link': f"{self.base_url}{inst.get('link', '')}" if inst.get('link') else '',
                            })
                    
                    time.sleep(0.3)  # Rate limiting
                except:
                    continue
            
            print(f"  - 주식 정보 조회 완료 ({len(instruments_info)}개)")
            return instruments_info
            
        except Exception as e:
            print(f"  [WARNING] 주식 정보 조회 실패: {e}")
            return []
    
    def is_valid_article_content(self, text):
        """본문이 유효한 기사 내용인지 검증"""
        if not text or len(text) < 200:
            return False

        # 법적 고지사항이나 불필요한 내용 필터링
        invalid_keywords = [
            'risk warning', 'disclaimer', '리스크 고지', '면책 조항',
            'fusion media', '판권소유', 'all rights reserved',
            'terms and conditions', '이용약관',
            'privacy policy', '개인정보 보호정책'
        ]

        # 텍스트 앞부분 500자를 검사 (법적 고지가 앞에 오는 경우가 많음)
        text_start = text[:500].lower()

        # 여러 개의 invalid 키워드가 포함되어 있으면 법적 고지로 판단
        keyword_count = sum(1 for keyword in invalid_keywords if keyword.lower() in text_start)

        if keyword_count >= 2:
            print(f"  [WARNING] 법적 고지사항으로 판단되어 스킵 (키워드 {keyword_count}개 발견)")
            return False

        # 전체 텍스트에서 법적 키워드 비율 확인
        total_text_lower = text.lower()
        legal_word_count = sum(total_text_lower.count(keyword.lower()) for keyword in invalid_keywords)

        # 텍스트가 짧은데 법적 키워드가 많으면 의심
        if len(text) < 1000 and legal_word_count >= 5:
            print(f"  [WARNING] 법적 고지사항 비율이 높아 스킵")
            return False

        return True

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
    
    def clean_title(self, title):
        """제목에서 출처 정보 제거"""
        if not title:
            return title
        
        # "By Investing.com", "By InvestingPro" 등 패턴 제거
        patterns = [
            r'\s*By\s+Investing\.com\s*$',
            r'\s*By\s+InvestingPro\s*$',
            r'\s*-\s*Investing\.com\s*$',
            r'\s*-\s*InvestingPro\s*$',
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def convert_tickers_to_badges(self, text, instruments_info=None):
        """
        티커 심볼을 실시간 뱃지로 변환
        API 데이터 또는 동적 검색으로 instrument_id 조회
        """
        # 패턴: (KS:005930), (NASDAQ:NVDA), (TYO:9984) 등
        pattern = r'\(([A-Z]+):([A-Z0-9]+)\)'

        # instrument 정보로부터 symbol -> id 매핑 생성
        symbol_to_id = {}
        if instruments_info:
            for inst in instruments_info:
                symbol = inst.get('symbol')
                inst_id = inst.get('id')
                if symbol and inst_id:
                    symbol_to_id[symbol] = inst_id

        def replace_ticker(match):
            exchange = match.group(1)
            symbol = match.group(2)
            full_ticker = f"{exchange}:{symbol}"

            # 1. API 데이터에서 먼저 조회
            instrument_id = symbol_to_id.get(symbol)

            # 2. 없으면 검색 API로 동적 조회
            if not instrument_id:
                search_result = self.search_instrument(symbol)
                if search_result and search_result.get('id'):
                    instrument_id = search_result['id']

            # 3. 찾지 못하면 해당 텍스트를 제거
            if not instrument_id:
                return ''

            # HTML 마크업으로 변환
            return f'<span class="stock-ticker" data-ticker="{full_ticker}" data-exchange="{exchange}" data-symbol="{symbol}" data-instrument-id="{instrument_id}">({full_ticker})</span>'

        return re.sub(pattern, replace_ticker, text)
    
    def create_post(self, article, index):
        """완전한 Jekyll 포스트 생성"""
        try:
            original_title = article.get('title', '').strip()
            article_url = article.get('url', '')
            image_url = article.get('image_url', '')
            
            if not original_title or not article_url:
                return False
            
            print(f"\n{'='*70}")
            print(f"[{index}] {original_title[:50]}...")
            print(f"{'='*70}")
            
            # 1. 본문 가져오기
            # API 요약을 먼저 사용하고, 필요시 크롤링 시도
            summary_content = article.get('summary', '')
            full_title = None
            full_content = summary_content
            
            # 요약이 너무 짧으면 크롤링 시도
            if len(summary_content) < 100:
                print(f"  - 요약이 짧아 전체 본문 크롤링 시도...")
                full_title, crawled_content = self.fetch_full_article_content(article_url)
                if crawled_content and len(crawled_content) > len(summary_content):
                    full_content = crawled_content
                    print(f"  - 크롤링 성공 ({len(crawled_content)} 자)")
                else:
                    print(f"  - 크롤링 실패, API 요약 사용")
            else:
                print(f"  - API 요약 사용 ({len(summary_content)} 자)")
            
            if not full_content or len(full_content) < 50:
                print(f"  [SKIP] 충분한 본문이 없음")
                return False
            
            # 2. 관련 주식 정보
            instruments = self.fetch_instrument_info(article.get('instrument_ids', []))
            
            # 3. 제목 결정 및 번역
            title_to_use = full_title if full_title else original_title
            
            print(f"  - 제목 번역 중...")
            title_kr = self.translate_to_korean(title_to_use)
            
            # 제목에서 출처 정보 제거
            title_kr = self.clean_title(title_kr)
            
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
            
            # 5. 요약 생성 (티커 변환 전, 종목 코드 제거)
            excerpt_text = content_kr[:200] if len(content_kr) > 200 else content_kr
            # 종목 코드 패턴 제거 (예: (KS:005930), (NASDAQ:NVDA))
            excerpt_clean = re.sub(r'\([A-Z]+:[A-Z0-9]+\)', '', excerpt_text)
            # 연속된 공백 정리
            excerpt_clean = re.sub(r'\s+', ' ', excerpt_clean).strip()
            excerpt = excerpt_clean + "..." if len(content_kr) > 200 else excerpt_clean
            
            # 5.5. 티커 심볼을 실시간 뱃지로 변환 (excerpt 생성 후)
            content_kr = self.convert_tickers_to_badges(content_kr, instruments)
            
            # 6. 주식 정보 마크다운 생성 (front matter에 포함되기 때문에 본문은 생략)
            # instruments_md = ""
            # if instruments:
            #     instruments_md = "\n\n## 📈 관련 주식\n\n"
            #     for inst in instruments:
            #         name = inst.get('name', '')
            #         symbol = inst.get('symbol', '')
            #         price_info = inst.get('price', {})
            #         link = inst.get('link', '')
                    
            #         last_price = price_info.get('last', 0)
            #         change = price_info.get('change', 0)
            #         change_percent = price_info.get('change_percent', 0)
                    
            #         # 등락 아이콘
            #         icon = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"
                    
            #         instruments_md += f"### {icon} [{name} ({symbol})]({link})\n\n"
            #         instruments_md += f"- **현재가**: {last_price:,.2f}\n"
            #         instruments_md += f"- **변동**: {change:+.2f} ({change_percent:+.2f}%)\n\n"
            
            # 7. 날짜
            pub_date = datetime.now()
            date_str = pub_date.strftime('%Y-%m-%d')

            # 8. 파일명 생성
            filename_base = self.sanitize_filename(title_kr)
            if not filename_base or len(filename_base) < 5:
                filename_base = self.sanitize_filename(original_title)

            filename = f"{date_str}-{filename_base}.md"
            filepath = self.posts_dir / filename

            # 9. 중복 판단: front matter의 article_id로 확인
            article_id = article.get('id', '')
            is_duplicate = False

            if filepath.exists():
                # 파일이 존재하면 front matter에서 article_id 확인
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                        # front matter에서 article_id 추출
                        import re as regex_module
                        match = regex_module.search(r'article_id:\s*["\']?([^"\'\n]+)["\']?', existing_content)
                        if match:
                            existing_article_id = match.group(1)
                            if existing_article_id == article_id:
                                is_duplicate = True
                except:
                    pass

            if is_duplicate:
                print(f"  [SKIP] 중복 기사 (ID: {article_id}): {filename}")
                return False
            
            # 10. Jekyll Front Matter 생성
            image_line = f'image: "{image_url}"\n' if image_url else ''

            # YAML 이스케이프: 작은따옴표 사용 (더 안전)
            title_escaped = title_kr.replace("'", "''")
            excerpt_escaped = excerpt.replace("'", "''")

            # 주식 태그 생성 (symbol과 instrument_id 포함)
            stock_tags = []
            if instruments:
                for inst in instruments:
                    symbol = inst.get('symbol', '')
                    inst_id = inst.get('id', '')
                    exchange_id = inst.get('exchange_id', '')
                    if symbol and inst_id:
                        stock_tags.append({
                            'symbol': symbol,
                            'instrument_id': inst_id,
                            'exchange_id': exchange_id
                        })

            # YAML 형식으로 stock_tags 생성
            stock_tags_yaml = ""
            if stock_tags:
                stock_tags_yaml = "stock_tags:\n"
                for tag in stock_tags:
                    stock_tags_yaml += f"  - symbol: {tag['symbol']}\n"
                    stock_tags_yaml += f"    instrument_id: {tag['instrument_id']}\n"
                    if tag['exchange_id']:
                        stock_tags_yaml += f"    exchange_id: {tag['exchange_id']}\n"

            front_matter = f"""---
layout: post
title: '{title_escaped}'
date: {pub_date.strftime('%Y-%m-%d %H:%M:%S +0900')}
categories: [Financial]
author: "Investing.com"
article_id: "{article_id}"
{image_line}excerpt: '{excerpt_escaped}'
{stock_tags_yaml}---

{content_kr}


---
"""

            # 11. 파일 저장
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
        print("Investing.com 완전판 크롤러 (한국어)")
        print("Breaking News + 전체 본문 + 이미지 + 주식 정보")
        print("=" * 70)
        
        # API로 Breaking news 목록 가져오기
        articles = self.fetch_breaking_news_api()
        
        if not articles:
            print("\n[ERROR] API 호출 실패")
            return
        
        print(f"총 {len(articles)}개 기사 발견, 최대 {limit}개 처리\n")
        
        # 각 기사 처리
        created_count = 0
        for i, article in enumerate(articles[:limit], 1):
            try:
                if self.create_post(article, i):
                    created_count += 1
            except Exception as e:
                print(f"[ERROR] 처리 중 오류: {e}")
                continue

        print("\n" + "=" * 70)
        print(f"OK: 완료 - {created_count}개의 포스트 생성됨")
        print("=" * 70)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Investing.com 완전판 크롤러 (한국어)')
    parser.add_argument('--limit', type=int, default=5, help='가져올 기사 수 (기본: 5)')
    args = parser.parse_args()
    
    crawler = InvestingCompleteKR()
    crawler.run(limit=args.limit)


if __name__ == "__main__":
    main()

