/**
 * 실시간 주식 티커 뱃지
 * Investing.com API를 사용하여 실시간 주가 정보를 표시
 */

(function() {
  'use strict';

  // 주요 종목 티커 → instrument_id 매핑
  const TICKER_MAP = {
    // 한국
    '005930': '38081',  // 삼성전자
    '000660': '38088',  // SK하이닉스
    // 미국 (NASDAQ)
    'NVDA': '6497',     // NVIDIA
    'AAPL': '6408',     // Apple
    'MSFT': '20',       // Microsoft
    'GOOGL': '1057391', // Alphabet
    'TSLA': '13994',    // Tesla
    'META': '106640',   // Meta
    'AMZN': '6435',     // Amazon
    // 미국 (NYSE)
    'ARKK': '959230',   // ARK Innovation ETF
    'WMT': '7997',      // Walmart
    'JPM': '267',       // JPMorgan Chase
    'V': '40611',       // Visa
    'JNJ': '294',       // Johnson & Johnson
    // 대만
    '2330': '43430',    // TSMC
    '2317': '44237',    // Hon Hai (Foxconn)
    // 일본
    '9984': '35680',    // SoftBank
    '6857': '35838',    // Advantest
    '8035': '35703',    // Tokyo Electron
    // 홍콩
    '9888': '1055009',  // Baidu
    '9988': '1057420',  // Alibaba
    '0700': '20727',    // Tencent
    '0981': '44296',    // SMIC
    // 중국 (상하이)
    '688256': '1164029', // Cambricon
  };

  // API 호출 함수 (단일 instrument)
  async function fetchSingleStock(instrumentId) {
    const url = `https://endpoints.investing.com/pd-instruments/v1/instruments?instrument_ids=${instrumentId}`;
    console.log('[Stock Ticker] API URL:', url);
    
    try {
      const response = await fetch(url);
      console.log('[Stock Ticker] API 응답 상태:', response.status);
      if (!response.ok) {
        const text = await response.text();
        console.error('[Stock Ticker] 오류 응답:', text);
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data[0]; // 첫 번째 항목 반환
    } catch (error) {
      console.error('주식 데이터 가져오기 실패:', error);
      return null;
    }
  }
  
  // 여러 주식 데이터 가져오기
  async function fetchStockData(instrumentIds) {
    if (!instrumentIds || instrumentIds.length === 0) {
      return [];
    }

    // 각 instrument를 개별적으로 조회
    const promises = instrumentIds.map(id => fetchSingleStock(id));
    const results = await Promise.all(promises);
    
    // null이 아닌 것만 반환
    return results.filter(data => data !== null);
  }

  // 뱃지 HTML 생성
  function createBadge(data) {
    const price = data.price || {};
    const change = price.change || 0;
    const changePercent = price.change_percent || 0;
    const symbol = data.symbol || '';
    
    // 등락에 따른 색상 및 아이콘
    const isUp = change > 0;
    const isDown = change < 0;
    const colorClass = isUp ? 'badge-up' : isDown ? 'badge-down' : 'badge-neutral';
    const icon = isUp ? '▲' : isDown ? '▼' : '―';
    
    // 변동률 포맷팅
    const formattedChange = changePercent.toFixed(2);
    const sign = isUp ? '+' : '';
    
    return `<span class="stock-badge ${colorClass}">${symbol} ${icon} ${sign}${formattedChange}%</span>`;
  }

  // 모든 티커 업데이트
  async function updateAllTickers() {
    console.log('[Stock Ticker] 초기화 시작');
    const tickerElements = document.querySelectorAll('.stock-ticker');
    console.log('[Stock Ticker] 발견된 티커:', tickerElements.length);
    
    if (tickerElements.length === 0) {
      console.log('[Stock Ticker] 티커가 없습니다');
      return;
    }

    // instrument_id 수집
    const instrumentIds = [];
    const tickerDataMap = new Map();

    tickerElements.forEach(element => {
      const symbol = element.dataset.symbol;
      const exchange = element.dataset.exchange;
      
      console.log('[Stock Ticker] 처리 중:', symbol, exchange);
      
      // 1. data-instrument-id 속성에서 직접 가져오기 (우선순위)
      let instrumentId = element.dataset.instrumentId;
      
      // 2. 없으면 매핑 테이블에서 찾기 (fallback)
      if (!instrumentId) {
        instrumentId = TICKER_MAP[symbol];
      }
      
      if (instrumentId) {
        console.log('[Stock Ticker] ID 매핑:', symbol, '->', instrumentId);
        instrumentIds.push(instrumentId);
        tickerDataMap.set(instrumentId, element);
      } else {
        console.warn('[Stock Ticker] ID 없음:', symbol);
      }
    });

    if (instrumentIds.length === 0) {
      console.log('[Stock Ticker] instrument ID가 없습니다');
      return;
    }

    console.log('[Stock Ticker] API 호출 중, IDs:', instrumentIds);
    
    // API 호출
    const stockData = await fetchStockData(instrumentIds);
    console.log('[Stock Ticker] API 응답:', stockData.length, '개');

    // 각 티커 업데이트
    stockData.forEach(data => {
      const element = tickerDataMap.get(String(data.id));
      if (element) {
        const badge = createBadge(data);
        // 원래 텍스트 제거하고 뱃지만 표시
        element.innerHTML = badge;
        element.classList.add('ticker-loaded');
      }
    });
  }

  // 페이지 로드 시 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateAllTickers);
  } else {
    updateAllTickers();
  }

  // 5분마다 업데이트 (선택사항)
  setInterval(updateAllTickers, 5 * 60 * 1000);

})();

