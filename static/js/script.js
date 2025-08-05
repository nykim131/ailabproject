// 퀴즈 커뮤니티 JavaScript

// 전역 변수
let quizData = null;

// 따봉 버튼 클릭 함수
window.addLike = async function(quizId, button) {
    try {
        // 버튼 비활성화 (중복 클릭 방지)
        button.disabled = true;
        
        const response = await fetch(`/api/like/${quizId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 따봉 수 업데이트
            const likeCountSpan = button.querySelector('.like-count');
            likeCountSpan.textContent = data.likes_count;
            
            // 애니메이션 효과
            button.classList.add('liked');
            setTimeout(() => {
                button.classList.remove('liked');
            }, 600);
            
            // 오늘의 퀴즈 섹션 실시간 업데이트
            await updateTodayQuizSection();
            
            showToast('따봉!');
        } else {
            showToast('오류가 발생했습니다. 다시 시도해주세요.', 'error');
        }
    } catch (error) {
        console.error('따봉 추가 오류:', error);
        showToast('네트워크 오류가 발생했습니다.', 'error');
    } finally {
        // 버튼 활성화 (1초 후)
        setTimeout(() => {
            button.disabled = false;
        }, 1000);
    }
};

// DOM이 로드되면 실행
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeLikeButtons();
});

// 앱 초기화
function initializeApp() {
    setupNavigation();
    setupScrollEffects();
    setupModal();
    setupAnimations();
    setupTabs();
    loadQuizData();
}

// 좋아요 버튼 이벤트 바인딩
function initializeLikeButtons() {
    // 이벤트 델리게이션 사용 - document에 이벤트 리스너 추가
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-like')) {
            const button = e.target.closest('.btn-like');
            const quizId = button.dataset.quizId;
            if (quizId && !button.disabled) {
                handleLikeClick(quizId, button);
            }
        }
    });
}

// 좋아요 버튼 클릭 함수
async function handleLikeClick(quizId, button) {
    try {
        // 버튼 비활성화 (중복 클릭 방지)
        button.disabled = true;
        
        const response = await fetch(`/api/like/${quizId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 좋아요 수 업데이트
            const likeCountSpan = button.querySelector('.like-count');
            likeCountSpan.textContent = data.likes_count;
            
            // 애니메이션 효과
            button.classList.add('liked');
            setTimeout(() => {
                button.classList.remove('liked');
            }, 600);
            
            // 오늘의 퀴즈 섹션 실시간 업데이트
            await updateTodayQuizSection();
            
            showToast('좋아요!');
        } else {
            showToast('오류가 발생했습니다. 다시 시도해주세요.', 'error');
        }
    } catch (error) {
        console.error('좋아요 추가 오류:', error);
        showToast('네트워크 오류가 발생했습니다.', 'error');
    } finally {
        // 버튼 활성화 (1초 후)
        setTimeout(() => {
            button.disabled = false;
        }, 1000);
    }
}

// 오늘의 퀴즈 섹션 업데이트 함수
async function updateTodayQuizSection() {
    try {
        const response = await fetch('/api/today-quiz');
        const data = await response.json();
        
        if (data.success) {
            const todayQuizGrid = document.querySelector('#quiz .quiz-grid');
            if (todayQuizGrid) {
                // 기존 내용 제거
                todayQuizGrid.innerHTML = '';
                
                // 새로운 퀴즈 카드들 생성
                data.data.forEach(quiz => {
                    const quizCard = createTodayQuizCard(quiz);
                    todayQuizGrid.appendChild(quizCard);
                });
            }
        }
    } catch (error) {
        console.error('오늘의 퀴즈 섹션 업데이트 오류:', error);
    }
}

// 오늘의 퀴즈 카드 생성 함수
function createTodayQuizCard(quiz) {
    const appStyles = {
        'KB Pay': {color: '#FFE066', logo: '/static/image/kbpay.webp', class: 'kb'},
        '비트버니': {color: '#DDA0DD', logo: '/static/image/bitbunny.webp', class: 'bitbunny'},
        '오퀴즈': {color: '#FFB6C1', logo: '/static/image/oquiz.webp', class: 'oquiz'}
    };
    
    const style = appStyles[quiz.app_name] || {color: '#f8f9fa', logo: '/static/image/default.webp', class: 'default'};
    
    const card = document.createElement('div');
    card.className = 'news-card';
    card.innerHTML = `
        <div class="card-header">
            <div class="app-info">
                <img src="${style.logo}" alt="${quiz.app_name}" class="app-logo">
                <div class="app-details">
                    <h3 class="app-name">${quiz.app_name}</h3>
                    <span class="quiz-date">${quiz.published_date || quiz.quiz_date}</span>
                </div>
            </div>
            <div class="app-badge ${style.class}">${quiz.app_name}</div>
        </div>
        
        <div class="card-body">
            <h4 class="quiz-title">${quiz.title}</h4>
            <p class="quiz-description">
                ${quiz.content ? (quiz.content.length > 100 ? quiz.content.substring(0, 100) + '...' : quiz.content) : ''}
            </p>
            
            <div class="answer-section">
                <div class="answer-label">정답</div>
                <div class="answer-value">${quiz.answer}</div>
                <button class="copy-btn" onclick="copyToClipboard('${quiz.answer}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        </div>
        
        <div class="card-footer">
            <button class="btn btn-outline btn-sm" onclick="window.open('${quiz.url}', '_blank')">
                <i class="fas fa-link"></i>
                원문 보기
            </button>
            <button class="btn btn-ghost btn-sm" onclick="shareQuiz('${quiz.title}', '${quiz.url}')">
                <i class="fas fa-share"></i>
                공유하기
            </button>
            <div class="like-display">
                <i class="fas fa-thumbs-up"></i>
                <span class="like-count">${quiz.likes || 0}</span>
            </div>
        </div>
    `;
    
    return card;
}

// 네비게이션 설정
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // 네비게이션 링크 클릭 이벤트
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
            
            // 활성 링크 업데이트
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // 모바일 메뉴 토글
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // 스크롤 시 헤더 스타일 변경
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// 스크롤 효과 설정
function setupScrollEffects() {
    // 스무스 스크롤
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // 애니메이션 대상 요소들
    const animateElements = document.querySelectorAll('.news-card, .quiz-card, .stat-card');
    animateElements.forEach(el => observer.observe(el));
}

// 모달 설정
function setupModal() {
    const modal = document.getElementById('quizModal');
    const closeBtn = modal.querySelector('.close');

    // 모달 닫기
    closeBtn.addEventListener('click', function() {
        closeModal();
    });

    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
}

// 모달 닫기 함수
function closeModal() {
    const modal = document.getElementById('quizModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // 모달 애니메이션 리셋
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.transform = 'scale(0.8)';
    modalContent.style.opacity = '0';
}

// 애니메이션 설정
function setupAnimations() {
    // 숫자 카운터 애니메이션
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
        const target = parseFloat(counter.textContent);
        if (!isNaN(target)) {
            animateCounter(counter, 0, target, 2000);
        }
    });

    // 호버 효과
    const cards = document.querySelectorAll('.news-card, .quiz-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// 퀴즈 데이터 로드
function loadQuizData() {
    // 실제 구현에서는 API 호출을 통해 데이터를 가져옵니다
    // 여기서는 이미 HTML에 포함된 데이터를 사용합니다
    console.log('퀴즈 데이터 로드 완료');
}

// 섹션으로 스크롤
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = section.offsetTop - headerHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

// 퀴즈 상세보기
function viewQuizDetail(index) {
    const quizCards = document.querySelectorAll('.quiz-card');
    const quizCard = quizCards[index];
    
    if (quizCard) {
        const title = quizCard.querySelector('.quiz-title a').textContent;
        const description = quizCard.querySelector('.quiz-description').textContent;
        const score = quizCard.querySelector('.score').textContent;
        const engine = quizCard.querySelector('.engine').textContent;
        const url = quizCard.querySelector('.quiz-title a').href;
        
        const modalContent = `
            <div class="quiz-detail">
                <div class="detail-header">
                    <div class="detail-score">
                        <span class="score-badge">${score}</span>
                        <span class="engine-badge">${engine}</span>
                    </div>
                </div>
                
                <div class="detail-content">
                    <h3 class="detail-title">${title}</h3>
                    <p class="detail-description">${description}</p>
                    
                    <div class="detail-meta">
                        <div class="meta-item">
                            <i class="fas fa-link"></i>
                            <a href="${url}" target="_blank">원본 링크</a>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-calendar"></i>
                            <span>${new Date().toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="window.open('${url}', '_blank')">
                        <i class="fas fa-external-link-alt"></i>
                        원본 보기
                    </button>
                    <button class="btn btn-secondary" onclick="closeModal()">
                        <i class="fas fa-times"></i>
                        닫기
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('quizDetailContent').innerHTML = modalContent;
        openModal();
    }
}

// 모달 열기
function openModal() {
    const modal = document.getElementById('quizModal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // 모달 애니메이션
    setTimeout(() => {
        const modalContent = modal.querySelector('.modal-content');
        modalContent.style.transform = 'scale(1)';
        modalContent.style.opacity = '1';
    }, 10);
}

// 숫자 카운터 애니메이션
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * easeOutQuart(progress);
        element.textContent = current.toFixed(1);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// 이징 함수
function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// 퀴즈 검색 기능
function searchQuiz(query) {
    const quizCards = document.querySelectorAll('.quiz-card');
    const searchTerm = query.toLowerCase();
    
    quizCards.forEach(card => {
        const title = card.querySelector('.quiz-title a').textContent.toLowerCase();
        const description = card.querySelector('.quiz-description').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || description.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.5s ease';
        } else {
            card.style.display = 'none';
        }
    });
}

// 퀴즈 필터링
function filterQuizByEngine(engine) {
    const quizCards = document.querySelectorAll('.quiz-card');
    
    quizCards.forEach(card => {
        const cardEngine = card.querySelector('.engine').textContent;
        
        if (engine === 'all' || cardEngine === engine) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.5s ease';
        } else {
            card.style.display = 'none';
        }
    });
}

// 퀴즈 정렬
function sortQuizByScore(order) {
    const quizGrid = document.querySelector('.quiz-grid');
    const quizCards = Array.from(quizGrid.querySelectorAll('.quiz-card'));
    
    quizCards.sort((a, b) => {
        const scoreA = parseFloat(a.querySelector('.score').textContent);
        const scoreB = parseFloat(b.querySelector('.score').textContent);
        
        return order === 'asc' ? scoreA - scoreB : scoreB - scoreA;
    });
    
    quizCards.forEach(card => {
        quizGrid.appendChild(card);
    });
}

// 토스트 메시지 표시
function showToast(message, type = 'info') {
    // 기존 토스트 제거
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 새 토스트 생성
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // 스타일 적용
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#ff4757' : '#228B22'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    // 따봉 이모지 추가
    if (type !== 'error' && message === '따봉!') {
        toast.innerHTML = `<i class="fas fa-thumbs-up"></i> ${message}`;
    }
    
    document.body.appendChild(toast);
    
    // 애니메이션 시작
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // 자동 제거
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); }
        to { transform: translateX(100%); }
    }
    
    .animate-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .header.scrolled {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    }
    
    .nav-menu.active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        padding: 1rem;
    }
    
    .nav-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }
    
    .nav-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .nav-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }
    
    .modal-content {
        transform: scale(0.8);
        opacity: 0;
        transition: all 0.3s ease;
    }
    
    .quiz-detail {
        padding: 1rem 0;
    }
    
    .detail-header {
        margin-bottom: 1.5rem;
    }
    
    .detail-score {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .score-badge, .engine-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .score-badge {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        color: white;
    }
    
    .engine-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .detail-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #333;
        line-height: 1.4;
    }
    
    .detail-description {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .detail-meta {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .detail-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
    
    .toast {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
`;
document.head.appendChild(style);

// 탭 설정
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const quizCards = document.querySelectorAll('.quiz-card');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const selectedTab = this.getAttribute('data-tab');
            
            // 활성 탭 버튼 변경
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 퀴즈 카드 필터링
            filterQuizCards(selectedTab);
            
            // 통계 업데이트
            updateStats(selectedTab);
        });
    });
}

