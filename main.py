from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import psycopg2
import openai
import subprocess
import sys

app = Flask(__name__)

def load_quiz_data_from_db():
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="nykim",
        password="1234",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT id, app_name, quiz_date, title, url, engines, content, published_date, answer, created_at, likes
        FROM quiz_results
        ORDER BY quiz_date DESC, created_at DESC
    """)
    rows = cur.fetchall()
    # 컬럼명 리스트
    columns = [desc[0] for desc in cur.description]
    # dict로 변환
    results = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return results

def get_best_answer_with_llm(app_name, answers, quiz_date):
    #openai.api_key = os.getenv('OPENAI_API_KEY')
    openai.api_key = "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"   
    
    # 정답 후보 필터링 - 의미없는 단어들 제거
    filtered_answers = []
    exclude_words = [
        'KB Pay', 'KB페이', '리브메이트', '비트버니', '오케이캐쉬백', '오퀴즈', 'OK캐쉬백',
        '문제', '퀴즈', '정답', '오늘의', '앱', '통합', '출제', '금요일', '자', '사진',
        quiz_date, app_name, '월', '일', '년', '2025', '2024', '2023'
    ]
    
    for answer in answers:
        if not answer or len(answer.strip()) < 2:  # 너무 짧은 답 제외
            continue
        
        # 제외할 단어가 포함된 경우 스킵
        if any(exclude_word in answer for exclude_word in exclude_words):
            continue
            
        # 너무 긴 문장 제외 (50자 이상)
        if len(answer) > 50:
            continue
            
        # 특수문자만 있는 경우 제외
        if answer.strip() in ['○○○○○', '...', '-', '=', '|']:
            continue
            
        filtered_answers.append(answer)
    
    # 필터링된 답이 없으면 원본에서 가장 짧은 답 사용
    if not filtered_answers:
        valid_answers = [a for a in answers if a and len(a.strip()) >= 2 and len(a) <= 20]
        if valid_answers:
            # 가장 짧은 답 선택
            filtered_answers = [min(valid_answers, key=len)]
        else:
            return "정답 수집 필요"
    
    # 디버깅: 필터링된 답 출력
    print(f"Debug - 원본 답변: {answers}")
    print(f"Debug - 필터링된 답변: {filtered_answers}")
    
    if not filtered_answers:
        return "정답 수집 필요"
    
    prompt = f"""아래는 '{app_name}' 퀴즈의 정답 후보 리스트입니다.
    
    강력한 정답 추출 규칙:
    1. 가장 짧고 핵심적인 답만 선택해줘 (긴 문장 절대 금지!)
    2. 단어 하나 또는 최대 2-3단어 조합만 허용
    3. "○○○○○" 빈칸이 있는 문장에서는 그 빈칸에 들어갈 단어만 찾아줘. ooooo를 포함한 문장은 노출 절대 금지!
    4. 브랜드명, 제품명, 인물명 등 고유명사 우선
    5. 설명문, 광고문구, 긴 문장은 절대 선택하지 마
    6. 특수문자(따옴표, 괄호 등)로 묶인 핵심 단어가 있으면 그것을 우선 추출
    7. 여러 후보 중 가장 간단하고 명확한 답 선택
    
    예시:
    - "올리브영 1등 질 유산균 ○○○○○!" → 제품명만 추출 (예: 락토핏)
    - "미국 연극·뮤지컬계의 가장 권위 있는 상" → 상 이름만 추출 (예: 토니상)

    정답 후보:
    {chr(10).join('- ' + a for a in filtered_answers)}
    
    최종 정답 (단어만):"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 퀴즈 정답 추출 전문가야. 반드시 가장 짧고 핵심적인 단어만 추출해야 해. 긴 문장, 설명문, 광고문구는 절대 정답이 아니야. 오직 핵심 단어(고유명사, 브랜드명, 제품명 등)만 추출해줘. 예: '락토핏', '토니상', '김치' 같은 단순한 답만 허용해."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20,
        temperature=0
    )
    return response.choices[0].message.content.strip()

