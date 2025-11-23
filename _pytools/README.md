# Jekyll News - Python Tools

Jekyll 블로그 자동화를 위한 Python 도구 모음

## 📁 구조

```
_pytools/
├── venv/                         # Python 가상환경
├── requirements.txt              # Python 패키지 목록
├── run_all_crawlers.py           # 통합 크롤러 실행기
├── investing_complete_kr.py      # Investing.com 뉴스 크롤러
├── yahoo_finance_kr.py           # Yahoo Finance 뉴스 크롤러
├── marketwatch_kr.py             # MarketWatch 뉴스 크롤러
├── cnbc_kr.py                    # CNBC 뉴스 크롤러
├── ticker_cache.json             # 종목 코드 → instrument ID 캐시
└── README.md                     # 이 파일
```

## 🚀 설치

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
cd _pytools
python -m venv venv

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 가상환경 활성화 (Windows cmd)
.\venv\Scripts\activate.bat
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## 📰 통합 크롤러 실행기

모든 뉴스 크롤러를 한 번에 실행하거나 개별 소스를 선택해서 실행할 수 있습니다.

### 사용법

```bash
# 모든 크롤러 실행 (각 소스당 5개씩)
python run_all_crawlers.py

# 기사 수 지정 (각 소스당 10개씩)
python run_all_crawlers.py --limit 10

# 특정 소스만 실행
python run_all_crawlers.py --source investing   # Investing.com만
python run_all_crawlers.py --source yahoo       # Yahoo Finance만
python run_all_crawlers.py --source mw          # MarketWatch만
python run_all_crawlers.py --source cnbc        # CNBC만
python run_all_crawlers.py --source all         # 모든 소스 (기본값)
```

### 지원 소스

| 소스 | 설명 | 파일명 |
|------|------|--------|
| `investing` | Investing.com Breaking News | investing_complete_kr.py |
| `yahoo` | Yahoo Finance Stock Market News | yahoo_finance_kr.py |
| `mw` | MarketWatch Latest News | marketwatch_kr.py |
| `cnbc` | CNBC Markets & Investing News | cnbc_kr.py |

---

## 📈 개별 크롤러

### 1. Investing.com 크롤러

Investing.com에서 최신 금융 뉴스를 가져와 Jekyll 포스트로 자동 생성합니다.

```bash
# 기본: 5개의 뉴스 가져오기
python investing_complete_kr.py

# 특정 개수 지정
python investing_complete_kr.py --limit 10
```

**특징:**
- Breaking News API 사용 (최신 속보 자동 수집)
- kr.investing.com에서 완전한 기사 내용 추출
- 관련 주식 정보 및 실시간 주가 포함
- Bearer Token 자동 추출

### 2. Yahoo Finance 크롤러

Yahoo Finance에서 주식 시장 뉴스를 가져옵니다.

```bash
python yahoo_finance_kr.py
python yahoo_finance_kr.py --limit 10
```

**특징:**
- Stock Market News 섹션에서 뉴스 수집
- Latest News 섹션 포함
- 본문에서 티커 심볼 자동 추출

### 3. MarketWatch 크롤러

MarketWatch에서 최신 금융 뉴스를 가져옵니다.

```bash
python marketwatch_kr.py
python marketwatch_kr.py --limit 10
```

**특징:**
- Latest News, Markets, Investing 섹션에서 뉴스 수집
- Dow Jones 산하 미디어의 고품질 기사
- 본문에서 티커 심볼 자동 추출

### 4. CNBC 크롤러

CNBC에서 주식 시장 및 투자 뉴스를 가져옵니다.

```bash
python cnbc_kr.py
python cnbc_kr.py --limit 10
```

**특징:**
- Markets, Investing, Technology 섹션에서 뉴스 수집
- 비디오/오디오 콘텐츠 자동 필터링
- 본문에서 티커 심볼 자동 추출

---

## 🎯 공통 기능

모든 크롤러는 다음 기능을 공유합니다:

- ✅ **자동 한국어 번역** - Google Translator API 사용
- ✅ **실시간 주식 배지** - data-instrument-id 포함 HTML 태그 생성
- ✅ **Ticker 캐시 시스템** - ticker_cache.json으로 종목 ID 매핑
- ✅ **Cloudflare 우회** - cloudscraper 사용
- ✅ **중복 방지** - 이미 존재하는 파일은 건너뜀
- ✅ **Readability Fallback** - 본문 추출 실패 시 대체 방법 사용

---

## 🎯 Ticker 캐시 시스템

본문에 언급된 종목 코드(예: $NVDA, AAPL)를 실시간 주식 배지로 표시하기 위해 `ticker_cache.json`을 사용합니다.

### 새로운 종목 추가하기

1. **Investing.com에서 종목 검색**
   - `https://www.investing.com/equities/[종목명]` 접속

2. **Instrument ID 찾기**
   ```python
   python -c "import cloudscraper; r = cloudscraper.create_scraper().get('https://www.investing.com/equities/[종목-url]'); import re; print(re.findall(r'\"instrument_id\"\s*:\s*(\d+)', r.text)[0])"
   ```

3. **ticker_cache.json에 추가**
   ```json
   {
     "tickers": {
       "AAPL": {"instrument_id": 6408},
       "새종목": {"instrument_id": 12345}
     }
   }
   ```

---

## 📝 생성되는 포스트 형식

```markdown
---
layout: post
title: '기사 제목'
date: 2025-11-23 14:25:08 +0900
categories: [Financial]
author: "소스명"
image: "이미지 URL"
excerpt: '기사 요약'
stock_tags:
  - symbol: NVDA
    instrument_id: 6497
---

기사 본문...

<span class="stock-ticker" data-ticker="NVDA" data-symbol="NVDA" data-instrument-id="6497">$NVDA</span>

---

*출처: [소스명](원문링크)*
```

---

## 📦 필요한 패키지

| 패키지 | 버전 | 용도 |
|--------|------|------|
| requests | >=2.31.0 | HTTP 요청 |
| cloudscraper | >=1.2.71 | Cloudflare 보호 우회 |
| beautifulsoup4 | >=4.12.0 | HTML 파싱 |
| lxml | >=4.9.0 | 빠른 HTML/XML 처리 |
| readability-lxml | >=0.8.1 | 본문 추출 |
| deep-translator | >=1.11.4 | 한국어 번역 |

---

## 🔧 트러블슈팅

### 403 Forbidden 에러

Cloudflare가 요청을 차단하는 경우입니다. `cloudscraper`가 이를 자동으로 처리하지만,
실패할 경우 잠시 기다린 후 다시 시도하세요.

### 인코딩 에러 (Windows)

Windows 콘솔에서 한글이 깨지는 경우, PowerShell에서 다음 명령을 실행하세요:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

또는 스크립트가 자동으로 처리합니다.

### 번역 실패

Google Translate API 제한에 걸린 경우입니다. 잠시 기다린 후 다시 시도하거나
`--limit` 옵션으로 기사 수를 줄여주세요.

### 본문을 찾을 수 없음

뉴스 사이트의 HTML 구조가 변경된 경우일 수 있습니다.
Readability fallback이 자동으로 시도되지만, 실패 시 이슈를 제보해주세요.

---

## 📝 라이선스

MIT License

---

Made with ❤️ for Jekyll News Automation
