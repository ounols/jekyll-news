/**
 * 실시간 주식 티커 뱃지
 * Investing.com 검색 API + 실시간 가격 API를 사용하여 실시간 주가 정보를 표시
 */

(function() {
  'use strict';

  // 검색 결과 캐시 (같은 심볼 중복 요청 방지)
  const instrumentCache = new Map();

  // Investing.com 검색 API로 종목 정보 조회
  async function searchInstrument(symbol) {
    // 캐시 확인
    if (instrumentCache.has(symbol)) {
      return instrumentCache.get(symbol);
    }

    const url = 'https://kr.investing.com/search/service/search';

    try {
      console.log('[Stock Ticker] 종목 검색 중:', symbol);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new URLSearchParams({
          search_text: symbol,
          term: symbol,
          country_id: '0',
          tab_id: 'All'
        })
      });

      if (!response.ok) {
        console.error('[Stock Ticker] 검색 API 오류:', response.status);
        return null;
      }

      const data = await response.json();
      const results = data.All || [];

      if (results.length > 0) {
        const result = results[0];
        const instrumentInfo = {
          id: result.pair_ID,
          symbol: result.symbol,
          name: result.name,
          exchange: result.exchange_popular_symbol
        };

        // 캐시에 저장
        instrumentCache.set(symbol, instrumentInfo);
        console.log('[Stock Ticker] 검색 성공:', symbol, '->', instrumentInfo.id);
        return instrumentInfo;
      }

      console.warn('[Stock Ticker] 검색 결과 없음:', symbol);
      return null;

    } catch (error) {
      console.error('[Stock Ticker] 검색 API 호출 실패:', error);
      return null;
    }
  }

  // API 호출 함수 (단일 instrument - 실시간 가격 조회)
  async function fetchSingleStock(instrumentId) {
    const url = `https://endpoints.investing.com/pd-instruments/v1/instruments?instrument_ids=${instrumentId}`;
    console.log('[Stock Ticker] 가격 API 호출:', instrumentId);

    try {
      const response = await fetch(url);
      console.log('[Stock Ticker] 가격 API 응답 상태:', response.status);
      if (!response.ok) {
        const text = await response.text();
        console.error('[Stock Ticker] 오류 응답:', text);
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data[0]; // 첫 번째 항목 반환
    } catch (error) {
      console.error('[Stock Ticker] 가격 데이터 가져오기 실패:', error);
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

  // Post-Card 배지 업데이트 함수
  async function updateCardBadges() {
    console.log('[Stock Ticker] Post-Card 배지 업데이트 시작');
    const cardBadges = document.querySelectorAll('.stock-badge--card');
    console.log('[Stock Ticker] 발견된 Post-Card 배지:', cardBadges.length);

    if (cardBadges.length === 0) {
      console.log('[Stock Ticker] Post-Card 배지가 없습니다');
      return;
    }

    const updatePromises = [];

    cardBadges.forEach(element => {
      const symbol = element.dataset.symbol;
      const instrumentId = element.dataset.instrumentId;

      console.log('[Stock Ticker] Post-Card 배지 처리:', symbol, 'ID:', instrumentId);

      if (instrumentId) {
        updatePromises.push(
          fetchSingleStock(instrumentId).then(data => {
            if (data) {
              const change = data.price?.change || 0;
              const changePercent = data.price?.change_percent || 0;
              const isUp = change > 0;
              const isDown = change < 0;
              const colorClass = isUp ? 'badge-up' : isDown ? 'badge-down' : 'badge-neutral';
              const sign = isUp ? '+' : '';

              // Post-Card 배지 업데이트
              element.className = `stock-badge stock-badge--card ${colorClass}`;
              element.textContent = `${symbol} ${sign}${changePercent.toFixed(2)}%`;
              element.classList.add('ticker-loaded');

              console.log('[Stock Ticker] Post-Card 배지 업데이트 완료:', symbol);
            }
          })
        );
      }
    });

    await Promise.all(updatePromises);
    console.log('[Stock Ticker] Post-Card 배지 업데이트 완료');
  }

  // Post 페이지 메타 배지 업데이트 함수
  async function updatePostBadges() {
    console.log('[Stock Ticker] Post 메타 배지 업데이트 시작');
    const postBadges = document.querySelectorAll('.stock-badge--post');
    console.log('[Stock Ticker] 발견된 Post 메타 배지:', postBadges.length);

    if (postBadges.length === 0) {
      console.log('[Stock Ticker] Post 메타 배지가 없습니다');
      return;
    }

    const updatePromises = [];

    postBadges.forEach(element => {
      const symbol = element.dataset.symbol;
      const instrumentId = element.dataset.instrumentId;

      console.log('[Stock Ticker] Post 메타 배지 처리:', symbol, 'ID:', instrumentId);

      if (instrumentId) {
        updatePromises.push(
          fetchSingleStock(instrumentId).then(data => {
            if (data) {
              const change = data.price?.change || 0;
              const changePercent = data.price?.change_percent || 0;
              const isUp = change > 0;
              const isDown = change < 0;
              const colorClass = isUp ? 'badge-up' : isDown ? 'badge-down' : 'badge-neutral';
              const sign = isUp ? '+' : '';

              // Post 메타 배지 업데이트
              element.className = `stock-badge stock-badge--post ${colorClass}`;
              element.textContent = `${symbol} ${sign}${changePercent.toFixed(2)}%`;
              element.classList.add('ticker-loaded');

              console.log('[Stock Ticker] Post 메타 배지 업데이트 완료:', symbol);
            }
          })
        );
      }
    });

    await Promise.all(updatePromises);
    console.log('[Stock Ticker] Post 메타 배지 업데이트 완료');
  }

  // 모든 티커 업데이트
  async function updateAllTickers() {
    console.log('[Stock Ticker] 초기화 시작');
    const tickerElements = document.querySelectorAll('.stock-ticker');
    console.log('[Stock Ticker] 발견된 티커:', tickerElements.length);

    // 모든 티커 요소 처리
    const updatePromises = [];

    tickerElements.forEach(element => {
      const symbol = element.dataset.symbol;
      const exchange = element.dataset.exchange;

      console.log('[Stock Ticker] 처리 중:', symbol, 'Exchange:', exchange);

      // 1. data-instrument-id 속성에서 직접 가져오기 (우선순위)
      let instrumentId = element.dataset.instrumentId;

      if (instrumentId) {
        // instrument_id가 있으면 바로 가격 조회
        console.log('[Stock Ticker] ID 사용:', symbol, '->', instrumentId);
        updatePromises.push(
          fetchSingleStock(instrumentId).then(data => {
            if (data) {
              const badge = createBadge(data);
              element.innerHTML = badge;
              element.classList.add('ticker-loaded');
            }
          })
        );
      } else {
        // instrument_id가 없으면 검색 API로 동적 조회
        console.log('[Stock Ticker] 종목 검색 필요:', symbol);
        updatePromises.push(
          searchInstrument(symbol).then(instrumentInfo => {
            if (instrumentInfo && instrumentInfo.id) {
              // 검색 성공 → 가격 조회
              console.log('[Stock Ticker] 검색 성공, 가격 조회:', instrumentInfo.id);
              return fetchSingleStock(instrumentInfo.id).then(data => {
                if (data) {
                  const badge = createBadge(data);
                  element.innerHTML = badge;
                  element.classList.add('ticker-loaded');
                }
              });
            } else {
              console.warn('[Stock Ticker] 검색 실패:', symbol);
            }
          })
        );
      }
    });

    // 모든 업데이트 완료 대기
    if (updatePromises.length > 0) {
      await Promise.all(updatePromises);
    }
    console.log('[Stock Ticker] 모든 티커 업데이트 완료');

    // Post-Card 배지도 업데이트
    await updateCardBadges();

    // Post 메타 배지도 업데이트
    await updatePostBadges();
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