def get_latest_quiz_per_app():
    """메인 페이지용: 각 앱별로 quiz_date가 가장 최신인 퀴즈 1개씩만 반환"""
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="nykim",
        password="1234",
        port=5432
    )
    cur = conn.cursor()
    
    # 각 앱별로 최신 quiz_date를 가져오고, 
    # 그 중에서 좋아요가 가장 높은 글을 선택
    # 좋아요가 모두 0이면 정답에 가까운 순(created_at 기준)으로 선택
    cur.execute("""
        WITH latest_dates AS (
            SELECT app_name, MAX(quiz_date) as max_date
            FROM quiz_results
            WHERE answer IS NOT NULL AND answer != ''
            GROUP BY app_name
        ),
        latest_quizzes AS (
            SELECT r.id, r.app_name, r.quiz_date, r.title, r.url, r.engines, 
                   r.content, r.published_date, r.answer, r.created_at, r.likes
            FROM quiz_results r
            INNER JOIN latest_dates l ON r.app_name = l.app_name AND r.quiz_date = l.max_date
            WHERE r.answer IS NOT NULL AND r.answer != ''
        ),
        ranked_quizzes AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY app_name 
                       ORDER BY 
                           CASE WHEN likes > 0 THEN likes ELSE 0 END DESC,
                           created_at DESC
                   ) as rn
            FROM latest_quizzes
        )
        SELECT id, app_name, quiz_date, title, url, engines, content, 
               published_date, answer, created_at, likes
        FROM ranked_quizzes
        WHERE rn = 1
        ORDER BY app_name
    """)
    
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in rows]
    
    cur.close()
    conn.close()
    return results

def get_best_quiz_per_app():
    """기존 함수 - 아카이브에서 사용하지 않음"""
    all_quiz = load_quiz_data_from_db()
    # app_name별로 answer 후보 모으기
    quiz_by_app = {}
    for quiz in all_quiz:
        app = quiz['app_name']
        if app not in quiz_by_app:
            quiz_by_app[app] = []
        quiz_by_app[app].append(quiz)
    # app_name별로 LLM으로 best answer 추출
    best_quiz_list = []
    for app, quiz_list in quiz_by_app.items():
        answers = [q['answer'] for q in quiz_list if q['answer']]
        if not answers:
            continue
        quiz_date = quiz_list[0].get('quiz_date', '')
        best_answer = get_best_answer_with_llm(app, answers, quiz_date)
        # best_answer와 일치하는 quiz를 하나만 선택
        for q in quiz_list:
            if q['answer'] == best_answer:
                best_quiz_list.append(q)
                break
        else:
            # 일치하는 게 없으면 첫 번째 quiz 사용
            best_quiz_list.append(quiz_list[0])
    return best_quiz_list

def get_quiz_by_app_name():
    """아카이브용: app_name별로 모든 퀴즈 데이터를 그룹화하여 반환"""
    all_quiz = load_quiz_data_from_db()
    quiz_by_app = {}
    
    for quiz in all_quiz:
        app = quiz['app_name']
        if app not in quiz_by_app:
            quiz_by_app[app] = []
        quiz_by_app[app].append(quiz)
    
    # 각 app별로 최신순 정렬 (quiz_date 기준)
    for app in quiz_by_app:
        quiz_by_app[app].sort(key=lambda x: (x.get('quiz_date', ''), x.get('created_at', '')), reverse=True)
    
    return quiz_by_app

