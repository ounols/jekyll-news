# GitHub Actions 워크플로우

이 디렉토리에는 Jekyll 블로그의 자동화 워크플로우가 포함되어 있습니다.

## 워크플로우 설명

### 1. Auto Post Generation (`auto-post.yml`)

**목적**: Investing.com에서 Breaking News를 자동으로 크롤링하여 포스트를 생성합니다.

**스케줄**:
- 매 30분마다 자동 실행 (UTC 기준)
- 수동 실행 가능 (GitHub UI에서 "Run workflow" 클릭)

**실행 과정**:
1. 저장소 체크아웃
2. Python 3.11 설정
3. 필요한 의존성 설치
   - `cloudscraper`: Cloudflare 우회
   - `beautifulsoup4`: HTML 파싱
   - `readability-lxml`: 본문 추출
   - `deep-translator`: 한국어 번역
4. `investing_complete_kr.py` 실행 (최대 5개 기사)
5. 새로운 포스트가 생성되면 자동 커밋 및 푸시

**변경사항 감지**:
- `_posts/` 디렉토리의 변경사항만 커밋
- 중복 기사는 자동으로 스킵됨
- 새로운 포스트만 깃허브에 푸시됨

**커밋 메시지**:
```
feat: Auto-generated posts from Investing.com

- Generated X new posts
- Timestamp: YYYY-MM-DD HH:MM:SS UTC
```

### 2. Build and Deploy Jekyll (`build-and-deploy.yml`)

**목적**: Jekyll 사이트를 빌드하고 GitHub Pages에 배포합니다.

**트리거**:
- `main` 브랜치에 푸시할 때
- 풀 리퀘스트가 생성/업데이트될 때

**실행 과정**:
1. 저장소 체크아웃
2. Ruby 3.2 설정
3. 번들 의존성 설치
4. Jekyll 빌드 (`_site/` 디렉토리 생성)
5. (main 브랜치 푸시인 경우) GitHub Pages에 배포

## 주요 기능

### 자동 포스트 생성
- Investing.com의 Breaking News API 사용
- 새로운 기사 감지 시 자동 포스트 생성
- 중복 기사 방지 (article_id 기반)
- 한국어 번역 지원
- 관련 주식 정보 자동 추가

### 자동 배포
- 포스트 생성 후 자동으로 GitHub Pages에 반영
- 빌드 실패 시 메일 알림 (GitHub 설정)

## 수동 실행

GitHub 웹 UI에서 워크플로우를 수동으로 실행할 수 있습니다:

1. **Actions** 탭 클릭
2. **Auto Post Generation** 선택
3. **Run workflow** 클릭
4. 실행 로그 확인

## 문제 해결

### 워크플로우가 실행되지 않음
- GitHub Pages 설정 확인
- 저장소 설정 → Actions에서 워크플로우 활성화 확인
- 스케줄 시간대 확인 (UTC 기준)

### 포스트가 생성되지 않음
- **Actions** 탭에서 실행 로그 확인
- Python 의존성 설치 성공 여부 확인
- Investing.com API 가용성 확인

### 배포 실패
- GitHub Pages 설정 확인
- `_site/` 디렉토리 생성 여부 확인
- Jekyll 빌드 오류 로그 확인

## 설정 커스터마이징

### 포스트 생성 주기 변경

`auto-post.yml`의 `cron` 값을 수정:

```yaml
schedule:
  - cron: '0 */6 * * *'  # 6시간마다
  - cron: '0 0 * * *'    # 매일 0시
  - cron: '0 * * * *'    # 매시간
```

Cron 표현식 가이드:
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (0 = Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

예시:
- `'*/30 * * * *'`: 30분마다
- `'0 */3 * * *'`: 3시간마다
- `'0 9 * * 1-5'`: 평일 09:00 (UTC)

### 한번에 가져올 기사 수 변경

`auto-post.yml`의 `run post generation` 단계에서:

```yaml
run: |
  cd _pytools
  python investing_complete_kr.py --limit 10  # 10개로 변경
```

## 로그 확인

각 워크플로우의 상세 로그는 GitHub UI의 **Actions** 탭에서 확인할 수 있습니다:

1. 워크플로우 이름 클릭
2. 실행 항목 클릭
3. 각 단계별 로그 확인
4. 실패 시 에러 메시지 확인

## 비용 고려사항

GitHub Actions는 public 저장소에서 무제한 무료이며, private 저장소의 경우:
- 월 2,000분의 실행 시간 무료
- 이 워크플로우는 월 약 40분 소비 (30분 간격 × 24시간 × 30일 ÷ 60)

## 보안

- Python 스크립트는 로컬에서 테스트 후 업로드 권장
- 민감한 정보는 GitHub Secrets에 저장
- 워크플로우 실행 권한 확인
