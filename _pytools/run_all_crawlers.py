#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 크롤러 실행기
- 모든 뉴스 크롤러를 한 번에 실행
- 각 소스별로 개별 실행 가능
"""

import argparse
import sys

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def run_investing(limit):
    """Investing.com 크롤러 실행"""
    try:
        from investing_complete_kr import InvestingCompleteKR
        print("\n" + "=" * 70)
        print("🔵 Investing.com 크롤러 시작")
        print("=" * 70)
        crawler = InvestingCompleteKR()
        crawler.run(limit=limit)
        return True
    except Exception as e:
        print(f"[ERROR] Investing.com 크롤러 실패: {e}")
        return False


def run_yahoo(limit):
    """Yahoo Finance 크롤러 실행"""
    try:
        from yahoo_finance_kr import YahooFinanceKR
        print("\n" + "=" * 70)
        print("🟣 Yahoo Finance 크롤러 시작")
        print("=" * 70)
        crawler = YahooFinanceKR()
        crawler.run(limit=limit)
        return True
    except Exception as e:
        print(f"[ERROR] Yahoo Finance 크롤러 실패: {e}")
        return False


def run_marketwatch(limit):
    """MarketWatch 크롤러 실행"""
    try:
        from marketwatch_kr import MarketWatchKR
        print("\n" + "=" * 70)
        print("🟢 MarketWatch 크롤러 시작")
        print("=" * 70)
        crawler = MarketWatchKR()
        crawler.run(limit=limit)
        return True
    except Exception as e:
        print(f"[ERROR] MarketWatch 크롤러 실패: {e}")
        return False


def run_cnbc(limit):
    """CNBC 크롤러 실행"""
    try:
        from cnbc_kr import CNBCKR
        print("\n" + "=" * 70)
        print("🟠 CNBC 크롤러 시작")
        print("=" * 70)
        crawler = CNBCKR()
        crawler.run(limit=limit)
        return True
    except Exception as e:
        print(f"[ERROR] CNBC 크롤러 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='통합 뉴스 크롤러 - 미국 증시 뉴스 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_all_crawlers.py                    # 모든 크롤러 실행 (각 5개씩)
  python run_all_crawlers.py --limit 10         # 모든 크롤러 실행 (각 10개씩)
  python run_all_crawlers.py --source investing # Investing.com만 실행
  python run_all_crawlers.py --source yahoo     # Yahoo Finance만 실행
  python run_all_crawlers.py --source mw        # MarketWatch만 실행
  python run_all_crawlers.py --source cnbc      # CNBC만 실행
  python run_all_crawlers.py --source all       # 모든 소스 실행 (기본값)

지원 소스:
  investing  - Investing.com Breaking News
  yahoo      - Yahoo Finance Stock Market News
  mw         - MarketWatch Latest News
  cnbc       - CNBC Markets & Investing News
  all        - 모든 소스 (기본값)
        """
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=5,
        help='각 소스에서 가져올 기사 수 (기본: 5)'
    )

    parser.add_argument(
        '--source', '-s',
        type=str,
        default='all',
        choices=['all', 'investing', 'yahoo', 'mw', 'marketwatch', 'cnbc'],
        help='크롤링할 소스 선택 (기본: all)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("📰 통합 뉴스 크롤러 - 미국 증시 뉴스 수집")
    print("=" * 70)
    print(f"설정: 소스={args.source}, 기사수={args.limit}")

    results = {}

    if args.source == 'all':
        # 모든 크롤러 실행
        results['Investing.com'] = run_investing(args.limit)
        results['Yahoo Finance'] = run_yahoo(args.limit)
        results['MarketWatch'] = run_marketwatch(args.limit)
        results['CNBC'] = run_cnbc(args.limit)
    elif args.source == 'investing':
        results['Investing.com'] = run_investing(args.limit)
    elif args.source == 'yahoo':
        results['Yahoo Finance'] = run_yahoo(args.limit)
    elif args.source in ['mw', 'marketwatch']:
        results['MarketWatch'] = run_marketwatch(args.limit)
    elif args.source == 'cnbc':
        results['CNBC'] = run_cnbc(args.limit)

    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 실행 결과 요약")
    print("=" * 70)

    for source, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {source}: {status}")

    success_count = sum(1 for s in results.values() if s)
    total_count = len(results)

    print("-" * 70)
    print(f"  총 {total_count}개 중 {success_count}개 성공")
    print("=" * 70)


if __name__ == "__main__":
    main()