def get_latest_update_date():
    """각 앱별 최신 업데이트 날짜를 가져오는 함수"""
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="nykim",
        password="1234",
        port=5432
    )
    cur = conn.cursor()
    
    # quiz_date 컬럼의 데이터 타입 확인
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'quiz_list' AND column_name = 'quiz_date'
    """)
    column_info = cur.fetchone()
    print(f"Debug - quiz_date column type: {column_info}")
    
    # quiz_list 테이블에서 각 앱별 최신 날짜 조회 (YYYY-MM-DD 형식으로)
    cur.execute("""
        SELECT app_name, MAX(quiz_date) as latest_date
        FROM quiz_list 
        GROUP BY app_name
        ORDER BY app_name
    """)
    
    latest_dates = {}
    for row in cur.fetchall():
        # 원본 값을 그대로 사용
        latest_dates[row[0]] = row[1]
    
    # 전체 최신 날짜 조회 (YYYY-MM-DD 형식으로)
    cur.execute("""
        SELECT MAX(quiz_date) as overall_latest
        FROM quiz_list
    """)
    
    overall_latest_row = cur.fetchone()
    overall_latest = overall_latest_row[0] if overall_latest_row else None
    
    # 디버깅: 전체 최신 날짜 출력
    print(f"Debug - overall_latest: {overall_latest}, type: {type(overall_latest)}")
    
    cur.close()
    conn.close()
    return latest_dates, overall_latest

@app.route('/')
def index():
    """메인 페이지 - 돈버는 퀴즈 앱"""
    # 오늘의 정답: 최신 퀴즈만
    today_quiz_data = get_latest_quiz_per_app()
    # 아카이브: 모든 퀴즈 데이터
    archive_quiz_data = load_quiz_data_from_db()
    # 최신 업데이트 날짜 가져오기
    latest_dates, overall_latest = get_latest_update_date()
    
    return render_template('index.html', 
                         quiz_data=today_quiz_data,
                         archive_data=archive_quiz_data,
                         latest_update_date=overall_latest)

@app.route('/archive')
def archive():
    """퀴즈 아카이브 페이지 - app_name별 탭 (모든 퀴즈)"""
    quiz_by_app = get_quiz_by_app_name()
    return render_template('archive.html', quiz_by_app=quiz_by_app)

@app.route('/api/quiz')
def api_quiz():
    """퀴즈 데이터 API 엔드포인트"""
    quiz_data = load_quiz_data_from_db()
    return jsonify({"results": quiz_data})

@app.route('/api/quiz/<int:quiz_id>')
def api_quiz_detail(quiz_id):
    """특정 퀴즈 상세 정보 API"""
    quiz_data = load_quiz_data_from_db()
    if 0 <= quiz_id < len(quiz_data):
        return jsonify(quiz_data[quiz_id])
    return jsonify({"error": "퀴즈를 찾을 수 없습니다."}), 404

@app.route('/api/stats')
def api_stats():
    """퀴즈 통계 API"""
    quiz_data = load_quiz_data_from_db()
    results = quiz_data
    
    if not results:
        return jsonify({
            "total_quizzes": 0,
            "average_score": 0,
            "latest_update": None,
            "engines": []
        })
    
    # 통계 계산
    total_quizzes = len(results)
    average_score = sum(result.get('score', 0) for result in results) / total_quizzes
    
    # 최신 업데이트 날짜
    latest_update = None
    for result in results:
        if result.get('publishedDate'):
            try:
                date = datetime.strptime(result['publishedDate'], '%Y-%m-%d')
                if latest_update is None or date > latest_update:
                    latest_update = date
            except ValueError:
                continue
    
    # 사용된 엔진들
    engines = list(set(result.get('engine', '') for result in results if result.get('engine')))
    
    return jsonify({
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "latest_update": latest_update.strftime('%Y-%m-%d') if latest_update else None,
        "engines": engines
    })

@app.route('/api/search')
def api_search():
    """퀴즈 검색 API"""
    query = request.args.get('q', '').lower()
    quiz_data = load_quiz_data_from_db()
    results = quiz_data
    
    if not query:
        return jsonify(results)
    
    # 검색 필터링
    filtered_results = []
    for result in results:
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        
        if query in title or query in content:
            filtered_results.append(result)
    
    return jsonify(filtered_results)

@app.route('/api/filter')
def api_filter():
    """퀴즈 필터링 API"""
    engine = request.args.get('engine', 'all')
    quiz_data = load_quiz_data_from_db()
    results = quiz_data
    
    if engine == 'all':
        return jsonify(results)
    
    # 엔진별 필터링
    filtered_results = [result for result in results if result.get('engine') == engine]
    return jsonify(filtered_results)

@app.route('/api/sort')
def api_sort():
    """퀴즈 정렬 API"""
    order = request.args.get('order', 'desc')  # desc 또는 asc
    quiz_data = load_quiz_data_from_db()
    results = quiz_data
    
    # 점수별 정렬
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=(order == 'desc'))
    return jsonify(sorted_results)

@app.route('/api/today-quiz')
def api_today_quiz():
    """오늘의 퀴즈 데이터 조회 API"""
    try:
        quiz_data = get_latest_quiz_per_app()
        return jsonify({
            'success': True,
            'data': quiz_data
        })
    except Exception as e:
        print(f"Error in api_today_quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/admin')
def admin():
    """관리자 페이지"""
    return render_template('admin.html')

@app.route('/admin/search', methods=['POST'])
def admin_search():
    """관리자 페이지에서 퀴즈 검색 실행"""
    try:
        data = request.get_json()
        search_type = data.get('type')  # 'today' 또는 'date'
        target_date = data.get('date')  # 날짜 (YYYY-MM-DD 형식)
        
        # DB 연결
        conn = psycopg2.connect(
            host="localhost",
            dbname="mydb",
            user="nykim",
            password="1234",
            port=5432
        )
        cur = conn.cursor()
        
        if search_type == 'today':
            # 오늘 날짜로 quiz_list 업데이트
            today = datetime.now().strftime('%Y-%m-%d')
            cur.execute("""
                UPDATE quiz_list 
                SET quiz_date = %s
            """, (today,))
        elif search_type == 'date' and target_date:
            # 지정된 날짜로 quiz_list 업데이트
            cur.execute("""
                UPDATE quiz_list 
                SET quiz_date = %s
            """, (target_date,))
        else:
            return jsonify({'success': False, 'message': '잘못된 요청입니다.'})
        
        conn.commit()
        cur.close()
        conn.close()
        
        # quiz_searcher.py 실행
        result = subprocess.run([sys.executable, 'quiz_searcher.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': '퀴즈 검색이 완료되었습니다.',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False, 
                'message': '퀴즈 검색 중 오류가 발생했습니다.',
                'error': result.stderr
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@app.route('/admin/quiz-list')
def admin_quiz_list():
    """quiz_list 테이블 조회"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="mydb",
            user="nykim",
            password="1234",
            port=5432
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT app_name, quiz_date 
            FROM quiz_list 
            ORDER BY app_name, quiz_date
        """)
        
        rows = cur.fetchall()
        quiz_list = [{'app_name': row[0], 'quiz_date': row[1]} for row in rows]
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'data': quiz_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@app.route('/api/like/<int:quiz_id>', methods=['POST'])
def add_like(quiz_id):
    """좋아요 추가 API (중복 방지 없음)"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="mydb",
            user="nykim",
            password="1234",
            port=5432
        )
        cur = conn.cursor()
        
        # 좋아요 수 증가
        cur.execute("""
            UPDATE quiz_results 
            SET likes = likes + 1
            WHERE id = %s
        """, (quiz_id,))
        
        # 현재 좋아요 수 조회
        cur.execute("SELECT likes FROM quiz_results WHERE id = %s", (quiz_id,))
        result = cur.fetchone()
        likes_count = result[0] if result else 0
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'likes_count': likes_count
        })
        
    except Exception as e:
        print(f"Error in add_like: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/likes/<int:quiz_id>')
def get_likes(quiz_id):
    """특정 퀴즈의 좋아요 수 조회"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="mydb",
            user="nykim",
            password="1234",
            port=5432
        )
        cur = conn.cursor()
        
        # 좋아요 수 조회
        cur.execute("SELECT likes FROM quiz_results WHERE id = %s", (quiz_id,))
        result = cur.fetchone()
        likes_count = result[0] if result else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'likes_count': likes_count
        })
        
    except Exception as e:
        print(f"Error in get_likes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 개발 환경에서 디버그 모드 활성화
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 돈버는 퀴즈 앱이 시작됩니다...")
    print("📍 접속 주소: http://localhost:5000")
    print("📊 API 문서: http://localhost:5000/api/quiz")
    print("💡 개발 모드:", debug_mode)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        threaded=True
    ) 