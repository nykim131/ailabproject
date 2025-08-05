# 🎯 퀴즈 커뮤니티

다양한 퀴즈 앱의 소식과 정보를 제공하는 커뮤니티입니다! KB Pay, 카카오페이, 캐시워크 등 다양한 앱의 퀴즈 정보를 한눈에 확인할 수 있는 현대적인 웹 플랫폼입니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **퀴즈 소식 공유**: 다양한 앱의 최신 퀴즈 소식을 실시간으로 확인
- **퀴즈 정보 제공**: 정확한 퀴즈 정보와 포인트 정보 제공
- **커뮤니티 기반**: 사용자들이 정보를 공유하고 교환하는 플랫폼
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 기기에서 최적화

### 🎨 UI/UX 특징
- **현대적 디자인**: 그라데이션 배경과 글래스모피즘 효과
- **애니메이션**: 부드러운 전환 효과와 호버 애니메이션
- **인터랙티브 요소**: 모달, 스크롤 효과, 카운터 애니메이션
- **접근성**: 키보드 네비게이션과 스크린 리더 지원

### 📱 지원하는 퀴즈 앱
- **KB Pay 오늘의 퀴즈**: 매일 오전 10시 진행, 10P 적립
- **카카오페이 퀴즈타임**: 카카오페이 머니로 포인트 적립
- **캐시워크 돈버는퀴즈**: 현금 적립으로 100원 획득
- **KB스타뱅킹 스타퀴즈**: KB스타뱅킹 포인트 적립

## 🚀 설치 및 실행

### 필수 요구사항
- Python 3.7 이상
- pip (Python 패키지 관리자)

### 1. 저장소 클론
```bash
git clone <repository-url>
cd finalproject
```

### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행
```bash
python main.py
```

### 5. 브라우저에서 접속
```
http://localhost:5000
```

## 📁 프로젝트 구조

```
finalproject/
├── main.py                 # Flask 애플리케이션 메인 파일
├── quiz.json              # 퀴즈 데이터 파일
├── requirements.txt       # Python 의존성 목록
├── README.md             # 프로젝트 문서
├── templates/
│   └── index.html        # 메인 HTML 템플릿
└── static/
    ├── css/
    │   └── style.css     # 스타일시트
    └── js/
        └── script.js     # JavaScript 파일
```

## 🔧 API 엔드포인트

### 기본 엔드포인트
- `GET /` - 메인 페이지
- `GET /api/quiz` - 전체 퀴즈 데이터
- `GET /api/quiz/<id>` - 특정 퀴즈 상세 정보
- `GET /api/stats` - 퀴즈 통계 정보

### 검색 및 필터링
- `GET /api/search?q=<query>` - 퀴즈 검색
- `GET /api/filter?engine=<engine>` - 엔진별 필터링
- `GET /api/sort?order=<asc|desc>` - 점수별 정렬

### 시스템
- `GET /health` - 헬스 체크

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: `#ff6b35` (오렌지)
- **Secondary**: `#667eea` (파란색)
- **Accent**: `#ffd700` (골드)
- **Background**: `#f8f9fa` (연한 회색)
- **Text**: `#333` (진한 회색)

### 타이포그래피
- **Font Family**: Noto Sans KR
- **Weights**: 300, 400, 500, 700, 900
- **Responsive**: 모바일 최적화된 폰트 크기

### 컴포넌트
- **Cards**: 둥근 모서리, 그림자 효과
- **Buttons**: 그라데이션 배경, 호버 애니메이션
- **Modals**: 블러 배경, 스케일 애니메이션
- **Navigation**: 고정 헤더, 스크롤 효과

## 📊 데이터 구조

### quiz.json 예시
```json
{
  "query": "kb pay 오늘의 퀴즈",
  "number_of_results": 12,
  "results": [
    {
      "url": "https://example.com",
      "title": "KB Pay 오늘의 퀴즈 정답",
      "content": "퀴즈 내용...",
      "publishedDate": "2025-05-08",
      "engine": "google",
      "score": 2.5,
      "category": "general"
    }
  ]
}
```

## 🔍 주요 기능 설명

### 1. 히어로 섹션
- 매력적인 그라데이션 배경
- 퀴즈 소식 보기 및 정답 공유하기 버튼
- 애니메이션된 커뮤니티 아이콘

### 2. 퀴즈 소식 섹션
- 최신 퀴즈 소식 카드 그리드
- 각 앱별 정답과 포인트 정보
- 날짜 및 카테고리 메타 정보

### 3. 정답 공유 섹션
- KB Pay 퀴즈 정답 공유
- 통계 카드 (공유된 정답, 최신 업데이트, 평균 점수)
- 퀴즈 카드 그리드
- 상세보기 모달

### 4. 소개 섹션
- 커뮤니티 소개 및 특징
- 애니메이션된 사용자 아이콘

## 🛠️ 개발 가이드

### 새로운 기능 추가
1. HTML 템플릿에 마크업 추가
2. CSS 스타일 정의
3. JavaScript 인터랙션 구현
4. Flask 라우트 추가 (필요시)

### 스타일 수정
- `static/css/style.css` 파일에서 스타일 수정
- CSS 변수 사용으로 일관성 유지
- 반응형 디자인 고려

### JavaScript 기능 확장
- `static/js/script.js` 파일에서 기능 추가
- 모듈화된 함수 구조 유지
- 에러 핸들링 포함

## 📱 반응형 디자인

### 브레이크포인트
- **Mobile**: 480px 이하
- **Tablet**: 768px 이하
- **Desktop**: 768px 이상

### 최적화 사항
- 터치 친화적 버튼 크기
- 모바일 네비게이션 메뉴
- 적응형 그리드 레이아웃
- 최적화된 폰트 크기

## 🚀 배포

### 로컬 개발
```bash
export FLASK_ENV=development
python main.py
```

### 프로덕션 배포
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**퀴즈 커뮤니티** - 퀴즈 앱의 소식과 정보를 제공하는 커뮤니티입니다! 🎯✨ # ailabproject
