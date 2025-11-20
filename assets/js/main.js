// Search Toggle
document.addEventListener('DOMContentLoaded', function() {
  const searchIcon = document.querySelector('.icon__search');
  const search = document.querySelector('.search');
  const searchOverlay = document.querySelector('.search__overlay');
  const searchInput = document.querySelector('#js-search-input');
  const searchClose = document.querySelector('.search__close');
  
  if (searchIcon && search) {
    searchIcon.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      search.classList.add('is-visible');
      document.body.classList.add('search-is-visible');
      if (searchInput) {
        setTimeout(() => searchInput.focus(), 100);
      }
    });
  }
  
  function closeSearch() {
    if (search) {
      search.classList.remove('is-visible');
      document.body.classList.remove('search-is-visible');
      if (searchInput) {
        searchInput.value = '';
        const resultsContainer = document.getElementById('js-results-container');
        if (resultsContainer) {
          resultsContainer.innerHTML = '';
        }
      }
    }
  }
  
  if (searchClose) {
    searchClose.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      closeSearch();
    });
  }
  
  if (searchOverlay) {
    searchOverlay.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      closeSearch();
    });
  }
  
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && search && search.classList.contains('is-visible')) {
      closeSearch();
    }
  });
  
  // Mobile Menu Toggle
  const hamburger = document.querySelector('.hamburger');
  const mainNav = document.querySelector('.main-nav');
  
  if (hamburger && mainNav) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('is-open');
      mainNav.classList.toggle('is-visible');
    });
  }
  
  // Dark Mode Toggle
  const toggleTheme = document.querySelector('.toggle-theme');
  if (toggleTheme) {
    toggleTheme.addEventListener('click', function() {
      const html = document.documentElement;
      const isDark = html.hasAttribute('dark');
      
      if (isDark) {
        html.removeAttribute('dark');
        html.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
      } else {
        html.setAttribute('dark', '');
        html.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
      }
    });
  }
  
  // Top Button
  const topButton = document.querySelector('.top');
  if (topButton) {
    topButton.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
  
  // Newsletter Form
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const email = this.querySelector('input[type="email"]').value;
      // 여기에 뉴스레터 구독 로직을 추가할 수 있습니다
      alert('Thank you for subscribing!');
      this.reset();
    });
  }
  
  // Smooth Scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });
  
  // Search Functionality
  let searchData = [];
  let searchIndex = null;
  
  // Get base URL - use relative path
  const searchJsonPath = '/search.json';
  
  // Load search data
  fetch(searchJsonPath)
    .then(response => {
      if (!response.ok) {
        throw new Error('Search data not found');
      }
      return response.json();
    })
    .then(data => {
      searchData = data;
      // Create search index (simple word-based index)
      searchIndex = searchData.map((item, index) => ({
        index: index,
        words: (item.title + ' ' + item.excerpt + ' ' + item.content + ' ' + (item.categories || []).join(' ') + ' ' + (item.tags || []).join(' ')).toLowerCase().split(/\s+/)
      }));
    })
    .catch(err => {
      console.error('Error loading search data:', err);
    });
  
  // Search function
  function performSearch(query) {
    if (!searchIndex || !query || query.trim().length === 0) {
      return [];
    }
    
    const queryWords = query.toLowerCase().trim().split(/\s+/);
    const results = [];
    
    searchIndex.forEach(item => {
      let score = 0;
      const post = searchData[item.index];
      
      queryWords.forEach(word => {
        // Title matches get highest score
        if (post.title.toLowerCase().includes(word)) {
          score += 10;
        }
        // Category/tag matches
        if (post.categories && post.categories.some(cat => cat.toLowerCase().includes(word))) {
          score += 5;
        }
        if (post.tags && post.tags.some(tag => tag.toLowerCase().includes(word))) {
          score += 5;
        }
        // Content matches
        item.words.forEach(postWord => {
          if (postWord.includes(word) || word.includes(postWord)) {
            score += 1;
          }
        });
      });
      
      if (score > 0) {
        results.push({ post, score });
      }
    });
    
    // Sort by score (highest first)
    results.sort((a, b) => b.score - a.score);
    
    return results.slice(0, 10); // Return top 10 results
  }
  
  // Display search results
  function displaySearchResults(results) {
    const resultsContainer = document.getElementById('js-results-container');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
      resultsContainer.innerHTML = '<div class="no-results">No results found.</div>';
      return;
    }
    
    resultsContainer.innerHTML = results.map(result => {
      const post = result.post;
      const imageHtml = post.image ? `
        <div class="search-results__image">
          <img src="${post.image}" alt="${post.title}">
        </div>
      ` : '';
      
      return `
        <div class="search-results__item">
          ${imageHtml}
          <a href="${post.url}" class="search-results__content">
            ${post.date ? `<span class="search-results__date">${post.date}</span>` : ''}
            <h4 class="search-results__title">${post.title}</h4>
          </a>
        </div>
      `;
    }).join('');
  }
  
  // Search input handler
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      
      if (query.length === 0) {
        document.getElementById('js-results-container').innerHTML = '';
        return;
      }
      
      // Debounce search
      searchTimeout = setTimeout(() => {
        const results = performSearch(query);
        displaySearchResults(results);
      }, 300);
    });
    
    // Handle Enter key
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = this.value.trim();
        if (query.length > 0) {
          const results = performSearch(query);
          if (results.length > 0) {
            window.location.href = results[0].post.url;
          }
        }
      }
    });
  }
  
  // Category Tabs Functionality
  const categoryTabs = document.querySelectorAll('.category-tabs__item');
  const categoryPosts = document.querySelectorAll('.category-posts');
  
  if (categoryTabs.length > 0) {
    categoryTabs.forEach(tab => {
      tab.addEventListener('click', function() {
        const category = this.getAttribute('data-category');
        
        // Remove active class from all tabs
        categoryTabs.forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        this.classList.add('active');
        
        // Hide all category posts
        categoryPosts.forEach(posts => {
          posts.classList.remove('active');
        });
        
        // Show selected category posts
        const selectedPosts = document.querySelector(`.category-posts[data-category="${category}"]`);
        if (selectedPosts) {
          selectedPosts.classList.add('active');
        }
      });
    });
  }
});

