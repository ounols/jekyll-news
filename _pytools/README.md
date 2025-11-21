# Jekyll News - Python Tools

Jekyll 블로그 자동화를 위한 Python 도구 모음

## 📁 구조

```
_pytools/
├── venv/                         # Python 가상환경
├── requirements.txt              # Python 패키지 목록
├── investing_complete_kr.py      # Investing.com 뉴스 크롤러 (최종 버전)
├── ticker_cache.json             # 종목 코드 → instrument ID 캐시
└── README.md                     # 이 파일
```

## 🚀 설치

### 1. 가상환경 생성 및 활성화

```powershell
# 가상환경 생성
cd _pytools
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 가상환경 활성화 (Windows cmd)
.\venv\Scripts\activate.bat
```

### 2. 패키지 설치

```powershell
pip install -r requirements.txt
```

## 📰 Investing.com 뉴스 크롤러

Investing.com에서 최신 금융 뉴스를 가져와 Jekyll 포스트로 자동 생성합니다.

### 사용법

```powershell
# 기본: 5개의 뉴스 가져오기
python investing_complete_kr.py

# 특정 개수 지정
python investing_complete_kr.py --limit 10

# 더 많은 뉴스 가져오기
python investing_complete_kr.py --limit 20
```

### 기능

- ✅ **Breaking News API 사용** - 최신 속보 자동 수집
- ✅ **전체 본문 크롤링** - kr.investing.com에서 완전한 기사 내용 추출
- ✅ **자동 한국어 번역** - Google Translator API 사용
- ✅ **관련 주식 정보** - 실시간 주가, 변동률 포함
- ✅ **실시간 주식 배지** - JavaScript로 동적 업데이트 (data-instrument-id 자동 포함)
- ✅ **Ticker 캐시 시스템** - 종목 코드 → instrument ID 자동 매핑
- ✅ **이미지 자동 포함** - 메인 이미지 URL 추출
- ✅ **Cloudflare 우회** - cloudscraper로 안정적인 크롤링
- ✅ **중복 방지** - 이미 존재하는 파일은 건너뜀

### 🎯 Ticker 캐시 시스템

본문에 언급된 종목 코드(예: NASDAQ:NVDA)를 실시간 주식 배지로 표시하기 위해 `ticker_cache.json`을 사용합니다.

#### 새로운 종목 추가하기

크롤러 실행 후 "찾지 못한 티커" 경고가 나타나면:

1. **Investing.com에서 종목 검색**
   - `https://www.investing.com/equities/[종목명]` 접속
   
2. **Instrument ID 찾기**
   ```python
   # _pytools에서 실행
   python -c "import cloudscraper; r = cloudscraper.create_scraper().get('https://www.investing.com/equities/[종목-url]'); import re; print(re.findall(r'\"instrument_id\"\s*:\s*(\d+)', r.text)[0])"
   ```

3. **ticker_cache.json에 추가**
   ```json
   {
     "tickers": {
       "AAPL": 6408,
       "새종목": 12345  // 여기에 추가
     }
   }
   ```

### 생성되는 포스트 형식

```markdown
---
layout: post
title: '기사 제목'
date: 2025-11-21 14:25:08 +0900
categories: [Financial]
author: "Investing.com"
image: "이미지 URL"
excerpt: '기사 요약 (종목 코드 제거됨)'
---

기사 본문...

<span class="stock-ticker" data-ticker="NASDAQ:NVDA" data-exchange="NASDAQ" data-symbol="NVDA" data-instrument-id="6497">(NASDAQ:NVDA)</span>

## 📈 관련 주식

### 🔺 [NVIDIA Corporation (NVDA)](링크)
- **현재가**: 180.64
- **변동**: +5.88 (+3.15%)

---

**원문**: [제목](원문링크)
```

## 📦 필요한 패키지

- `cloudscraper>=1.2.71` - Cloudflare 보호 우회
- `beautifulsoup4>=4.12.0` - HTML 파싱
- `lxml>=4.9.0` - 빠른 HTML/XML 처리
- `requests>=2.31.0` - HTTP 요청

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

### 기사를 찾을 수 없음

Investing.com의 HTML 구조가 변경된 경우일 수 있습니다. 
이슈를 제보해주세요.

## 💡 향후 추가 예정

- [ ] 다른 뉴스 소스 추가 (예: Bloomberg, Reuters)
- [ ] 스케줄러 기능 (자동 실행)
- [ ] 이미지 다운로드 및 로컬 저장
- [ ] 카테고리 자동 분류 (AI 기반)
- [ ] 한글 번역 기능

## 📝 라이선스

MIT License

---

Made with ❤️ for Jekyll News Automation