// 퀴즈 카드 필터링
function filterQuizCards(selectedTab) {
    const quizCards = document.querySelectorAll('.quiz-card');
    
    quizCards.forEach(card => {
        const cardApp = card.getAttribute('data-app');
        
        if (selectedTab === 'all' || cardApp === selectedTab) {
            card.classList.remove('hidden');
            card.classList.add('visible');
        } else {
            card.classList.add('hidden');
            card.classList.remove('visible');
        }
    });
}

// 통계 업데이트
function updateStats(selectedTab) {
    const visibleCards = document.querySelectorAll(`.quiz-card[data-app="${selectedTab}"]`);
    const allCards = document.querySelectorAll('.quiz-card');
    
    const cardsToCount = selectedTab === 'all' ? allCards : visibleCards;
    const visibleCardsArray = Array.from(cardsToCount).filter(card => !card.classList.contains('hidden'));
    
    // 퀴즈 정보 수 업데이트
    const quizInfoStat = document.querySelector('.stat-card .stat-number');
    if (quizInfoStat) {
        quizInfoStat.textContent = visibleCardsArray.length;
    }
    
    // 평균 점수 업데이트
    const avgScoreStat = document.querySelectorAll('.stat-card .stat-number')[2];
    if (avgScoreStat && visibleCardsArray.length > 0) {
        const scores = visibleCardsArray.map(card => {
            const scoreElement = card.querySelector('.score');
            return scoreElement ? parseFloat(scoreElement.textContent) : 0;
        });
        const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        avgScoreStat.textContent = avgScore.toFixed(2);
    }
} 